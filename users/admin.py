from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'role', 'status', 'consent_given',
                     'deletion_requested', 'is_staff', 'created_at']
    list_filter   = ['role', 'status', 'is_staff', 'consent_given', 'deletion_requested']
    search_fields = ['email']
    ordering      = ['email']
    readonly_fields = ['id', 'created_at', 'updated_at',
                       'consent_timestamp', 'consent_ip_address',
                       'deletion_requested_at']

    fieldsets = (
        ('Credentials',   {'fields': ('email', 'password')}),
        ('Role & Status', {'fields': ('role', 'status', 'consent_given')}),
        ('Permissions',   {'fields': ('is_staff', 'is_superuser', 'is_active',
                                      'groups', 'user_permissions')}),
        ('Timestamps',    {'fields': ('id', 'created_at', 'updated_at')}),
    
        ('RA 10173 Compliance', {'fields': ('consent_timestamp',
                                            'consent_ip_address',
                                            'consent_version')}),
        
        ('Account Deletion Request', {'fields': ('deletion_requested',
                                                  'deletion_requested_at',
                                                  'deletion_reason')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2', 'role', 'status'),
        }),
    )