# тест модели
from django.test import TestCase
from .models import Task
# Create your tests here.

class ModelTestCase(TestCase):
    def setUp(self):
        self.task_name = "Выполнить лабораторную работу №9"
        self.task = Task(name=self.task_name)

    def test_model_can_create_task(self):
        old_count = Task.objects.count()
        self.task.save()
        new_count = Task.objects.count()
        self.assertNotEqual(old_count, new_count)


# тест вьюхи
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.task_data = {
            'name': 'Выполнить 9 лабораторную работу',
            'description': 'Прочитать руководство по django rest framework',
            'priority': 'h'
        }
        self.response = self.client.post(reverse('create'), self.task_data, format='json')

    def test_api_can_create_a_task(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)