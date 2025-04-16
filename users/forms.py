from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")

from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        user = authenticate(
            username=cleaned_data.get("username"),
            password=cleaned_data.get("password")
        )
        if not user:
            raise forms.ValidationError("Неверное имя пользователя или пароль")
        cleaned_data["user"] = user
        return cleaned_data
