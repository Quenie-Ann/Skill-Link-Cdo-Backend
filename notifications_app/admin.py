from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['id', 'get_recipient', 'type', 'title', 'is_read', 'created_at']
    list_filter   = ['type', 'is_read']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['id', 'created_at']

    @admin.display(description='Recipient')
    def get_recipient(self, obj):
        return obj.user.email
