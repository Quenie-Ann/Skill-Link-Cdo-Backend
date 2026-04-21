from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # What appears in the user list
    list_display  = ['email', 'role', 'status', 'consent_given', 'is_staff', 'created_at']
    list_filter   = ['role', 'status', 'is_staff']
    search_fields = ['email']
    ordering      = ['email']
    readonly_fields = ['id', 'created_at', 'updated_at']

    # Override BaseUserAdmin fieldsets to match your custom User fields
    # (BaseUserAdmin expects 'username' which your model does not have)
    fieldsets = (
        ('Credentials',   {'fields': ('email', 'password')}),
        ('Role & Status', {'fields': ('role', 'status', 'consent_given')}),
        ('Permissions',   {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Timestamps',    {'fields': ('id', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2', 'role', 'status'),
        }),
    )
