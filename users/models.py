# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models  # Убедитесь, что импортировали models

<<<<<<< HEAD
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
=======
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        LANDLORD = 'landlord', 'Landlord'
        TENANT = 'tenant', 'Tenant'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

>>>>>>> 4e781aa2e67265bef6ddaa545fb3efa9327a4be9
