from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Property, Booking
from .forms import PropertyForm, BookingForm

User = get_user_model()

class PropertyFormTests(TestCase):
    def test_price_must_be_positive(self):
        form = PropertyForm(data={
            'title': 'Test Property',
            'description': 'A nice place',
            'price': -50,
            'location': 'Test City',
            'phone_number': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_phone_number_format(self):
        invalid = PropertyForm(data={
            'title': 'T',
            'description': 'D',
            'price': 100,
            'location': 'L',
            'phone_number': 'abc123'
        })
        self.assertFalse(invalid.is_valid())
        self.assertIn('phone_number', invalid.errors)

        valid = PropertyForm(data={
            'title': 'T',
            'description': 'D',
            'price': 100,
            'location': 'L',
            'phone_number': '+77171234567'
        })
        self.assertTrue(valid.is_valid())

class BookingFormTests(TestCase):
    def test_property_required(self):
        form = BookingForm(data={'status': 'pending'})
        self.assertFalse(form.is_valid())
        self.assertIn('property', form.errors)

class PropertyAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass1234')
        self.client = APIClient()
        resp = self.client.post(reverse('token_obtain_pair'), {
            'username': 'apiuser',
            'password': 'pass1234'
        }, format='json')
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_property_with_phone(self):
        url = reverse('property-list-create')
        data = {
            'title': 'API Test',
            'description': 'API Desc',
            'price': '150.00',
            'location': 'API City',
            'phone_number': '+77170000000'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phone_number'], '+77170000000')

class PropertyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='vuser', password='pass1234')
        self.client.login(username='vuser', password='pass1234')

    def test_add_property_view(self):
        url = reverse('add_property')
        response = self.client.post(url, {
            'title': 'View Test',
            'description': 'Desc',
            'price': 200,
            'location': 'City',
            'phone_number': '+77170000001'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Property.objects.filter(title='View Test').exists())

    def test_edit_property_view(self):
        prop = Property.objects.create(
            title='Old', description='Old', price=100,
            location='Loc', user=self.user, phone_number='+77170000002'
        )
        url = reverse('edit_property', args=[prop.pk])
        response = self.client.post(url, {
            'title': 'New',
            'description': 'New',
            'price': 120,
            'location': 'NewLoc',
            'phone_number': '+77170000003'
        })
        self.assertEqual(response.status_code, 302)
        prop.refresh_from_db()
        self.assertEqual(prop.title, 'New')
        self.assertEqual(prop.phone_number, '+77170000003')

    def test_delete_property_view(self):
        prop = Property.objects.create(
            title='ToDelete', description='D', price=50,
            location='L', user=self.user
        )
        url = reverse('delete_property', args=[prop.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Property.objects.filter(pk=prop.pk).exists())

class BookingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buser', password='pass1234')
        self.prop = Property.objects.create(
            title='B', description='B', price=75,
            location='L', user=self.user
        )
        self.client.login(username='buser', password='pass1234')

    def test_quick_booking(self):
        url = reverse('quick_booking') + f'?property_id={self.prop.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(property=self.prop, user=self.user).exists())
