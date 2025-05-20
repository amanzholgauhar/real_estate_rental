# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterAPIView,
    ProfileAPIView,
    ChangePasswordAPIView,
    PasswordResetRequestView,
    register_view,
    login_view,
    profile_view,
    logout_view,
)

urlpatterns = [
    # API endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/',    TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileAPIView.as_view(),        name='profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('password-reset/',  PasswordResetRequestView.as_view(), name='password-reset'),

    # HTML views
    path('register/form/', register_view,  name='register_form'),
    path('login/form/',    login_view,     name='login_form'),
    path('profile/form/',  profile_view,   name='profile_form'),
    path('logout/',        logout_view,    name='logout'),
]
