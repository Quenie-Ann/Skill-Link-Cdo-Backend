from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. Custom User Model (Handles Roles)
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('worker', 'Worker'),
        ('resident', 'Resident'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

# 2. Worker Profile (Stores Skills and Ratings)
class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    skills = models.TextField(help_text="e.g., Plumbing, Carpentry")
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Worker: {self.user.username}"

# 3. Job Request (The core feature of your system)
class JobRequest(models.Model):
    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    category = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)