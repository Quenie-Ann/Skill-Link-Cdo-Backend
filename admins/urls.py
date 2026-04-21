from django.urls import path
from .views import AdminProfileView, AdminProfileUpdateView

urlpatterns = [
    path('admin/profile/',        AdminProfileView.as_view()),
    path('admin/profile/update/', AdminProfileUpdateView.as_view()),
]
