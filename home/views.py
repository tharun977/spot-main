from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot, ParkingDetails, PaymentDetails, LogDetails, VehicleType , AllowedVehicleType , ParkingFee
from .forms import ParkingPlaceForm, PaymentForm   , ParkingLotFormSet , ParkingFeeForm , RegistrationForm , LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout , get_user_model
from django.views.decorators.csrf import csrf_protect  
from django.contrib.auth.decorators import login_required, user_passes_test  
from django.contrib import messages  # Import Django messages framework
from .forms import ProfileUpdateForm , LoginForm , ParkingLotForm


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome, " + user.username)
            return redirect('user_dashboard')  # ✅ Redirect after successful registration
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})



User = get_user_model()  # Ensures we use home.User

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"✅ Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "❌ Invalid username or password")
        else:
            messages.error(request, "❌ Form validation failed")
    
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def settings(request):
    return render(request, 'settings.html')  # ✅ Ensure 'settings.html' exists


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# Utility functions to check user roles
def is_staff(user):
    return user.is_authenticated and user.role == "Staff"

def is_user(user):
    return user.is_authenticated and user.role == "User"

def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Admin Dashboard (No changes required)
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Staff Dashboard
@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    parking_places = ParkingPlace.objects.all()  # Read-only view
    parking_fees = ParkingFee.objects.all()  # Editable

    if request.method == "POST":
        fee_id = request.POST.get("fee_id")
        new_fee = request.POST.get("new_fee")
        if fee_id and new_fee:
            fee = ParkingFee.objects.get(id=fee_id)
            fee.fee = new_fee
            fee.save()

    return render(request, 'staff_dashboard.html', {
        'parking_places': parking_places,
        'parking_fees': parking_fees,
    })

# User Dashboard
@login_required
@user_passes_test(is_user)
def user_dashboard(request):
    parking_fees = ParkingFee.objects.all()  # Read-only
    payments = PaymentDetails.objects.filter(user_id=request.user)

    return render(request, 'user_dashboard.html', {
        'parking_fees': parking_fees,
        'payments': payments,
    })


def home(request):
    return render(request, 'home.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})

def manage_parking_places(request):
    if request.method == "POST":
        place_form = ParkingPlaceForm(request.POST)

        if place_form.is_valid():
            parking_place = place_form.save()
            return redirect('manage_parking_places')

    else:
        place_form = ParkingPlaceForm()

    parking_places = ParkingPlace.objects.all()

    return render(request, 'manage_parking_places.html', {
        'place_form': place_form,
        'parking_places': parking_places
    })


def parking_place_detail(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    parking_fees = ParkingFee.objects.filter(place=parking_place)

    return render(request, 'parking_place_detail.html', {
        'parking_place': parking_place,
        'parking_fees': parking_fees
    })


def manage_parking_fees(request):
    """ View for managing parking fees separately """
    if request.method == 'POST':
        fee_form = ParkingFeeForm(request.POST)
        if fee_form.is_valid():
            fee_form.save()
            return redirect('manage_parking_fees')
    else:
        fee_form = ParkingFeeForm()

    parking_fees = ParkingFee.objects.all()

    return render(
        request, 
        'manage_parking_fees.html', 
        {'fee_form': fee_form, 'parking_fees': parking_fees}
    )


def edit_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)

    if request.method == "POST":
        form = ParkingPlaceForm(request.POST, instance=parking_place)
        if form.is_valid():
            parking_place = form.save(commit=False)
            parking_place.save()

            # **Fix: Correctly update allowed vehicle types**
            AllowedVehicleType.objects.filter(parking_place=parking_place).delete()
            for vehicle_type in form.cleaned_data['vehicle_types']:
                AllowedVehicleType.objects.create(parking_place=parking_place, vehicle_type=vehicle_type)

            return redirect('manage_parking_places')

    else:
        # Preload existing vehicle types
        existing_vehicle_types = parking_place.allowed_vehicle_types.values_list('vehicle_type', flat=True)
        form = ParkingPlaceForm(instance=parking_place, initial={'vehicle_types': existing_vehicle_types})

    return render(request, 'edit_parking_place.html', {'form': form, 'parking_place': parking_place})



def delete_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    if request.method == "POST":
        parking_place.delete()
        return redirect('manage_parking_places')

def payments(request):
    payments = PaymentDetails.objects.all()
    return render(request, 'payments.html', {"payments": payments})



# ✅ View all parking lots inside a parking place
def parking_lot_list(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    parking_lots = ParkingLot.objects.filter(parking_place=parking_place)
    return render(request, 'parking_lot_list.html', {'parking_place': parking_place, 'parking_lots': parking_lots})

# ✅ Add a new parking lot
def add_parking_lot(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    if request.method == 'POST':
        form = ParkingLotForm(request.POST)
        if form.is_valid():
            parking_lot = form.save(commit=False)
            parking_lot.parking_place = parking_place  # Assign the parking place
            parking_lot.save()
            return redirect('parking_lot_list', pk=pk)
    else:
        form = ParkingLotForm()
    return render(request, 'add_parking_lot.html', {'form': form, 'parking_place': parking_place})

# ✅ Edit an existing parking lot
def edit_parking_lot(request, lot_pk):
    parking_lot = get_object_or_404(ParkingLot, pk=lot_pk)
    if request.method == 'POST':
        form = ParkingLotForm(request.POST, instance=parking_lot)
        if form.is_valid():
            form.save()
            return redirect('parking_lot_list', pk=parking_lot.parking_place.pk)
    else:
        form = ParkingLotForm(instance=parking_lot)
    return render(request, 'edit_parking_lot.html', {'form': form, 'parking_lot': parking_lot})

# ✅ Delete a parking lot
def delete_parking_lot(request, lot_pk):
    parking_lot = get_object_or_404(ParkingLot, pk=lot_pk)
    parking_lot.delete()
    return redirect('parking_lot_list', pk=parking_lot.parking_place.pk)



def logs(request):
    logs = LogDetails.objects.all()
    return render(request, 'log.html', {"logs": logs})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
