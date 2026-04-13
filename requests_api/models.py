# requests_api/models.py
import uuid
from django.db import models
from django.conf import settings


class JobRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_match', 'Pending Match'),
        ('offer_sent', 'Offer Sent'),
        ('offer_accepted', 'Offer Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resident = models.ForeignKey('residents.ResidentProfile', on_delete=models.CASCADE, related_name='job_requests')
    category = models.ForeignKey('workers.SkillCategory', on_delete=models.SET_NULL, null=True, related_name='job_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location_address = models.TextField()
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_match')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_requests'
        indexes = [
            models.Index(fields=['resident', 'status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return f'{self.title} [{self.status}]'


class JobOffer(models.Model):
    STATUS_CHOICES = [
        ('pending_response', 'Pending Response'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='offers')
    worker = models.ForeignKey('workers.WorkerProfile', on_delete=models.CASCADE, related_name='offers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_response')
    match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_offers'
        indexes = [
            models.Index(fields=['request', 'status']),
            models.Index(fields=['worker', 'status']),
        ]


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.IntegerField()  # 1-5
    review_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ratings'
        indexes = [models.Index(fields=['rated_user'])]
