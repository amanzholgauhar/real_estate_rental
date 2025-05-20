import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Booking, Property


def max_size_validator(limit_value):
    """
    Returns a validator that ensures uploaded file is not larger than limit_value bytes.
    """
    def validator(value):
        size_mb = limit_value / (1024 * 1024)
        if value.size > limit_value:
            raise ValidationError(
                f"The file size must not exceed {size_mb:.2f} MB."
            )
    return validator


class PropertyForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
            max_size_validator(10 * 1024 * 1024),
        ],
    )

    class Meta:
        model = Property
        fields = [
            "title",
            "description",
            "price",
            "location",
            "phone_number",
            "image",
        ]
        help_texts = {
            "phone_number": "Enter phone number in format +77171234567 or 77171234567",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # общие атрибуты для всех полей
        for field in self.fields.values():
            field.widget.attrs.update(
                {"class": "w-full px-3 py-2 border border-black rounded"}
            )

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None or price <= 0:
            raise ValidationError("Price must be a positive number.")
        return price

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if phone and not re.match(r"^\+?\d{7,20}$", phone):
            raise ValidationError("Phone number format is incorrect.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        description = cleaned_data.get("description")
        if not title or not description:
            raise ValidationError("Title and description are required.")
        return cleaned_data


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["property", "status"]
        widgets = {
            "status": forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # скрываем поле с объявлением (оно передаётся через GET)
        self.fields["property"].widget = forms.HiddenInput()
        # класс для select
        self.fields["status"].widget.attrs.update(
            {
                "class": (
                    "mt-1 w-full px-3 py-2 "
                    "border border-gray-300 rounded-lg "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500"
                )
            }
        )
