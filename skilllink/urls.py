# skilllink/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Skill-Link CDO API",
        default_version='v1',
        description="Barangay-based skilled worker matching system for Cagayan de Oro City",
        contact=openapi.Contact(email="admin@skilllink.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [

    path('admin/', admin.site.urls),

    # Swagger UI and ReDoc endpoints
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/',   schema_view.with_ui('redoc',   cache_timeout=0), name='redoc'),

    path('api/', include('users.urls')),
    path('api/', include('workers.urls')),
    path('api/', include('residents.urls')),
    path('api/', include('requests_api.urls')),
    path('api/', include('notifications_app.urls')),
    path('api/', include('admins.urls')),
]