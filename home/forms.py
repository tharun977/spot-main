from django import forms
from django.forms import inlineformset_factory
from .models import User, ParkingPlace, PaymentDetails, ParkingFee, ParkingLot, VehicleType 

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'mobile_number', 'email', 'role']

from django import forms
from .models import ParkingPlace, VehicleType

class ParkingPlaceForm(forms.ModelForm):
    vehicle_types = forms.ModelMultipleChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Allowed Vehicle Types"
    )

    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status']

    def save(self, commit=True):
        parking_place = super().save(commit=False)

        if commit:
            parking_place.save()

            # **Fix: Update Many-to-Many Relation**
            parking_place.allowed_vehicle_types.all().delete()  # Remove old relations
            for vehicle_type in self.cleaned_data['vehicle_types']:
                parking_place.allowed_vehicle_types.create(vehicle_type=vehicle_type)

        return parking_place
    
    
# Formset for adding multiple Parking Lots dynamically
ParkingLotFormSet = inlineformset_factory(
    ParkingPlace, ParkingLot,
    fields=('lot_name',),
    extra=2,  # Default extra parking lots
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
