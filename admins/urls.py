# admins/urls.py
from django.urls import path
from .views import AdminProfileView, AdminProfileUpdateView, AuditLogView  

urlpatterns = [
    path('admin/profile/',        AdminProfileView.as_view()),
    path('admin/profile/update/', AdminProfileUpdateView.as_view()),
     path('admin/audit-log/',      AuditLogView.as_view()),  
]
