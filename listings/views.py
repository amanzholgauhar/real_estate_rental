from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Property, Booking
from .serializers import PropertySerializer
from .forms import PropertyForm, BookingForm

# 🔹 API-проверка
class TestView(APIView):
    def get(self, request):
        return JsonResponse({"message": "It works!"})

# 🔹 Список объявлений + создание
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'location']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 🔹 CRUD одно объявление
class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

# 🔹 HTML: Добавить объявление
@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.user = request.user  
            property_obj.save()
            return redirect('property_list')  # поменяй на нужный URL
    else:
        form = PropertyForm()

    return render(request, 'listings/add_property.html', {'form': form})
from django.core.mail import send_mail
from django.conf import settings

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            # ✉️ Отправка email
            send_mail(
                subject="Бронирование принято",
                message=f"Ваше бронирование для '{booking.property}' успешно создано.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
            )

            return redirect('profile_view')
    else:
        form = BookingForm()
    return render(request, 'listings/create_booking.html', {'form': form})
