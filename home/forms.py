from django import forms
from django.forms import inlineformset_factory
from .models import User, ParkingPlace, PaymentDetails, ParkingFee, ParkingLot, VehicleType

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'full_name', 'mobile_number', 'email', 'role']

class ParkingPlaceForm(forms.ModelForm):
    lots = forms.CharField(
        required=False, 
        help_text="Enter lot names separated by commas (e.g., A1, B2, C3)"
    )
    vehicle_types = forms.ModelMultipleChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status', 'vehicle_types']

    def save(self, commit=True):
        parking_place = super().save(commit=False)

        if commit:
            parking_place.save()  # ✅ Save parking place before adding related data

            # ✅ Save Parking Lots
            parking_place.lots.all().delete()  # Remove old lots
            lot_names = self.cleaned_data['lots'].split(',')
            for lot_name in lot_names:
                lot_name = lot_name.strip()
                if lot_name:
                    ParkingLot.objects.create(
                        parking_id=parking_place,
                        lot_name=lot_name,
                        status_before="Available",
                        status_after="Available"
                    )

            # ✅ Fix Vehicle Types Updating
            if hasattr(parking_place, 'vehicle_types'):
                parking_place.vehicle_types.set(self.cleaned_data['vehicle_types'])  # ✅ Correctly update ManyToManyField

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
