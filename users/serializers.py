from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.validators import UniqueValidator
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.TENANT)
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные данные для входа.")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну строчную букву.")
        return value
