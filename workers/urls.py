# workers/urls.py
from django.urls import path
from .views import (
    WorkerListCreateView, WorkerVerifyView, WorkerSuspendView, WorkerDetailView,
    WorkerProfileView, WorkerAvailabilityView, WorkerStatsView,
    WorkerOnlineStatusView, WorkerPendingMatchView, WorkerActiveJobView,
    WorkerAcceptMatchView, WorkerDeclineMatchView, WorkerCompleteJobView,
    SkillCategoryListView,
)

urlpatterns = [
    path('workers/', WorkerListCreateView.as_view()),
    path('workers/<uuid:pk>/verify/', WorkerVerifyView.as_view()),
    path('workers/<uuid:pk>/suspend/', WorkerSuspendView.as_view()),
    path('workers/<uuid:pk>/', WorkerDetailView.as_view()),
    path('profile/', WorkerProfileView.as_view()),
    path('worker/availability-schedule/', WorkerAvailabilityView.as_view()),
    path('worker/stats/', WorkerStatsView.as_view()),
    path('worker/status/', WorkerOnlineStatusView.as_view()),
    path('worker/match/pending/', WorkerPendingMatchView.as_view()),
    path('worker/job/active/', WorkerActiveJobView.as_view()),
    path('worker/match/<uuid:match_id>/accept/', WorkerAcceptMatchView.as_view()),
    path('worker/match/<uuid:match_id>/decline/', WorkerDeclineMatchView.as_view()),
    path('worker/job/<uuid:job_id>/complete/', WorkerCompleteJobView.as_view()),
    path('skill-categories/', SkillCategoryListView.as_view()),
]
