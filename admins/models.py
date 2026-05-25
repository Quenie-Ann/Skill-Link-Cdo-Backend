# admins/models.py
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
    
# ✅ NEW — Audit Log for RA 10173 Compliance
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('verify_worker',    'Verified Worker'),
        ('reject_worker',    'Rejected Worker'),
        ('verify_resident',  'Verified Resident'),
        ('reject_resident',  'Rejected Resident'),
        ('suspend_user',     'Suspended User'),
        ('reactivate_user',  'Reactivated User'),
        ('approve_deletion', 'Approved Account Deletion'),
        ('reject_deletion',  'Rejected Account Deletion'),
        ('create_category',  'Created Skill Category'),
        ('update_category',  'Updated Skill Category'),
        ('cancel_job',       'Cancelled Job Request'),
        ('login',            'Admin Login'),
        ('logout',           'Admin Logout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_email = models.EmailField(null=True, blank=True)
    detail = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.admin.email} → {self.action} at {self.timestamp}'





    





