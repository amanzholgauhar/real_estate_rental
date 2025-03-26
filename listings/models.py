# listings/models.py

from users.models import CustomUser  # Убедитесь, что импорт правильный
from django.db import models

class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="properties")

    def __str__(self):
        return self.title
