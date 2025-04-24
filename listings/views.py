from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
import logging

from .models import Property, Booking
from .serializers import PropertySerializer
from .forms import PropertyForm, BookingForm

# Настройка логгера
logger = logging.getLogger(__name__)

# 🔹 API-проверка
class TestView(APIView):
    def get(self, request):
        return JsonResponse({"message": "It works!"})

# 🔹 Список объявлений + создание
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.select_related('user').prefetch_related('booking_set').all()  # добавление prefetch_related
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

    def get_queryset(self):
        # Даем доступ только к объявлениям, которые принадлежат текущему пользователю
        return Property.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Убедитесь, что только владелец может редактировать объявление
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this property.")
        serializer.save()

    def perform_destroy(self, instance):
        # Проверяем, что только владелец может удалить объявление
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this property.")
        instance.delete()

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


# 🔹 Создание бронирования с логированием и проверкой
@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем бронирование, но не сохраняем объект сразу
                booking = form.save(commit=False)
                booking.user = request.user
                booking.save()

                # Проверяем, что связанное свойство существует перед отправкой email
                if not booking.property:
                    logger.error(f"Property not found for booking: {booking.id}")
                    return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

                # Отправка email о подтверждении бронирования
                send_mail(
                    subject="Бронирование принято",
                    message=f"Ваше бронирование для '{booking.property}' успешно создано.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                )

                # Редирект после успешного бронирования
                return redirect('profile_view')

            except Exception as e:
                # Логирование ошибки при бронировании
                logger.error(f"Error creating booking: {str(e)}")  # Пример логирования ошибки
                return Response({"error": "Произошла ошибка при бронировании."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        form = BookingForm()

    return render(request, 'listings/create_booking.html', {'form': form})

from django.shortcuts import render
from .models import Property
from django.db.models import Q

def property_list_view(request):
    # Получаем все объекты недвижимости
    properties = Property.objects.all()

    # Фильтрация по параметрам (если они есть в GET-запросе)
    search_query = request.GET.get('search', '')
    location_query = request.GET.get('location', '')
    price_query = request.GET.get('price', '')

    # Поиск по названию, описанию и местоположению
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Фильтрация по местоположению
    if location_query:
        properties = properties.filter(location__icontains=location_query)

    # Фильтрация по цене
    if price_query:
        try:
            price = float(price_query)  # Преобразуем цену в число
            properties = properties.filter(price__lte=price)
        except ValueError:
            pass  # Игнорируем ошибки преобразования, если цена не валидна

    return render(request, 'listings/property_list.html', {'properties': properties})
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
import logging

from .models import Property, Booking
from .forms import PropertyForm, BookingForm
from .serializers import PropertySerializer

# Настройка логгера
logger = logging.getLogger(__name__)

# 🔹 API-проверка
class TestView(APIView):
    def get(self, request):
        return JsonResponse({"message": "It works!"})

# 🔹 Список объявлений + создание
class PropertyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.select_related('user').prefetch_related('booking_set').all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 🔹 CRUD одно объявление
class PropertyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this property.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this property.")
        instance.delete()

# 🔹 Добавить объявление
@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.user = request.user  
            property_obj.save()
            return redirect('property_list')
    else:
        form = PropertyForm()

    return render(request, 'listings/add_property.html', {'form': form})

# 🔹 Создание бронирования
@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.save()

                if not booking.property:
                    logger.error(f"Property not found for booking: {booking.id}")
                    return JsonResponse({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

                send_mail(
                    subject="Бронирование подтверждено",
                    message=f"Ваше бронирование для '{booking.property}' успешно создано.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                )

                return redirect('profile_view')
            except Exception as e:
                logger.error(f"Error creating booking: {str(e)}")
                return JsonResponse({"error": "Ошибка при бронировании."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        form = BookingForm()

    return render(request, 'listings/create_booking.html', {'form': form})

# 🔹 Список объявлений с фильтрами
def property_list_view(request):
    properties = Property.objects.all()

    search_query = request.GET.get('search', '')
    location_query = request.GET.get('location', '')
    price_query = request.GET.get('price', '')

    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if location_query:
        properties = properties.filter(location__icontains=location_query)

    if price_query:
        try:
            price = float(price_query)
            properties = properties.filter(price__lte=price)
        except ValueError:
            pass

    return render(request, 'listings/property_list.html', {'properties': properties})

# 🔹 Выход из системы (Logout)
def logout_view(request):
    logout(request)  # Завершаем сессию пользователя
    return redirect('login')  # Перенаправляем на страницу логина
