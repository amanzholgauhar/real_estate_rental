# users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterAPIView,
    ProfileAPIView,
    ChangePasswordAPIView,
    PasswordResetRequestView,
    password_reset_form_view,
    password_reset_confirm_view,
    register_view,
    login_view,
    profile_view,
    logout_view,
)

urlpatterns = [
    # ─── REST API ────────────────────────────────────────────────────────────────
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_api'),

    # ─── HTML VIEWS ─────────────────────────────────────────────────────────────
    # Registration & Login
    path('register/form/', register_view,    name='register'),
    path('login/form/',    login_view,       name='login'),
    path('logout/',        logout_view,      name='logout'),

    # Profile
    path('profile/form/',  profile_view,     name='profile_view'),

    # Password Reset (HTML)
    path(
        'password-reset/form/',
        password_reset_form_view,
        name='password_reset_form'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        password_reset_confirm_view,
        name='password_reset_confirm'
    ),
]
