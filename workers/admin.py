from django.contrib import admin
from .models import WorkerProfile, SkillCategory, RateBand

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'skill_category', 'verification_status', 'is_online', 'declared_rate', 'avg_rating']
    list_filter = ['verification_status', 'skill_category', 'is_suspended']
    search_fields = ['full_name', 'user__email']

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'is_active', 'created_at']

@admin.register(RateBand)
class RateBandAdmin(admin.ModelAdmin):
    list_display = ['category', 'min_rate', 'max_rate', 'effective_date']
