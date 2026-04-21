import uuid
from django.db import models
from django.conf import settings


class AdminProfile(models.Model):
    """
    Stores barangay-specific information for users with role='admin'.
    Each admin user has exactly one AdminProfile (1:0..1 per ERD Section 3).
    """
    admin_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile'
        # OneToOneField enforces the 1:0..1 relationship from the ERD.
        # related_name='admin_profile' lets you access the profile from
        # a User instance as: user.admin_profile
    )
    barangay_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_profiles'

    def __str__(self):
        return f'AdminProfile — {self.user.email} ({self.barangay_name})'
