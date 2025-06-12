
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('', lambda r: redirect('property_list')),     
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),             
    path('listings/', include('listings.urls')), 
    path('i18n/', include('django.conf.urls.i18n')),       
]
urlpatterns += i18n_patterns(
    path('', include('users.urls')),        # главная часть сайта
    path('listings/', include('listings.urls')),  # если нужно
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
