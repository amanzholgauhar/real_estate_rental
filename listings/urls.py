# listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Здесь указываем основной путь для listings
]
