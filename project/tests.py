import unittest
from django.contrib.auth.models import User
from django.test import TestCase, Client


class HomeTestAnonymousUser(TestCase, unittest.TestCase):

    def test_home_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')


class HomeTestAuthenticatedUser(TestCase, unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user('test_user', 'test@example.com', '1234')
        user.is_staff=True
        user.save()
        self.client.login(username='test_user', password='1234')

    def test_home_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')