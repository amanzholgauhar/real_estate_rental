from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_user(self):
        url = reverse('register')  
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'role': 'tenant',  
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_login_user(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_change_password(self):
        url = reverse('change-password')
        data = {
            'old_password': self.user_data['password'],
            'new_password': 'newpassword123',
        }
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_profile(self):
        url = reverse('profile') 
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])

        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
