from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    TYPE_EMPLOYEE = "employee"
    TYPE_CUSTOMER = "customer"
    TYPE_CHOICES = [
        (TYPE_EMPLOYEE, "Employee"),
        (TYPE_CUSTOMER, "Customer"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    phone = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
    )


    def save(self, *args, **kwargs):
        if self.type == self.TYPE_EMPLOYEE and not self.photo:
            raise ValueError("Фотография обязательна для сотрудников")
        super().save(*args, **kwargs)



class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает исполнителя"),
        ("in_progress", "В процессе"),
        ("done", "Выполнена"),
    ]

    client = models.ForeignKey(
        User,
        related_name="created_tasks",
        on_delete=models.CASCADE,
        limit_choices_to={"type": User.TYPE_CUSTOMER},
    )
    employee = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"type": User.TYPE_EMPLOYEE},
        
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    report = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.status == "done" and not self.report:
            raise ValueError("Отчет не может быть пустым при закрытии задачи")
        super().save(*args, **kwargs)
