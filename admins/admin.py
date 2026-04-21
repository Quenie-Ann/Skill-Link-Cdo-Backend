from django.contrib import admin
from .models import AdminProfile


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
