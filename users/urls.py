# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, LogoutView, RegisterView, MeView,
    ForgotPasswordView, ResetPasswordView,
    AdminResetUserPasswordView,
    ChangePasswordView, ActiveSessionsView,
)

urlpatterns = [
    path('login/',         LoginView.as_view()),
    path('logout/',        LogoutView.as_view()),
    path('register/',      RegisterView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('me/',            MeView.as_view()),
    path('auth/forgot-password/', ForgotPasswordView.as_view()),
    path('auth/reset-password/',  ResetPasswordView.as_view()),
    path('admin/users/<uuid:user_id>/reset-password/', AdminResetUserPasswordView.as_view()),
    path('users/me/change-password/', ChangePasswordView.as_view()),
    path('users/me/sessions/',        ActiveSessionsView.as_view()),
]