# requests_api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from .models import JobRequest, JobOffer, Rating
from .serializers import JobRequestSerializer, JobOfferSerializer, RatingSerializer
from workers.models import SkillCategory
from skilllink.permissions import IsAdmin, IsResident, IsWorker


class RequestListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdmin()]
        return [IsResident()]

    def get(self, request):
        requests = JobRequest.objects.select_related(
            'resident', 'category'
        ).all().order_by('-created_at')
        return Response(JobRequestSerializer(requests, many=True).data)

    def post(self, request):
        # Auto-attach the logged-in resident's profile
        try:
            resident_profile = request.user.resident_profile
        except Exception:
            return Response(
                {'error': 'Resident profile not found. Please contact the admin.'},
                status=400
            )

        data = request.data.copy()
        data['resident'] = str(resident_profile.id)

        ser = JobRequestSerializer(data=data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)

        # Print errors to Django terminal so we can see exactly what's missing
        print("JobRequest validation errors:", ser.errors)
        return Response(ser.errors, status=400)

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
