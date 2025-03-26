# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models  # Убедитесь, что импортировали models

class CustomUser(AbstractUser):
    # Дополнительные поля, если необходимо
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Устанавливаем имя для обратной связи
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Устанавливаем имя для обратной связи
        blank=True
    )
