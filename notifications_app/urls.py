from django.urls import path
from .views import NotificationListView, NotificationDetailView

urlpatterns = [
    path('notifications/', NotificationListView.as_view()),
    path('notifications/<uuid:pk>/read/', NotificationDetailView.as_view(), {'action': 'read'}),
    path('notifications/<uuid:pk>/', NotificationDetailView.as_view()),
]
