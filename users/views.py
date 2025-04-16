from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField

from .serializers import RegisterSerializer

User = get_user_model()


# 🔹 Регистрация
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# 🔹 Профиль текущего пользователя (GET)
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return Response(data)


# 🔹 Смена пароля
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        old_password = CharField(required=True)
        new_password = CharField(required=True)

    def post(self, request):
        user = request.user
        serializer = self.InputSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({'error': 'Старый пароль неверен.'}, status=400)

            try:
                validate_password(new_password, user=user)
            except Exception as e:
                return Response({'error': e.messages}, status=400)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Пароль успешно изменён.'}, status=200)

        return Response(serializer.errors, status=400)


# 🔹 Восстановление пароля по email
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email not found"}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:8000/reset-password/{uid}/{token}/"

        send_mail(
            subject="Password Reset",
            message=f"Click to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "Reset link sent to email"}, status=status.HTTP_200_OK)
