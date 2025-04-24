from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Property

User = get_user_model()

class PropertyAPITests(TestCase):
    def setUp(self):
        # создаём пользователей и объекты недвижимости для тестирования
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # создаем объявления недвижимости, привязываем к пользователю
        self.property_1 = Property.objects.create(title="Apartment 1", description="Nice apartment", location="New York", price=100, user=self.user)
        self.property_2 = Property.objects.create(title="Apartment 2", description="Beautiful apartment", location="London", price=200, user=self.user)

    def test_filter_search(self):
        # используем reverse для построения правильного URL
        url = reverse('property-list-create')  # Убедитесь, что у вас правильное имя URL
        response = self.client.get(url, {'search': 'apartment'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # Все объявления с "apartment" в title, description или location

    def test_sorting_by_price(self):
        # используем reverse для построения правильного URL
        url = reverse('property-list-create')  # Убедитесь, что у вас правильное имя URL
        response = self.client.get(url, {'ordering': 'price'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['price'], 100)  # Проверка, что первое объявление с минимальной ценой
        self.assertEqual(response.data[1]['price'], 200)  # Проверка, что второе объявление с большей ценой
