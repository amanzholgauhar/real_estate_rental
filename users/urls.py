from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterAPIView, ProfileAPIView, ChangePasswordAPIView, PasswordResetRequestView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
]
