from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterAPIView, ProfileAPIView, ChangePasswordAPIView,
    PasswordResetRequestView, register_view, login_view, profile_view, LogoutView
)

urlpatterns = [
    # API 
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/form/', profile_view, name='profile_view'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),

    # HTML view 
    path('register/form/', register_view, name='register'),
    path('login/form', login_view, name='login'),

     path('logout/', LogoutView.as_view(), name='logout'),
]
