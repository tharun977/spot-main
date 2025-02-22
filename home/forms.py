from django import forms
from django.forms import inlineformset_factory
from .models import (
    User, ParkingPlace, ParkingLot, PaymentDetails, ParkingFee, VehicleType , AllowedVehicleType
)
from django.contrib.auth.forms import  AuthenticationForm
from django.forms import ModelForm
from django.contrib.auth import authenticate


# ========================== USER FORMS ========================== #


class LoginForm(AuthenticationForm):
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")
        else:
            raise forms.ValidationError("Invalid username or password.")

        return cleaned_data


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


class StaffRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)  # ✅ Allow empty avatar

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # ✅ Hash password
        user.is_staff = True  # ✅ Mark as staff user
        user.is_superuser = False  # ✅ Ensure it's not an admin

        if not self.cleaned_data.get('avatar'):
            user.avatar = 'static/images/default_user.png'  # ✅ Set default avatar

        if commit:
            user.save()

        return user
    

# ========================== PARKING LOT FORM ========================== #

class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = ['lot_name', 'vehicle_number', 'status_before', 'status_after']
        widgets = {
            'lot_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYBH####XX'}),
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
