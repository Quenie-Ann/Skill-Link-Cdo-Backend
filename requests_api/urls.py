# requests_api/urls.py
from django.urls import path
from .views import (
    RequestListCreateView, RequestStatusView, ResidentRequestsView,
    JobHistoryView, RatingCreateView, SendOfferView,
    StatsView, WeeklyStatsView, SkillBreakdownView, MatchLogsView, ActivityFeedView,
)

urlpatterns = [
    path('requests/', RequestListCreateView.as_view()),
    path('requests/<uuid:pk>/status/', RequestStatusView.as_view()),
    path('resident/requests/', ResidentRequestsView.as_view()),
    path('jobs/history/', JobHistoryView.as_view()),
    path('ratings/', RatingCreateView.as_view()),
    path('requests/<uuid:request_id>/send-offer/<uuid:worker_id>/',
         SendOfferView.as_view()),
    # Admin analytics
    path('stats/', StatsView.as_view()),
    path('stats/weekly/', WeeklyStatsView.as_view()),
    path('stats/skills/', SkillBreakdownView.as_view()),
    path('matches/logs/', MatchLogsView.as_view()),
    path('activity/', ActivityFeedView.as_view()),
]
