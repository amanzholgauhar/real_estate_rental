# listings/urls.py

from django.urls import path
from .views import (
    TestView,
    PropertyListCreateAPIView,
    PropertyRetrieveUpdateDestroyAPIView,
    property_list_view,
    property_detail_view,
    add_property_view,
    edit_property_view,
    delete_property_view,
    quick_booking,
    create_booking,
    my_bookings_view,
    edit_booking_view,
    create_review,
    edit_review,
)

urlpatterns = [
    # ── HTML URLs ── #
    path('list/', property_list_view, name='property_list'),
    path('<int:pk>/', property_detail_view, name='property_detail'),
    path('add/', add_property_view, name='add_property'),
    path('<int:pk>/edit/', edit_property_view, name='edit_property'),
    path('<int:pk>/delete/', delete_property_view, name='delete_property'),

    path('book/quick/', quick_booking, name='quick_booking'),
    path('book/', create_booking, name='create_booking'),

    path('my-bookings/', my_bookings_view, name='my_bookings'),
    path('my-bookings/<int:pk>/edit/', edit_booking_view, name='edit_booking'),

    # reviews
    path('<int:pk>/reviews/new/',  create_review, name='create_review'),
    path('reviews/<int:pk>/edit/', edit_review,  name='edit_review'),

    # ── API URLs ── #
    path('api/test/', TestView.as_view(), name='api_test'),
    path('api/properties/', PropertyListCreateAPIView.as_view(), name='api_property_list_create'),
    path('api/properties/<int:pk>/', PropertyRetrieveUpdateDestroyAPIView.as_view(),
         name='api_property_detail'),
]
