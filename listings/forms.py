
import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Property, Booking

def MaxSizeValidator(limit_value):
    def validator(value):
        if value.size > limit_value:
            raise ValidationError(f"The file size must not exceed {limit_value/(1024*1024)} MB")
    return validator

class PropertyForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg','jpeg','png']),
            MaxSizeValidator(10*1024*1024),
        ]
    )

    class Meta:
        model = Property
        fields = ['title','description','price','location','phone_number','image']
        help_texts = {
            'phone_number': ': +77171234567 or 77171234567',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fld in self.fields.values():
            fld.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-black rounded'
            })

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price <= 0:
            raise ValidationError("The price should be possitive")
        return price

    def clean_phone_number(self):
        phone = (self.cleaned_data.get('phone_number') or '').strip()
        if phone and not re.match(r'^\+?\d{7,20}$', phone):
            raise ValidationError("Incorrect format.")
        return phone

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('title') or not cleaned.get('description'):
            raise ValidationError("The title and description are required.")
        return cleaned


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['property','status']
        widgets = {'status': forms.Select()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].widget = forms.HiddenInput()
        self.fields['status'].widget.attrs.update({
            'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
