from django.urls import path
from .views import PropertyListCreateAPIView, PropertyRetrieveUpdateDestroyAPIView, TestView
from .views import add_property_view
from .views import create_booking
urlpatterns = [
    path('', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('<int:pk>/', PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property-detail'),
    path('test/', TestView.as_view(), name='test'),
    path('add/', add_property_view, name='add_property'),
    path('book/', create_booking, name='create_booking'),
]

