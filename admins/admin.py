# admins/admin.py
from django.contrib import admin
from .models import AdminProfile, AuditLog


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['admin_id', 'get_email', 'barangay_name', 'created_at']
    list_display_links = ['admin_id', 'get_email']
    list_filter = ['barangay_name']
    search_fields = ['user__email', 'barangay_name']
    readonly_fields = ['admin_id', 'created_at']

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ['timestamp', 'admin', 'action', 'target_email', 'ip_address']
    list_filter   = ['action']
    search_fields = ['admin__email', 'target_email', 'detail']
    readonly_fields = ['id', 'admin', 'action', 'target_email',
                       'detail', 'ip_address', 'timestamp']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False