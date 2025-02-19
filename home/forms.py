from django import forms
from django.forms import inlineformset_factory
from .models import (
    User, ParkingPlace, ParkingLot, PaymentDetails, ParkingFee, VehicleType , AllowedVehicleType
)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm


# ========================== USER FORMS ========================== #

class RegistrationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'User'  # ✅ Force role to be 'User'
        if not user.avatar:
            user.avatar = 'avatars/default.png'  # ✅ Set default avatar
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']


# ========================== PARKING PLACE FORM ========================== #

class ParkingPlaceForm(ModelForm):
    vehicle_types = forms.ModelMultipleChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Allowed Vehicle Types"
    )

    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location', 'capacity', 'available_spaces', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing an existing ParkingPlace, prepopulate the allowed vehicle types
        if self.instance.pk:
            self.fields['vehicle_types'].initial = self.instance.allowed_vehicle_types.values_list('vehicle_type', flat=True)

    def save(self, commit=True):
        parking_place = super().save(commit=False)

        if commit:
            parking_place.save()  # Save ParkingPlace first to get an ID

            # ✅ Fix: Ensure the Many-to-Many relation is updated on creation
            self.save_m2m()  # Ensures Django saves M2M relationships

            # ✅ Delete old AllowedVehicleType records (to avoid duplicates)
            parking_place.allowed_vehicle_types.all().delete()

            # ✅ Add new AllowedVehicleType entries
            for vehicle_type in self.cleaned_data['vehicle_types']:
                AllowedVehicleType.objects.create(parking_place=parking_place, vehicle_type=vehicle_type)

        return parking_place


# ========================== PARKING LOT FORM ========================== #

class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = ['lot_name', 'status_before', 'status_after']
        widgets = {
            'lot_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status_before': forms.TextInput(attrs={'class': 'form-control'}),
            'status_after': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ✅ Inline Formset for Parking Lots inside a Parking Place
ParkingLotFormSet = inlineformset_factory(
    ParkingPlace, ParkingLot,
    form=ParkingLotForm,
    extra=2,  # Default extra parking lots
    can_delete=True
)


# ========================== PAYMENT FORM ========================== #

class PaymentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    parking_detail = forms.ModelChoiceField(
        queryset=PaymentDetails.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount_paid = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        help_text="Enter a positive amount."
    )

    class Meta:
        model = PaymentDetails
        fields = ['user', 'parking_detail', 'amount_paid', 'payment_method', 'payment_status']


# ========================== PARKING FEE FORM ========================== #

class ParkingFeeForm(forms.ModelForm):
    parking_place = forms.ModelChoiceField(
        queryset=ParkingPlace.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Parking Place"
    )
    vehicle_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Vehicle Type"
    )
    fee = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        help_text="Enter a valid parking fee."
    )

    class Meta:
        model = ParkingFee
        fields = ['parking_place', 'vehicle_type', 'fee']
