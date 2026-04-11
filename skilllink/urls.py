from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('workers.urls')),
    path('api/', include('residents.urls')),
    path('api/', include('requests_api.urls')),
    path('api/', include('notifications_app.urls')),
]