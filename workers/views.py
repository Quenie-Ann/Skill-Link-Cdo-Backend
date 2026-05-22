# workers/views.py
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import WorkerProfile, SkillCategory, RateBand, JobType
from .serializers import WorkerProfileSerializer, WorkerCreateSerializer, SkillCategorySerializer, RateBandSerializer
from requests_api.models import JobOffer
from requests_api.serializers import JobOfferSerializer
from skilllink.permissions import IsAdmin, IsResident, IsWorker
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

# Skill Category Views    
class SkillCategoryListView(APIView):
    def get(self, request):
        cats = SkillCategory.objects.filter(is_active=True)
        return Response(SkillCategorySerializer(cats, many=True).data)

class AdminSkillCategoryCreateView(APIView):
    """
    POST /api/admin/skill-categories/
    Creates a new SkillCategory in workers_skill_categories table.
    This is the same table that WorkerProfile.skill_category FK points to,
    that RegisterUser reads for the dropdown, and that ResidentDashboard
    reads for the category tile grid.
    Body: { category_name, description (optional) }
    """
    permission_classes = [IsAdmin]
 
    def post(self, request):
        name = request.data.get('category_name', '').strip()
        if not name:
            return Response({'error': 'category_name is required.'}, status=400)
        if SkillCategory.objects.filter(category_name__iexact=name).exists():
            return Response(
                {'error': f'Category "{name}" already exists.'}, status=400
            )
        cat = SkillCategory.objects.create(
            category_name=name,
            description=request.data.get('description', ''),
            is_active=True,
        )
        return Response(SkillCategorySerializer(cat).data, status=201)
 
 
class AdminSkillCategoryDetailView(APIView):
    """
    PATCH  /api/admin/skill-categories/<uuid:pk>/
    DELETE /api/admin/skill-categories/<uuid:pk>/
 
    PATCH renames or toggles is_active.
    DELETE is a soft-delete: sets is_active=False so the category
    disappears from public lists but existing WorkerProfile FKs are
    not broken.
    """
    permission_classes = [IsAdmin]
 
    def patch(self, request, pk):
        try:
            cat = SkillCategory.objects.get(pk=pk)
        except SkillCategory.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)
 
        if 'category_name' in request.data:
            new_name = request.data['category_name'].strip()
            if SkillCategory.objects.filter(
                category_name__iexact=new_name
            ).exclude(pk=pk).exists():
                return Response(
                    {'error': f'Category "{new_name}" already exists.'}, status=400
                )
            cat.category_name = new_name
 
        if 'description' in request.data:
            cat.description = request.data['description']
 
        if 'is_active' in request.data:
            cat.is_active = bool(request.data['is_active'])
 
        cat.save()
        return Response(SkillCategorySerializer(cat).data)
 
    def delete(self, request, pk):
        try:
            cat = SkillCategory.objects.get(pk=pk)
        except SkillCategory.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)
 
        cat.is_active = False
        cat.save()
        return Response({
            'id': str(pk),
            'deleted': True,
            'note': 'Category deactivated. Existing worker profiles are unaffected.',
        })

# JobType Views
class JobTypeListView(APIView):
    """
    GET /api/skill-categories/<uuid:category_id>/job-types/
 
    Public endpoint. Returns active job types for a given category.
    Called by ResidentDashboard Step 2 to populate the specific
    problem selection list dynamically instead of reading from mockData.js.
    """
    def get(self, request, category_id):
        try:
            SkillCategory.objects.get(pk=category_id, is_active=True)
        except SkillCategory.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)
 
        items = JobType.objects.filter(
            category_id=category_id, is_active=True
        ).order_by('name')
 
        return Response([{'id': str(j.id), 'name': j.name} for j in items])
 
 
class AdminJobTypeCreateView(APIView):
    """
    POST /api/admin/skill-categories/<uuid:category_id>/job-types/
 
    Admin adds a job type under a category.
    Body: { name: "Fix leaking pipe" }
    """
    permission_classes = [IsAdmin]
 
    def post(self, request, category_id):
        try:
            cat = SkillCategory.objects.get(pk=category_id)
        except SkillCategory.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)
 
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'name is required.'}, status=400)
 
        if JobType.objects.filter(
            category=cat, name__iexact=name
        ).exists():
            return Response(
                {'error': f'Job type "{name}" already exists under this category.'},
                status=400,
            )
 
        jt = JobType.objects.create(category=cat, name=name, is_active=True)
        return Response({
            'id':          str(jt.id),
            'name':        jt.name,
            'category_id': str(cat.id),
        }, status=201)
 
 
