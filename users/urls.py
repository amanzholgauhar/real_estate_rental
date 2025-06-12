from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    profile_view,
    profile_edit_view,
    change_password_view,
    register_view,
    login_view,
    logout_view,
    password_reset_form_view,
    password_reset_confirm_view,
    RegisterAPIView,
    ProfileAPIView,
    ChangePasswordAPIView,
    PasswordResetRequestView,
    LogoutView,
)

urlpatterns = [
    # — API —
    path('register/',      RegisterAPIView.as_view(),       name='register_api'),
    path('login/',         TokenObtainPairView.as_view(),   name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),      name='token_refresh'),
    path('profile/',       ProfileAPIView.as_view(),        name='profile_api'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password_api'),
    path('password-reset/',  PasswordResetRequestView.as_view(), name='password_reset_api'),
    path('logout/',         LogoutView.as_view(),           name='logout_api'),

    # — HTML —
    path('register/form/', register_view,            name='register'),
    path('login/form/',    login_view,               name='login'),
    path('logout/form/',   logout_view,              name='logout'),
    path('profile/form/',  profile_view,             name='profile_view'),
    path('profile/edit/form/', profile_edit_view,    name='profile_edit_form'),
    path('change-password/form/', change_password_view, name='change_password_form'),
    path('password-reset/form/',      password_reset_form_view,   name='password_reset_form'),
    path('password-reset-confirm/form/<uidb64>/<token>/', password_reset_confirm_view,
         name='password_reset_confirm_form'),
]
