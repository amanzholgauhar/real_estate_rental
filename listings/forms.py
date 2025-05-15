from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Property, Booking

# Ограничение по размеру файла (например, 10 MB)
def MaxSizeValidator(limit_value):
    def validator(value):
        if value.size > limit_value:
            raise ValidationError(f"Размер файла не должен превышать {limit_value / (1024 * 1024)} MB")
    return validator

# Форма для объявления
class PropertyForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),  # Ограничиваем типы изображений
            MaxSizeValidator(10 * 1024 * 1024)  # Ограничение по размеру (10 MB)
        ]
    )

    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'image']

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        description = cleaned_data.get("description")

        if not title or not description:
            raise forms.ValidationError("Заголовок и описание должны быть заполнены.")
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['property', 'status']
        widgets = {
            'status': forms.Select(),  # по умолчанию Select, но мы добавим attrs ниже
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # скрываем выбор property (он уже заполнен из GET)
        self.fields['property'].widget = forms.HiddenInput()
        # задаём классы для <select name="status">
        self.fields['status'].widget.attrs.update({
            'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })

