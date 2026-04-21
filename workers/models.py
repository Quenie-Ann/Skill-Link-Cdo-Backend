# workers/models.py
import uuid
from django.db import models
from django.conf import settings


class SkillCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skill_categories'

    def __str__(self):
        return self.category_name


class RateBand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='rate_bands')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    min_rate = models.DecimalField(max_digits=10, decimal_places=2)
    max_rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rate_bands'
        indexes = [models.Index(fields=['category', 'effective_date'])]


class WorkerProfile(models.Model):
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'), ('verified', 'Verified'),
        ('rejected', 'Rejected'), ('flagged', 'Flagged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    skill_category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, related_name='workers')
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    declared_rate = models.DecimalField(max_digits=10, decimal_places=2)
    years_experience = models.IntegerField(default=0)
    bio = models.TextField(null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    is_online = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    # D-04: availability schedule — JSON array of day strings
    availability_schedule = models.JSONField(default=list, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'worker_profiles'
        indexes = [
            models.Index(fields=['skill_category', 'verification_status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.skill_category})'
