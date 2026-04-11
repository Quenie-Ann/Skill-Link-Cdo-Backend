from django.urls import path
from .views import ResidentListView, ResidentVerifyView

urlpatterns = [
    path('residents/', ResidentListView.as_view()),
    path('residents/<uuid:pk>/verify/', ResidentVerifyView.as_view()),
]
