# workers/views.py
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import WorkerProfile, SkillCategory
from .serializers import WorkerProfileSerializer, WorkerCreateSerializer, SkillCategorySerializer
from requests_api.models import JobOffer, JobRequest
from requests_api.serializers import JobOfferSerializer
from skilllink.permissions import IsAdmin, IsWorker
from rest_framework.permissions import IsAuthenticated


class WorkerListCreateView(APIView):
    """
    GET  /api/workers/   → Admin: list all workers
    POST /api/workers/   → Admin: register a walk-in worker (FR-WRK-06)
    """
    permission_classes = [IsAuthenticated, IsAdmin]
 
    def get(self, request):
        workers = WorkerProfile.objects.select_related('skill_category', 'user').all()
        return Response(WorkerProfileSerializer(workers, many=True).data)
 
    def post(self, request):
        ser = WorkerCreateSerializer(data=request.data)
        if ser.is_valid():
            worker = ser.save()
            return Response(WorkerProfileSerializer(worker).data, status=201)
        return Response(ser.errors, status=400)


class WorkerVerifyView(APIView):
    permission_classes = [IsAdmin]
    def patch(self, request, pk):
        try:
            worker = WorkerProfile.objects.get(pk=pk)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        is_verified = request.data.get('is_verified', True)
        worker.verification_status = 'verified' if is_verified else 'pending'
        if is_verified:
            worker.verified_at = timezone.now()
        worker.save()
        return Response(WorkerProfileSerializer(worker).data)


class WorkerSuspendView(APIView):
    permission_classes = [IsAdmin]
    def patch(self, request, pk):
        try:
            worker = WorkerProfile.objects.get(pk=pk)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        worker.is_suspended = request.data.get('is_suspended', True)
        worker.save()
        return Response(WorkerProfileSerializer(worker).data)


class WorkerProfileView(APIView):
    permission_classes = [IsWorker]
    def get(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found'}, status=404)
        return Response(WorkerProfileSerializer(profile).data)

    def put(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker profile not found'}, status=404)

        data = request.data.copy()

        if 'daily_rate' in data:
            data['declared_rate'] = data.pop('daily_rate')
        if 'experience_years' in data:
            data['years_experience'] = data.pop('experience_years')
        if 'phone' in data:
            data['contact_number'] = data.pop('phone')

        FRONTEND_ONLY = [
            'service', 'skills', 'location', 'rating',
            'hourly_rate', 'email', 'is_verified', 'skill_category_name',
            'avg_rating', 'verification_status', 'verified_at',
            'created_at', 'user_id',
        ]
        for field in FRONTEND_ONLY:
            data.pop(field, None)

        ser = WorkerProfileSerializer(profile, data=data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(WorkerProfileSerializer(profile).data)
        return Response(ser.errors, status=400)


class WorkerAvailabilityView(APIView):
    permission_classes = [IsWorker]
    def patch(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        days = request.data.get('availability_schedule', [])

        # Accept both short names (Mon) and full names (Monday) — normalize to full
        SHORT_TO_FULL = {
            'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
            'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'
        }
        normalized = [SHORT_TO_FULL.get(d, d) for d in days]

        profile.availability_schedule = normalized
        profile.save(update_fields=['availability_schedule'])
        return Response({'availability_schedule': profile.availability_schedule})


class WorkerStatsView(APIView):
    permission_classes = [IsWorker]
    def get(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        offers = profile.offers.all()
        completed = offers.filter(status='accepted', request__status='completed').count()
        pending = offers.filter(status='pending_response').count()
        return Response({
            'total_completed': completed,
            'pending_offers': pending,
            'avg_rating': float(profile.avg_rating),
            'is_online': profile.is_online,
        })


class WorkerOnlineStatusView(APIView):
    permission_classes = [IsWorker]
    def patch(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        profile.is_online = request.data.get('is_online', False)
        profile.save()
        return Response({'is_online': profile.is_online})


class WorkerPendingMatchView(APIView):
    permission_classes = [IsWorker]
    def get(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response({'has_offer': False, 'offer': None})
        offer = profile.offers.filter(status='pending_response').select_related(
            'request__category', 'request__resident'
        ).first()
        if not offer:
            return Response({'has_offer': False, 'offer': None})
        return Response({'has_offer': True, 'offer': JobOfferSerializer(offer).data})


class WorkerActiveJobView(APIView):
    permission_classes = [IsWorker]
    def get(self, request):
        try:
            profile = request.user.worker_profile
        except WorkerProfile.DoesNotExist:
            return Response(None)
        offer = profile.offers.filter(status='accepted', request__status='offer_accepted').select_related('request').first()
        if not offer:
            return Response(None)
        return Response(JobOfferSerializer(offer).data)


class WorkerAcceptMatchView(APIView):
    permission_classes = [IsWorker]
    def post(self, request, match_id):
        try:
            offer = JobOffer.objects.get(pk=match_id, worker=request.user.worker_profile)
        except (JobOffer.DoesNotExist, WorkerProfile.DoesNotExist):
            return Response({'error': 'Not found'}, status=404)
        offer.status = 'accepted'
        offer.save()
        offer.request.status = 'offer_accepted'
        offer.request.save()
        return Response({'matchId': str(match_id), 'accepted': True})


class WorkerDeclineMatchView(APIView):
    permission_classes = [IsWorker]
    def post(self, request, match_id):
        try:
            offer = JobOffer.objects.get(pk=match_id, worker=request.user.worker_profile)
        except (JobOffer.DoesNotExist, WorkerProfile.DoesNotExist):
            return Response({'error': 'Not found'}, status=404)
        offer.status = 'declined'
        offer.save()
        offer.request.status = 'pending_match'
        offer.request.save()
        return Response({'matchId': str(match_id), 'declined': True})


class WorkerCompleteJobView(APIView):
    permission_classes = [IsWorker]
    def post(self, request, job_id):
        try:
            offer = JobOffer.objects.get(pk=job_id, worker=request.user.worker_profile)
        except (JobOffer.DoesNotExist, WorkerProfile.DoesNotExist):
            return Response({'error': 'Not found'}, status=404)
        offer.request.status = 'completed'
        offer.request.save()
        return Response({'jobId': str(job_id), 'completed': True})

class WorkerDetailView(APIView):
    """
    DELETE /api/workers/<uuid>/
 
    Soft-deletes a worker account by suspending the linked User and
    marking the WorkerProfile as rejected. The profile record is retained
    in compliance with RA 10173 (data retention). The user's is_active is
    set to False, which prevents login without removing any records.
 
    Hard deletion is intentionally not implemented — see ERD Section 5.2.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
 
    def delete(self, request, pk):
        try:
            worker = WorkerProfile.objects.select_related('user').get(pk=pk)
        except WorkerProfile.DoesNotExist:
            return Response({'error': 'Worker not found'}, status=404)
 
        user = worker.user
        user.status    = 'suspended'
        user.is_active = False
        user.save(update_fields=['status', 'is_active'])
 
        worker.verification_status = 'rejected'
        worker.is_suspended        = True
        worker.is_online           = False
        worker.save(update_fields=['verification_status', 'is_suspended', 'is_online'])
 
        return Response(
            {
                'id':      str(pk),
                'deleted': True,
                'note':    (
                    'Account suspended and profile rejected per RA 10173 soft-deletion policy. '
                    'Records are retained; the user cannot log in.'
                ),
            },
            status=200,
        )
class SkillCategoryListView(APIView):
    def get(self, request):
        cats = SkillCategory.objects.filter(is_active=True)
        return Response(SkillCategorySerializer(cats, many=True).data)

