# listings/serializers.py

from rest_framework import serializers
from .models import Property

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'price',
            'location',
            'phone_number',
            'image',
            'user',
        ]
        read_only_fields = ['user']
