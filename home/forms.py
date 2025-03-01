from django import forms
from django.forms import inlineformset_factory
from .models import (
    User, ParkingPlace, ParkingLot, PaymentDetails, ParkingFee, VehicleType , ParkingDetails , validate_vehicle_number
)
from django.contrib.auth.forms import AuthenticationForm
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

class ParkingPlaceForm(forms.ModelForm):
    num_lots = forms.IntegerField(
        min_value=1, required=True, 
        label="Number of Parking Lots",
        help_text="Enter the total number of parking lots for this place."
    )
    
    class Meta:
        model = ParkingPlace
        fields = ['place_name', 'location' , 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # If editing an existing ParkingPlace
            self.fields['num_lots'].initial = self.instance.parkinglot_set.count()

    def save(self, commit=True):
        parking_place = super().save(commit=False)

        if commit:
            parking_place.save()  # Save ParkingPlace first

            # Update parking lots
            existing_lots = parking_place.parkinglot_set.all()
            new_lot_count = self.cleaned_data['num_lots']

            if new_lot_count > existing_lots.count():
                # Add new lots
                for i in range(existing_lots.count() + 1, new_lot_count + 1):
                    ParkingLot.objects.create(parking_place=parking_place, lot_number=i)

            elif new_lot_count < existing_lots.count():
                # Remove extra lots
                excess_lots = existing_lots.order_by('-lot_number')[:existing_lots.count() - new_lot_count]
                for lot in excess_lots:
                    lot.delete()

        return parking_place



# ========================== PARKING DETAILS FORM ========================== #
class ParkingDetailsForm(forms.ModelForm):
    vehicle_reg_no = forms.CharField(
        validators=[validate_vehicle_number],
        widget=forms.TextInput(attrs={"placeholder": "KL60 AB1234", "class": "form-control"})
    )

    out_time = forms.DateTimeField(
        required=False,  # ✅ Correct placement
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"]
    )

    vehicle_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select Vehicle Type"
    )

    occupied_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select User"
    )

    class Meta:
        model = ParkingDetails
        fields = [  # ❌ Removed 'in_time'
            "vehicle_reg_no", "mobile_number", "vehicle_type", 
            "out_time", "payment_status", 
            "parking_duration", "occupied_by"
        ]

# ========================== STAFF REGISTRATION FORM ========================== #

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