class AdminJobTypeDetailView(APIView):
    """
    PATCH  /api/admin/job-types/<uuid:pk>/  — rename or toggle
    DELETE /api/admin/job-types/<uuid:pk>/  — soft-delete
    """
    permission_classes = [IsAdmin]
 
    def patch(self, request, pk):
        try:
            jt = JobType.objects.get(pk=pk)
        except JobType.DoesNotExist:
            return Response({'error': 'Job type not found.'}, status=404)
 
        if 'name' in request.data:
            jt.name = request.data['name'].strip()
        if 'is_active' in request.data:
            jt.is_active = bool(request.data['is_active'])
        jt.save()
        return Response({'id': str(jt.id), 'name': jt.name})
 
    def delete(self, request, pk):
        try:
            jt = JobType.objects.get(pk=pk)
        except JobType.DoesNotExist:
            return Response({'error': 'Job type not found.'}, status=404)
 
        jt.is_active = False
        jt.save()
        return Response({'id': str(pk), 'deleted': True})
    
# Rate Band Views    
class RateBandView(APIView):
    """
    GET /api/skill-categories/<uuid:category_id>/rate-band/
 
    Public endpoint. Returns the most recently effective rate band
    for a category. Called during worker registration so the worker
    can see the allowed range before submitting their declared_rate.
    """
    def get(self, request, category_id):
        band = RateBand.objects.filter(
            category_id=category_id
        ).order_by('-effective_date').first()
 
        if not band:
            return Response(
                {'detail': 'No rate band set for this category.'}, status=404
            )
 
        return Response({
            'category_id':    str(category_id),
            'min_rate':       str(band.min_rate),
            'max_rate':       str(band.max_rate),
            'effective_date': band.effective_date.isoformat(),
        })
 
 
class AdminRateBandCreateView(APIView):
    """
    POST /api/admin/skill-categories/<uuid:category_id>/rate-band/
 
    Admin sets a new rate band for a category. Each POST inserts a
    new RateBand row (history is preserved). The most recent row by
    effective_date is always the active band.
 
    Rate band enforcement happens at two points:
      1. New registrations — WorkerCreateSerializer.validate() checks
         declared_rate against the active band and flags automatically.
      2. Existing workers — run: python manage.py enforce_rate_bands
         after calling this endpoint.
 
    Body: { min_rate: 300, max_rate: 800 }
    """
    permission_classes = [IsAdmin]
 
    def post(self, request, category_id):
        try:
            cat = SkillCategory.objects.get(pk=category_id)
        except SkillCategory.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)
 
        min_rate = request.data.get('min_rate')
        max_rate = request.data.get('max_rate')
 
        if min_rate is None or max_rate is None:
            return Response(
                {'error': 'Both min_rate and max_rate are required.'}, status=400
            )
 
        try:
            min_rate = float(min_rate)
            max_rate = float(max_rate)
        except (ValueError, TypeError):
            return Response(
                {'error': 'min_rate and max_rate must be numeric.'}, status=400
            )
 
        if min_rate < 0 or max_rate < 0:
            return Response({'error': 'Rates cannot be negative.'}, status=400)
        if min_rate >= max_rate:
            return Response(
                {'error': 'min_rate must be strictly less than max_rate.'}, status=400
            )
 
        band = RateBand.objects.create(
            category=cat,
            created_by=request.user,
            min_rate=min_rate,
            max_rate=max_rate,
        )
 
        return Response({
            'id':             str(band.id),
            'category_id':    str(cat.id),
            'category_name':  cat.category_name,
            'min_rate':       str(band.min_rate),
            'max_rate':       str(band.max_rate),
            'effective_date': band.effective_date.isoformat(),
        }, status=201)
 
 
class AdminRateBandListView(APIView):
    """
    GET /api/admin/rate-bands/
 
    Returns one row per active SkillCategory showing its current
    effective rate band. Used by the RateGovernance admin page to
    populate the overview panel on load.
    """
    permission_classes = [IsAdmin]
 
    def get(self, request):
        cats   = SkillCategory.objects.filter(is_active=True)
        result = []
 
        for cat in cats:
            band = RateBand.objects.filter(
                category=cat
            ).order_by('-effective_date').first()
 
            result.append({
                'category_id':    str(cat.id),
                'category_name':  cat.category_name,
                'min_rate':       str(band.min_rate)       if band else None,
                'max_rate':       str(band.max_rate)       if band else None,
                'effective_date': band.effective_date.isoformat() if band else None,
                'band_set':       band is not None,
            })
 
        return Response(result)

class ResidentWorkerDirectoryView(APIView):
    """
    GET /api/workers/directory/?category=<uuid>
    Resident-accessible. Returns verified, non-suspended workers.
    """
    permission_classes = [IsResident]

    def get(self, request):
        category_id = request.query_params.get('category')
        qs = WorkerProfile.objects.filter(
            verification_status='verified',
            is_suspended=False,
        ).select_related('skill_category', 'user')
        if category_id:
            qs = qs.filter(skill_category_id=category_id)
        return Response(WorkerProfileSerializer(qs, many=True).data)
