# requests_api/views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
 
from .models import JobRequest, JobOffer, Rating, JobType
from .serializers import JobRequestSerializer, JobOfferSerializer, RatingSerializer, JobTypeSerializer
from workers.models import SkillCategory, WorkerProfile
from workers.serializers import WorkerProfileSerializer
from skilllink.permissions import IsAdmin, IsResident, IsWorker
from .ml_client import get_matched_workers, MLServiceUnavailable

logger = logging.getLogger(__name__)

class JobTypeListView(APIView):
    """
    GET /api/job-types/?category_id=<uuid>
 
    Returns active job type tiles for the given skill category.
    The resident UI renders these as a fixed selection grid.
    No free-text job type input is accepted.
    """
    permission_classes = [IsResident]
 
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'detail': 'category_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job_types = JobType.objects.filter(
            category_id=category_id,
            is_active=True,
        )
        return Response(JobTypeSerializer(job_types, many=True).data)


class RequestListCreateView(APIView):
 
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdmin()]
        return [IsResident()]
 
    # GET: unchanged
    def get(self, request):
        requests = JobRequest.objects.select_related(
            'resident', 'category'
        ).all().order_by('-created_at')
        return Response(JobRequestSerializer(requests, many=True).data)
 
    # POST: refactored to include ML matching
    def post(self, request):
 
        # Step 1 — Auto-attach the logged-in resident's profile
        try:
            resident_profile = request.user.resident_profile
        except Exception:
            return Response(
                {'error': 'Resident profile not found. Please contact the admin.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        data = request.data.copy()
        data['resident'] = str(resident_profile.id)
 
        ser = JobRequestSerializer(data=data)
        if not ser.is_valid():
            print("JobRequest validation errors:", ser.errors)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
 
        job_request = ser.save()
 
        # Step 2 — Validate job_type belongs to the declared category (if provided)
        if job_request.job_type_id:
            try:
                JobType.objects.get(
                    id=job_request.job_type_id,
                    category=job_request.category,
                    is_active=True,
                )
            except JobType.DoesNotExist:
                job_request.delete()
                return Response(
                    {'detail': 'The selected job type does not belong to the declared skill category.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
 
        # Step 3 — Pre-filter verified candidates
        # Hard constraints: verified status + matching skill category + not suspended.
        candidates = WorkerProfile.objects.filter(
            skill_category=job_request.category,
            verification_status='verified',
            is_suspended=False,
        ).select_related('user', 'skill_category')
 
        if not candidates.exists():
            logger.info(
                "Job request %s — no verified candidates in category '%s'.",
                job_request.id,
                job_request.category,
            )
            return Response(
                {
                    'job_request':     JobRequestSerializer(job_request).data,
                    'matched_workers': [],
                    'message':         'No verified workers are currently available in this category.',
                },
                status=status.HTTP_200_OK,
            )
 
        # Step 4 — Call the ML service
        # On failure the job_request is preserved in pending_match for retry.
        try:
            ranked = get_matched_workers(job_request, candidates)
        except MLServiceUnavailable as exc:
            logger.error(
                "ML service unavailable for job request %s: %s",
                job_request.id, exc,
            )
            return Response(
                {
                    'detail': (
                        'Our matching service is currently unavailable. '
                        'Your request has been saved and will be processed shortly.'
                    ),
                    'job_request_id': str(job_request.id),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
 
        # Step 5 — Fetch full worker profiles in ML-ranked order
        ranked_ids    = [r['worker_id'] for r in ranked]
        score_map     = {r['worker_id']: r['score']           for r in ranked}
        breakdown_map = {r['worker_id']: r['score_breakdown'] for r in ranked}
 
        profile_map = {
            str(w.id): w
            for w in WorkerProfile.objects.filter(
                id__in=ranked_ids
            ).select_related('skill_category', 'user')
        }
 
        matched_workers = []
        for worker_id in ranked_ids:
            worker = profile_map.get(worker_id)
            if worker:
                matched_workers.append({
                    'worker':          WorkerProfileSerializer(worker).data,
                    'score':           score_map[worker_id],
                    'score_breakdown': breakdown_map[worker_id],
                })
 
        # Step 6 — Return job request + ranked worker list
        return Response(
            {
                'job_request':     JobRequestSerializer(job_request).data,
                'matched_workers': matched_workers,
            },
            status=status.HTTP_201_CREATED,
        )
    

class RequestStatusView(APIView):
    permission_classes = [IsAdmin]
    def patch(self, request, pk):
        try:
            job = JobRequest.objects.get(pk=pk)
        except JobRequest.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        job.status = request.data.get('status', job.status)
        job.save()
        return Response(JobRequestSerializer(job).data)


class ResidentRequestsView(APIView):
    permission_classes = [IsResident] 
    """Requests for the currently logged-in resident."""
    def get(self, request):
        try:
            profile = request.user.resident_profile
        except Exception:
            return Response([])
        requests = JobRequest.objects.filter(resident=profile).select_related('category').order_by('-created_at')
        return Response(JobRequestSerializer(requests, many=True).data)
    
class SendOfferView(APIView):
    permission_classes = [IsResident]

    def post(self, request, request_id, worker_id):
        from workers.models import WorkerProfile
        from notifications_app.models import Notification

        # Verify the job request belongs to this resident
        try:
            job_request = JobRequest.objects.get(
                pk=request_id,
                resident=request.user.resident_profile
            )
        except JobRequest.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=404)

        # Verify the worker exists and is verified
        try:
            worker = WorkerProfile.objects.get(
                pk=worker_id,
                verification_status='verified',
                is_suspended=False
            )
        except WorkerProfile.DoesNotExist:
            return Response(
                {'error': 'Worker not found or not verified.'},
                status=404
            )

        # Block duplicate active offers for the same request
        existing = JobOffer.objects.filter(
            request=job_request,
            status='pending_response'
        ).first()
        if existing:
            return Response(
                {'error': 'An active offer already exists for this request.'},
                status=400
            )

        # Create the offer record
        offer = JobOffer.objects.create(
            request=job_request,
            worker=worker,
            status='pending_response',
        )

        # Move request to offer_sent status
        job_request.status = 'offer_sent'
        job_request.save()

        # Notify the worker
        Notification.objects.create(
            user=worker.user,
            type='offer',
            title='New Job Offer!',
            message=f'You received a job offer for: {job_request.title}',
        )

        return Response(JobOfferSerializer(offer).data, status=201)


class JobHistoryView(APIView):
    permission_classes = [IsWorker]
    """Job history for the logged-in worker."""
    def get(self, request):
        try:
            profile = request.user.worker_profile
        except Exception:
            return Response([])
        offers = JobOffer.objects.filter(
            worker=profile, request__status='completed'
        ).select_related('request__category', 'request__resident').order_by('-created_at')
        return Response(JobOfferSerializer(offers, many=True).data)


class RatingCreateView(APIView):
    permission_classes = [IsResident]
    def post(self, request):
        data = request.data.copy()
        data['rater'] = str(request.user.id)
        ser = RatingSerializer(data=data)
        if ser.is_valid():
            rating = ser.save()
            # Update worker avg_rating atomically
            from workers.models import WorkerProfile
            try:
                rated_worker = WorkerProfile.objects.get(user=rating.rated_user)
                new_avg = Rating.objects.filter(rated_user=rating.rated_user).aggregate(a=Avg('score'))['a'] or 0
                rated_worker.avg_rating = round(new_avg, 2)
                rated_worker.save(update_fields=['avg_rating'])
            except WorkerProfile.DoesNotExist:
                pass
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


# ADMIN ANALYTICS 

class StatsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        from workers.models import WorkerProfile
        from residents.models import ResidentProfile
        return Response({
            'total_workers': WorkerProfile.objects.count(),
            'verified_workers': WorkerProfile.objects.filter(verification_status='verified').count(),
            'total_residents': ResidentProfile.objects.count(),
            'total_requests': JobRequest.objects.count(),
            'completed_requests': JobRequest.objects.filter(status='completed').count(),
            'pending_requests': JobRequest.objects.filter(status='pending_match').count(),
        })


class WeeklyStatsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            requests = JobRequest.objects.filter(created_at__date=day).count()
            completed = JobRequest.objects.filter(updated_at__date=day, status='completed').count()
            data.append({
                'day': day.strftime('%a'),
                'requests': requests,
                'completed': completed,
            })
        return Response(data)


class SkillBreakdownView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        from workers.models import WorkerProfile
        cats = SkillCategory.objects.filter(is_active=True)
        data = []
        for cat in cats:
            data.append({
                'skill': cat.category_name,
                'count': WorkerProfile.objects.filter(skill_category=cat, verification_status='verified').count(),
            })
        return Response(data)


class MatchLogsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        offers = JobOffer.objects.select_related(
            'request__category', 'worker'
        ).order_by('-created_at')[:20]
        logs = []
        for o in offers:
            logs.append({
                'id': str(o.id),
                'request_title': o.request.title,
                'worker_name': o.worker.full_name,
                'category': o.request.category.category_name if o.request.category else '-',
                'match_score': float(o.match_score) if o.match_score else None,
                'status': o.status,
                'created_at': o.created_at.isoformat(),
            })
        return Response(logs)


class ActivityFeedView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        # Mix recent requests + offers as activity
        from notifications_app.models import Notification
        notifs = Notification.objects.order_by('-created_at')[:15]
        return Response([{
            'id': str(n.id),
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'created_at': n.created_at.isoformat(),
        } for n in notifs])
