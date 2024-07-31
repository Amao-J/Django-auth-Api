import os
from django.conf import settings

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'findfuel_comprehensive')  # Replace 'your_project' with your actual project name

# Import the remaining necessary modules
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.user.models import User, Profile
from django.core import mail

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth-register-list')
        self.verify_otp_url = reverse('auth-verify-otp-verify-otp')
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration_and_otp_generation(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email=self.user_data['email'])
        profile = Profile.objects.get(user=user)
        
        self.assertIsNotNone(profile.otp)
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(profile.otp, mail.outbox[0].body)

    def test_verify_otp(self):
        # Register user to generate OTP
        self.client.post(self.register_url, self.user_data, format='json')
        
        user = User.objects.get(email=self.user_data['email'])
        profile = Profile.objects.get(user=user)
        otp = profile.otp
        
        verify_otp_data = {
            'email': self.user_data['email'],
            'otp': otp
        }

        response = self.client.post(self.verify_otp_url, verify_otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        profile.refresh_from_db()
        
        self.assertTrue(user.is_active)
        self.assertEqual(profile.otp, '')
    
    def test_verify_otp_invalid(self):
        # Register user to generate OTP
        self.client.post(self.register_url, self.user_data, format='json')
        
        user = User.objects.get(email=self.user_data['email'])
        profile = Profile.objects.get(user=user)
        
        verify_otp_data = {
            'email': self.user_data['email'],
            'otp': '000000'  # Invalid OTP
        }

        response = self.client.post(self.verify_otp_url, verify_otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        user.refresh_from_db()
        profile.refresh_from_db()
        
        self.assertFalse(user.is_active)
        self.assertNotEqual(profile.otp, '')

