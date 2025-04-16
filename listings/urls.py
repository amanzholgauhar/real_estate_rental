from django.urls import path
from .views import PropertyListCreateAPIView, PropertyRetrieveUpdateDestroyAPIView, TestView

urlpatterns = [
    path('', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('<int:pk>/', PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property-detail'),
    path('test/', TestView.as_view(), name='test'),
]

