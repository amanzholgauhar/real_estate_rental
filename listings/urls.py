# listings/urls.py

from django.urls import path
from .views import (
    PropertyListCreateAPIView,
    PropertyRetrieveUpdateDestroyAPIView,
    TestView,
    property_list_view,
    add_property_view,
    edit_property_view,
    delete_property_view,
    quick_booking,
    create_booking,
    my_bookings_view,
    edit_booking_view,
)

urlpatterns = [
    path('', PropertyListCreateAPIView.as_view(),           name='property-list-create'),
    path('<int:pk>/', PropertyRetrieveUpdateDestroyAPIView.as_view(), name='property-detail'),
    path('test/', TestView.as_view(),                         name='test'),

    path('list/',              property_list_view,  name='property_list'),
    path('add/',               add_property_view,   name='add_property'),
    path('<int:pk>/edit/',     edit_property_view,  name='edit_property'),
    path('<int:pk>/delete/',   delete_property_view,name='delete_property'),

    path('book/quick/', quick_booking,       name='quick_booking'),
    path('book/',       create_booking,      name='create_booking'),

    path('my-bookings/',            my_bookings_view, name='my_bookings'),
    path('my-bookings/<int:pk>/edit/', edit_booking_view, name='edit_booking'),
]
