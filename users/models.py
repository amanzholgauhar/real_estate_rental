from django.db import models

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


