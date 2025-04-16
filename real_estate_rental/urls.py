from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),  # 👈 добавь это, если убрала
    path('api/users/', include('users.urls')),  # если есть users.urls
]
