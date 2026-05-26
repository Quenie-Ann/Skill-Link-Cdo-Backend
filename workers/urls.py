from django.urls import path
from .views import (
    # Existing worker views (unchanged)
    WorkerListCreateView, WorkerVerifyView, WorkerSuspendView, WorkerDetailView,
    WorkerProfileView, WorkerAvailabilityView, WorkerStatsView,
    WorkerOnlineStatusView, WorkerPendingMatchView, WorkerActiveJobView,
    WorkerAcceptMatchView, WorkerDeclineMatchView, WorkerCompleteJobView,
    SkillCategoryListView,
    #  New governance views 
    AdminSkillCategoryCreateView, AdminSkillCategoryDetailView,
    JobTypeListView, AdminJobTypeCreateView, AdminJobTypeDetailView,
    RateBandView, AdminRateBandCreateView, AdminRateBandListView,
    DocumentUploadView,
)
 
urlpatterns = [
 
    # Worker profile management (unchanged) 
    path('workers/',                              WorkerListCreateView.as_view()),
    path('workers/<uuid:pk>/verify/',             WorkerVerifyView.as_view()),
    path('workers/<uuid:pk>/suspend/',            WorkerSuspendView.as_view()),
    path('workers/<uuid:pk>/',                    WorkerDetailView.as_view()),
    path('profile/',                              WorkerProfileView.as_view()),
    path('worker/availability-schedule/',         WorkerAvailabilityView.as_view()),
    path('worker/stats/',                         WorkerStatsView.as_view()),
    path('worker/status/',                        WorkerOnlineStatusView.as_view()),
    path('worker/match/pending/',                 WorkerPendingMatchView.as_view()),
    path('worker/job/active/',                    WorkerActiveJobView.as_view()),
    path('worker/match/<uuid:match_id>/accept/',  WorkerAcceptMatchView.as_view()),
    path('worker/match/<uuid:match_id>/decline/', WorkerDeclineMatchView.as_view()),
    path('worker/job/<uuid:job_id>/complete/',    WorkerCompleteJobView.as_view()),
     
     path('documents/upload/', DocumentUploadView.as_view()),
    # Skill categories — public read (unchanged) 
    path('skill-categories/',
         SkillCategoryListView.as_view()),
 
    # Skill categories — admin write (new)
    path('admin/skill-categories/',
         AdminSkillCategoryCreateView.as_view()),
    path('admin/skill-categories/<uuid:pk>/',
         AdminSkillCategoryDetailView.as_view()),
 
    # Job types — public read (new)
    path('skill-categories/<uuid:category_id>/job-types/',
         JobTypeListView.as_view()),
 
    # Job types — admin write (new)
    path('admin/skill-categories/<uuid:category_id>/job-types/',
         AdminJobTypeCreateView.as_view()),
    path('admin/job-types/<uuid:pk>/',
         AdminJobTypeDetailView.as_view()),
 
    # Rate bands — public read (new) 
    path('skill-categories/<uuid:category_id>/rate-band/',
         RateBandView.as_view()),
 
    # Rate bands — admin write (new)
    path('admin/skill-categories/<uuid:category_id>/rate-band/',
         AdminRateBandCreateView.as_view()),
    path('admin/rate-bands/',
         AdminRateBandListView.as_view()),
]