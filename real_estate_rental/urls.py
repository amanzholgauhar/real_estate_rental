from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', lambda request: redirect('login')),  # Перенаправление на страницу логина
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # Пользователи
    path('api/listings/', include('listings.urls')),  # Объявления
    path('listings/', include('listings.urls')), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)