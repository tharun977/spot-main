from django import forms 
from django.forms import inlineformset_factory
from .models import  User, ParkingPlace, PaymentDetails , ParkingFee ,ParkingLot, AllowedVehicleType, VehicleType

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'mobile_number', 'email', 'role']

class ParkingPlaceForm(forms.ModelForm):
    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status']  # Added available_spaces

class ParkingPlaceForm(forms.ModelForm):
    allowed_vehicle_types = forms.ModelMultipleChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status', 'allowed_vehicle_types']

# Create formset to allow multiple parking lots to be added dynamically
ParkingLotFormSet = inlineformset_factory(
    ParkingPlace, ParkingLot,
    fields=('lot_name', 'status'),
    extra=2,  # Allows adding 2 parking lots by default
    can_delete=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = ['user_id', 'parking_id', 'amount_paid', 'payment_method', 'payment_status']

class ParkingFeeForm(forms.ModelForm):
    class Meta:
        model = ParkingFee
        fields = ['parking_place', 'vehicle_type', 'fee']
