from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField

from .serializers import RegisterSerializer

from django.shortcuts import render, redirect
from .forms import RegisterForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Хэширование пароля
            user.save()
            return redirect('login')  # Перенаправление на страницу логина после регистрации
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


from django.contrib.auth import authenticate, login
from .forms import LoginForm

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("profile_view")  # это HTML-страница
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    
    return render(request, "users/login.html", {"form": form})

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

            # Проверка старого пароля
            if not user.check_password(old_password):
                return Response({'error': 'Старый пароль неверен.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Валидация нового пароля
                validate_password(new_password, user=user)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# users/views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # Завершаем сессию пользователя
    return redirect('login')  # Перенаправление на страницу логина
