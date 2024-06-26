from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Task
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile


class UserModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_employee_with_photo(self):
        url = reverse("user-list")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as photo:
            photo.write(b"file_content")
            photo.seek(0)
            data = {
                "username": "employee1",
                "password": "password123",
                "type": User.TYPE_EMPLOYEE,
                "phone": "1234567890",
                "photo": photo,
            }
            response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_employee_without_photo(self):
        url = reverse("user-list")
        data = {
            "username": "employee2",
            "password": "password123",
            "type": User.TYPE_EMPLOYEE,
            "phone": "1234567891",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Фотография обязательна для сотрудников", str(response.data))

    def test_create_customer_with_employee_permissions(self):
        url = reverse("user-list")
        data = {
            "username": "customer1",
            "password": "password123",
            "type": User.TYPE_CUSTOMER,
            "phone": "1234567892",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TaskModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer1",
            password="password123",
            type=User.TYPE_CUSTOMER,
            phone="1234567890",
        )
        self.employee = User.objects.create_user(
            username="employee1",
            password="password123",
            type=User.TYPE_EMPLOYEE,
            phone="1234567891",
        )

    def test_create_task(self):
        url = reverse("task-list")
        data = {
            "client": self.customer.id,
            "status": "pending",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_assign_task_to_employee(self):
        task = Task.objects.create(
            client=self.customer,
            status="pending",
        )
        task.employee = self.employee
        task.save()
        self.assertEqual(task.employee, self.employee)

    def test_complete_task_with_report(self):
        task = Task.objects.create(
            client=self.customer,
            status="in_progress",
            employee=self.employee,
        )
        task.status = "done"
        task.report = "Task completed successfully"
        task.save()
        self.assertEqual(task.status, "done")
        self.assertEqual(task.report, "Task completed successfully")

    def test_complete_task_without_report(self):
        task = Task.objects.create(
            client=self.customer,
            status="in_progress",
            employee=self.employee,
        )
        task.status = "done"
        with self.assertRaises(ValueError):
            task.save()
