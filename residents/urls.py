# residents/urls.py

from django.urls import path
from .views import ResidentDetailView, ResidentListView, ResidentVerifyView, ResidentRegisterView, ResidentProfileView

urlpatterns = [
    # Admin: list all residents
    path('residents/', ResidentListView.as_view()),

    # Admin: approve / reject a resident profile
    path('residents/<uuid:pk>/verify/', ResidentVerifyView.as_view()),

    # Admin: walk-in resident registration (creates User + ResidentProfile atomically)
    path('residents/register/', ResidentRegisterView.as_view()),
    
    path('resident/profile/', ResidentProfileView.as_view()), 
    path('residents/<uuid:pk>/', ResidentDetailView.as_view()),
]