from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL= reverse('user:create')
TOKEN_URL=reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test uses api (public)"""
    def setup(self):
        self.client =APIClient()

    def test_create_valid_user_success(self):
        """test is created successfully"""
        payload={
            'email':'test@gmail.com',
            'password':'testpass',
            'name':'Test name',
        }
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user=get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_exists(self):
        """test to check duplicate user"""
        payload={'email':'test@gmail.com','password':'testpass'}
        create_user(**payload)

        res=self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test that password too short"""
        payload={'email':'test@gmail.com','password':'pw'}
        payload ={
          'email':'test@gmail.com',
          'password':'pw',
          'name':'Test'
        }
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists=get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """token created for user"""
        payload={'email':'test@gmail.com','password':'testpass'}
        create_user(**payload)
        res=self.client.post(TOKEN_URL,payload)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_token_invalid_crediantials(self):
        """Test that token is no created if invalid credentials are given"""
        create_user(email='test@gmail.com',password='testpass')
        payload={'email':'test@gmail.com','password':'wrong'}
        res=self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test that no token if no user"""
        payload={'email':'test@gmail.com','passeord':'testpass'}
        res=self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test the email and password is required"""
        res=self.client.post(TOKEN_URL,{'email':'one','password':''})
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
