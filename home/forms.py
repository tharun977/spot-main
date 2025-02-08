from django import forms
from .models import ParkingPlace, Payment

class ParkingPlaceForm(forms.ModelForm):
    class Meta:
        model = ParkingPlace
        fields = ['location', 'number_of_slots', 'available_slots']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['log', 'amount']
