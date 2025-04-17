from django import forms
from .models import Property, Booking

# Форма для объявления
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'image']

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price

# Форма для бронирования
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['property', 'status']  # поля, которые можно выбирать вручную
