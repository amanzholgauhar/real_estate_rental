# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import CharField

from .serializers import RegisterSerializer
from .forms import RegisterForm, LoginForm

User = get_user_model()


# ——— HTML Views ——— #

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('profile_view')
            form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def password_reset_form_view(request):
    """
    HTML-форма: вводим email, отправляем письмо со ссылкой сброса.
    """
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[uid, token])
            )
            send_mail(
                subject="Password Reset",
                message=f"Click to reset your password:\n\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            message = "Ссылка для сброса пароля отправлена на ваш Email."
        except User.DoesNotExist:
            message = "Пользователь с таким Email не найден."
    return render(request, 'users/password_reset_form.html', {
        'message': message
    })


def password_reset_confirm_view(request, uidb64, token):
    """
    Обработка ссылки из письма: проверка токена и ввод нового пароля.
    """
    error = ''
    user = None
    validlink = False

    # 1) Декодируем uid и получаем пользователя
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # 2) Проверяем токен
    if user and default_token_generator.check_token(user, token):
        validlink = True
    else:
        error = "Ссылка устарела или неверна."

    # 3) Если форма отправлена и ссылка валидна — сохраняем новый пароль
    if request.method == 'POST' and validlink:
        new_password = request.POST.get('new_password')
        try:
            validate_password(new_password, user=user)
            user.set_password(new_password)
            user.save()
            login(request, user)
            return redirect('profile_view')
        except Exception as e:
            # Собираем все сообщения об ошибках в одну строку
            if hasattr(e, 'messages'):
                error = " ".join(e.messages)
            else:
                error = str(e)

    return render(request, 'users/password_reset_confirm.html', {
        'error': error,
        'validlink': validlink
    })


# ——— API Views ——— #

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'role': user.role
        })


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        old_password = CharField(required=True)
        new_password = CharField(required=True)

    def post(self, request):
        user = request.user
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Старый пароль неверен.'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_password(serializer.validated_data['new_password'], user)
            except Exception as e:
                return Response({'error': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Пароль успешно изменён.'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API-endpoint: POST {"email": "..."} → отправка письма.
    """
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email not found"},
                            status=status.HTTP_404_NOT_FOUND)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{request.scheme}://{request.get_host()}" \
                    f"{reverse('password_reset_confirm', args=[uid, token])}"
        send_mail(
            subject="Password Reset",
            message=f"Click to reset your password:\n\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({"message": "Reset link sent to email"},
                        status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"},
                            status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
