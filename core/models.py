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
    AVAILABILITY_CHOICES = [
        ('Weekdays', 'Weekdays'),
        ('Weekends', 'Weekends'),
        ('Flexible', 'Flexible'),
        ('Everyday', 'Everyday'),
    ]

    DOCUMENT_STATUS = [
        ('pending',   'Pending'),
        ('submitted', 'Submitted'),
        ('verified',  'Verified'),
    ]

    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    full_name          = models.CharField(max_length=100, blank=True)
    service            = models.CharField(max_length=100, blank=True)
    location           = models.CharField(max_length=200, blank=True)
    availability       = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Weekdays')
    experience_years   = models.IntegerField(default=0)
    hourly_rate        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    daily_rate         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating             = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    jobs_done          = models.IntegerField(default=0)
    is_verified        = models.BooleanField(default=False)
    is_suspended       = models.BooleanField(default=False)
    skills             = models.TextField(help_text="e.g., Plumbing, Pipe Fitting, Water Heater")
    bio                = models.TextField(blank=True)
    government_id      = models.CharField(max_length=50, choices=DOCUMENT_STATUS, default='pending')
    barangay_clearance = models.CharField(max_length=50, choices=DOCUMENT_STATUS, default='pending')
    submitted_at       = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Worker: {self.user.username}"

# 3. Job Request (The core feature of your system)
class JobRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('matched',     'Matched'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('cancelled',   'Cancelled'),
    ]

    URGENCY_CHOICES = [
        ('emergency', 'Emergency'),
        ('urgent',    'Urgent'),
        ('normal',    'Normal'),
        ('flexible',  'Flexible'),
    ]

    SCHEDULE_CHOICES = [
        ('asap',     'As Soon As Possible'),
        ('weekdays', 'Weekdays Only'),
        ('weekends', 'Weekends Only'),
        ('flexible', 'Flexible / Any Time'),
    ]

    resident        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    category        = models.CharField(max_length=100)
    description     = models.TextField()
    location        = models.CharField(max_length=200, blank=True)
    budget          = models.CharField(max_length=50, blank=True)
    urgency         = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    schedule        = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='flexible')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.category} ({self.status})"