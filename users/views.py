from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from rest_framework.serializers import CharField

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
