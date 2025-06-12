from django.shortcuts              import render, redirect
from django.contrib.auth           import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens    import default_token_generator
from django.contrib.auth.forms     import AuthenticationForm
from django.contrib                import messages
from django.urls                   import reverse
from django.utils.http             import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding         import force_bytes
from django.core.mail              import send_mail
from django.conf                   import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework                import generics, status, serializers
from rest_framework.views          import APIView
from rest_framework.response       import Response
from rest_framework.permissions    import IsAuthenticated
from rest_framework.serializers    import CharField

from .forms       import (
    ProfileForm,
    CustomPasswordChangeForm,
    RegisterForm,
    LoginForm,
)
from .serializers import RegisterSerializer

User = get_user_model()


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {
        'user': request.user
    })


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {
        'form': form
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('profile_view')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {
        'form': form
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST) 
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('profile_view')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')



def password_reset_form_view(request):
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            link  = request.build_absolute_uri(
                reverse('password_reset_confirm_form', args=[uid, token])
            )
            send_mail(
                "Password Reset",
                f"Click here to reset your password:\n\n{link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            message = "Reset link sent to your email."
        except User.DoesNotExist:
            message = "No user found with that email."
    return render(request, 'users/password_reset_form.html', {
        'message': message
    })



def password_reset_confirm_view(request, uidb64, token):
    error = ''
    validlink = False
    user = None

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        validlink = True
    else:
        error = "The reset link is invalid or has expired."

    if validlink and request.method == 'POST':
        new_pwd = request.POST.get('new_password')
        try:
            validate_password(new_pwd, user=user)
            user.set_password(new_pwd)
            user.save()
            login(request, user)
            return redirect('profile_view')
        except Exception as e:
            error = " ".join(e.messages) if hasattr(e, 'messages') else str(e)

    return render(request, 'users/password_reset_confirm.html', {
        'error': error,
        'validlink': validlink
    })


# ——— API Views ——— #

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileAPIView(APIView):
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Auth credentials not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        u = request.user
        return Response({
            'username':   u.username,
            'email':      u.email,
            'first_name': u.first_name,
            'last_name':  u.last_name,
        })


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        old_password = CharField(required=True)
        new_password = CharField(required=True)

    def post(self, request):
        user = request.user
        ser  = self.InputSerializer(data=request.data)
        if ser.is_valid():
            if not user.check_password(ser.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                validate_password(ser.validated_data['new_password'], user)
            except Exception as e:
                return Response({'error': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(ser.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed.'})
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        token = default_token_generator.make_token(u)
        uid   = urlsafe_base64_encode(force_bytes(u.pk))
        link  = request.build_absolute_uri(
            reverse('password_reset_confirm_form', args=[uid, token])
        )
        send_mail("Password Reset", f"Click to reset:\n\n{link}",
                  settings.DEFAULT_FROM_EMAIL, [email])
        return Response({'message': 'Reset link sent'})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        rt = request.data.get('refresh')
        RefreshToken(rt).blacklist()
        return Response({'message': 'Logged out'},
                        status=status.HTTP_205_RESET_CONTENT)
