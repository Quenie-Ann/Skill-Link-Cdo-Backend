# admins/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AdminProfile, AuditLog  
from .serializers import AdminProfileSerializer, AdminProfileCreateSerializer
from skilllink.permissions import IsAdmin


class AdminProfileView(APIView):
    """
    GET  /api/admin/profile/   — Retrieve the authenticated admin's profile.
    POST /api/admin/profile/   — Create the AdminProfile for the authenticated admin.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            profile = AdminProfile.objects.get(user=request.user)
        except AdminProfile.DoesNotExist:
            return Response(
                {'detail': 'Admin profile not found. Please create one.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AdminProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        # Prevent creating a duplicate profile.
        if AdminProfile.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'Admin profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AdminProfileCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProfileUpdateView(APIView):
    """
    PATCH /api/admin/profile/update/  — Update the barangay_name field.
    """
    permission_classes = [IsAdmin]

    def patch(self, request):
        try:
            profile = AdminProfile.objects.get(user=request.user)
        except AdminProfile.DoesNotExist:
            return Response(
                {'detail': 'Admin profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AdminProfileSerializer(
            profile,
            data=request.data,
            partial=True   # partial=True allows updating only barangay_name
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AuditLogView(APIView):
    """
    GET /api/admin/audit-log/ — View all admin actions
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')[:100]
        data = [
            {
                'id':           str(log.id),
                'admin':        log.admin.email if log.admin else 'deleted',
                'action':       log.action,
                'target_email': log.target_email,
                'detail':       log.detail,
                'ip_address':   log.ip_address,
                'timestamp':    log.timestamp,
            }
            for log in logs
        ]
        return Response(data)






