from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        data = super().clean()
        pwd = data.get("password")
        confirm = data.get("confirm_password")

        if pwd != confirm:
            raise ValidationError("Passwords do not match.")

        if len(pwd or "") < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not any(ch.isdigit() for ch in pwd or ""):
            raise ValidationError("Password must contain at least one digit.")

        if not any(ch.isalpha() for ch in pwd or ""):
            raise ValidationError("Password must contain at least one letter.")

        return data


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput
    )

    def clean(self):
        data = super().clean()
        user = authenticate(
            username=data.get("username"), password=data.get("password")
        )

        if user is None:
            raise ValidationError("Invalid username or password.")

        if not user.is_active:
            raise ValidationError("User account is inactive.")

        data["user"] = user
        return data
