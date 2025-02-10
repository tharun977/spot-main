from django import forms
from .models import  User, ParkingPlace, PaymentDetails , ParkingFee

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'mobile_number', 'email', 'role']

class ParkingPlaceForm(forms.ModelForm):
    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status']  # Added available_spaces


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = ['user_id', 'parking_id', 'amount_paid', 'payment_method', 'payment_status']

class ParkingFeeForm(forms.ModelForm):
    class Meta:
        model = ParkingFee
        fields = ['parking_place', 'vehicle_type', 'fee']
