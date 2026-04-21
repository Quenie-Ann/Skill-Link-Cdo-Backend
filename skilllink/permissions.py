# skilllink/permissions.py
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only barangay admins can access this endpoint."""
    message = 'You must be a Barangay Admin to access this.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsWorker(BasePermission):
    """Only skilled workers can access this endpoint."""
    message = 'You must be a Skilled Worker to access this.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'worker'
        )


class IsResident(BasePermission):
    """Only residents can access this endpoint."""
    message = 'You must be a Resident to access this.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'resident'
        )