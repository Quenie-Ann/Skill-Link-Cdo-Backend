from django.contrib import admin
from .models import ResidentProfile

@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'verification_status', 'created_at']
    list_filter = ['verification_status']
    search_fields = ['full_name', 'user__email']
