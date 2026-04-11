from django.contrib import admin
from .models import JobRequest, JobOffer, Rating

@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'resident', 'created_at']
    list_filter = ['status', 'category']

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['request', 'worker', 'status', 'match_score', 'created_at']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['rater', 'rated_user', 'score', 'created_at']
