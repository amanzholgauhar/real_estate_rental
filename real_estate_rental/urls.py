# real_estate_rental/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', lambda r: redirect('property_list')),     
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),             
    path('listings/', include('listings.urls')),        
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
