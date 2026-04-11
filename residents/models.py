import uuid
from django.db import models
from django.conf import settings


class ResidentProfile(models.Model):
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resident_profile')
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resident_profiles'
        indexes = [models.Index(fields=['user'])]

    def __str__(self):
        return self.full_name
