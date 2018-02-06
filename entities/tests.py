from django.contrib.auth.models import User
from django.test import TestCase  # , Client
from .models import Entity


class EntityTestAnonymousUser(TestCase):

    def test_anonymous_cannot_view_entities_using_api(self):
        response = self.client.get('/api/entities/')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_create_entity_using_api(self):
        response = self.client.post(
            '/api/entities/', data={'name': 'abcdef industries'})
        self.assertIn("Authentication credentials were not provided.",
                      response.content.decode())


class EntityTestActiveUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_active_user', 'test@example.com', '1234')
        self.client.login(username='test_active_user', password='1234')

    def test_nonstaff_cannot_view_entities_using_api(self):
        response = self.client.get('/api/entities/')
        self.assertEqual(response.status_code, 403)

    def test_nonstaff_cannot_create_entity_using_api(self):
        response = self.client.post(
            '/api/entities/', data={'name': 'abcdef industries'})
        self.assertIn(
            "You do not have permission to perform this action.",
            response.content.decode())


class EntityTestStaffUser(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        user.is_staff = True
        user.save()
        self.client.login(username='test_staff_user', password='1234')

    def test_staff_can_view_entities_using_api(self):
        response = self.client.get('/api/entities/')
        self.assertEqual(response.status_code, 200)

    def test_staff_can_create_entity_using_api(self):
        response = self.client.post(
            '/api/entities/', data={'name': 'abcdef industries'})
        self.assertIn('abcdef', response.content.decode())
        self.assertEqual(Entity.objects.count(), 1)


class EntityTestEntity(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        user.is_staff = True
        user.save()
        self.client.login(username='test_staff_user', password='1234')
        self.response = self.client.post(
            '/api/entities/', data={'name': 'abcdef industries'})

    def test_new_entity_has_correct_name(self):
        entity_obj = Entity.objects.first()
        self.assertEqual(entity_obj.name, 'abcdef industries')

    def test_new_entity_has_correct_code(self):
        entity_obj = Entity.objects.first()
        self.assertEqual(entity_obj.code, 'ABCDEF')
