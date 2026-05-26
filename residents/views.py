# residents/views.py
from skilllink.storage import upload_to_supabase
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from django.db import transaction

from .models import ResidentDocument, ResidentProfile
from .serializers import ResidentProfileSerializer
from skilllink.permissions import IsAdmin, IsResident


class ResidentListView(APIView):
    """
    GET /api/residents/
    Admin: list all resident profiles for the User Verification page (FR-ADM-01).
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        residents = ResidentProfile.objects.select_related('user').all()
        return Response(ResidentProfileSerializer(residents, many=True).data)


class ResidentVerifyView(APIView):
    """
    PATCH /api/residents/<uuid>/verify/
    Admin approves or rejects a resident's profile (FR-ADM-03).
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        try:
            resident = ResidentProfile.objects.get(pk=pk)
        except ResidentProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        is_verified = request.data.get('is_verified', True)
        resident.verification_status = 'verified' if is_verified else 'pending'
        resident.save()
        return Response(ResidentProfileSerializer(resident).data)


class ResidentRegisterView(APIView):
    """
    POST /api/residents/register/

    Admin walk-in registration for a Resident.
    Creates the User account AND the ResidentProfile in a single
    atomic transaction — if either step fails, neither is committed.

    Request body:
        email           str  required
        password        str  required  (min 6 chars)
        full_name       str  required
        contact_number  str  required
        address         str  required
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        data = request.data

        # Validate required fields
        required = ['email', 'password', 'full_name', 'contact_number', 'address']
        missing  = [f for f in required if not str(data.get(f, '')).strip()]
        if missing:
            return Response(
                {'error': f"Missing required fields: {', '.join(missing)}"},
                status=400,
            )

        if len(data.get('password', '')) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters.'},
                status=400,
            )

        email = data['email'].strip().lower()

        # Atomic creation 
        try:
            with transaction.atomic():
                from users.models import User

                if User.objects.filter(email=email).exists():
                    return Response(
                        {'error': 'A user with this email already exists.'},
                        status=400,
                    )

                user = User.objects.create_user(
                    email=email,
                    password=data['password'],
                    role='resident',
                    status='active',
                )

                profile = ResidentProfile.objects.create(
                    user=user,
                    full_name=data['full_name'].strip(),
                    contact_number=data['contact_number'].strip(),
                    address=data['address'].strip(),
                    verification_status='pending',
                )

        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response(ResidentProfileSerializer(profile).data, status=201)

class ResidentDetailView(APIView):
    """
    DELETE /api/residents/<uuid>/
 
    Soft-deletes a resident account by suspending the linked User.
    The ResidentProfile record is retained in compliance with RA 10173
    (data retention). The user's status is set to 'suspended' and
    is_active to False, which prevents login.
 
    Hard deletion is intentionally not implemented — see ERD Section 5.2.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
 
    def delete(self, request, pk):
        try:
            resident = ResidentProfile.objects.select_related('user').get(pk=pk)
        except ResidentProfile.DoesNotExist:
            return Response({'error': 'Resident not found'}, status=404)
 
        user = resident.user
        user.status    = 'suspended'
        user.is_active = False
        user.save(update_fields=['status', 'is_active'])
 
        # Also mark the profile as rejected so it clears the verification queue
        resident.verification_status = 'rejected'
        resident.save(update_fields=['verification_status'])
 
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
class ResidentProfileView(APIView):
    permission_classes = [IsResident]

    def get(self, request):
        try:
            profile = request.user.resident_profile
        except Exception:
            return Response({'error': 'Profile not found'}, status=404)
        return Response(ResidentProfileSerializer(profile).data)

class ResidentDocumentUploadView(APIView):
    """
    POST /api/residents/documents/upload/
    Uploads a resident's government ID or proof of residence to Supabase Storage.
    Called during registration — AllowAny because the user has no token yet.
    The resident_id ties the document to the correct profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        file        = request.FILES.get('file')
        doc_type    = request.data.get('doc_type', 'government_id')
        resident_id = request.data.get('resident_id')

        if not file:
            return Response({'error': 'No file provided.'}, status=400)
        if not resident_id:
            return Response({'error': 'resident_id is required.'}, status=400)

        try:
            resident = ResidentProfile.objects.get(pk=resident_id)
        except ResidentProfile.DoesNotExist:
            return Response({'error': 'Resident profile not found.'}, status=404)

        # Validate file size — max 10 MB
        if file.size > 10 * 1024 * 1024:
            return Response({'error': 'File size must not exceed 10 MB.'}, status=400)

        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return Response(
                {'error': 'Only PDF, JPG, and PNG files are allowed.'},
                status=400,
            )

        try:
            public_url = upload_to_supabase(
                file=file,
                folder='residents',
                original_filename=file.name,
            )
        except Exception as exc:
            return Response({'error': str(exc)}, status=500)

        doc = ResidentDocument.objects.create(
            resident=resident,
            doc_type=doc_type,
            storage_url=public_url,
            original_filename=file.name,
        )

        return Response({
            'id':          str(doc.id),
            'doc_type':    doc.doc_type,
            'storage_url': doc.storage_url,
            'filename':    doc.original_filename,
            'uploaded_at': doc.uploaded_at,
        }, status=201)


class ResidentDocumentListView(APIView):
    """
    GET /api/residents/<uuid:pk>/documents/
    Admin-only — lists all documents uploaded by a resident.
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            resident = ResidentProfile.objects.get(pk=pk)
        except ResidentProfile.DoesNotExist:
            return Response({'error': 'Resident not found.'}, status=404)

        docs = ResidentDocument.objects.filter(resident=resident)
        return Response([
            {
                'id':          str(d.id),
                'doc_type':    d.doc_type,
                'storage_url': d.storage_url,
                'filename':    d.original_filename,
                'uploaded_at': d.uploaded_at,
            }
            for d in docs
        ])