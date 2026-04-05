from django.contrib import admin
from .models import User, WorkerProfile, JobRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'service', 'is_verified', 'rating')
    list_filter = ('is_verified', 'availability')
    search_fields = ('full_name', 'service')

@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'resident', 
        'category', 
        'location', 
        'status', 
        'assigned_worker', 
        'created_at'
    )
    list_filter = ('status', 'urgency', 'created_at')
    search_fields = ('resident__username', 'category', 'description')
    list_editable = ('status', 'assigned_worker')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('resident', 'category', 'description', 'location', 'budget')
        }),
        ('Operations', {
            'fields': ('status', 'assigned_worker'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


