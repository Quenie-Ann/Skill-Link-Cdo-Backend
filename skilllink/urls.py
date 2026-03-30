from django.urls import path
from django.contrib import admin
from core import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Workers
    path('api/workers/', views.get_workers),
    path('api/workers/<int:pk>/', views.get_worker),

    # Jobs
    path('api/jobs/', views.get_jobs),
    path('api/jobs/create/', views.create_job),

    # Auth
    path('api/register/', views.register_user),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]