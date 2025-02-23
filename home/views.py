from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot, ParkingDetails, PaymentDetails, VehicleType, AllowedVehicleType, ParkingFee
from .forms import ParkingPlaceForm, PaymentForm, ParkingLotFormSet, ParkingFeeForm, LoginForm, ProfileUpdateForm, ParkingLotForm, StaffRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

@login_required
def home(request):
    return render(request, 'home.html')

User = get_user_model()  # Ensures we use the custom User model

# ========================== LOGIN & LOGOUT ========================== #

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
def user_logout(request):
    logout(request)
    return redirect('login')

# ========================== DASHBOARDS ========================== #

@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only superuser (Admin) can access
def admin_dashboard(request):
    return render(request, 'home.html')

@login_required
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

# ========================== USER PROFILE ========================== #

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

@login_required
def settings(request):
    return render(request, 'settings.html')

# ========================== STAFF MANAGEMENT ========================== #

@login_required
@user_passes_test(lambda u: u.is_superuser)  # ✅ Only Admins can access
def manage_staff_users(request):
    form = StaffRegistrationForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # ✅ Ensure user is marked as staff
            user.is_superuser = False  # ✅ Prevent admin creation
            user.save()
            messages.success(request, "✅ Staff user added successfully!")
            return redirect('manage_staff_users')
        else:
            messages.error(request, "❌ Failed to create staff user. Please correct the errors below.")

    # ✅ Ensure ALL existing non-superuser staff are fetched properly
    staff_users = User.objects.filter(is_staff=True, is_superuser=False).order_by('-date_joined')

    return render(request, 'manage_staff_users.html', {'form': form, 'staff_users': staff_users})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_staff(request, staff_id):
    staff = get_object_or_404(User, pk=staff_id, is_staff=True)
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Staff details updated successfully!")
            return redirect('manage_staff_users')
    else:
        form = StaffRegistrationForm(instance=staff)

    return render(request, 'edit_staff.html', {'form': form, 'staff': staff})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_staff(request, staff_id):
    staff = get_object_or_404(User, pk=staff_id, is_staff=True)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, "✅ Staff user deleted successfully!")
        return redirect('manage_staff_users')

    return render(request, 'delete_staff.html', {'staff': staff})

# ========================== PARKING PLACES ========================== #

@login_required
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

@login_required
def parking_place_detail(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    parking_fees = ParkingFee.objects.filter(parking_place=parking_place)

    return render(request, 'parking_place_detail.html', {
        'parking_place': parking_place,
        'parking_fees': parking_fees
    })

@login_required
def edit_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)

    if request.method == "POST":
        form = ParkingPlaceForm(request.POST, instance=parking_place)
        if form.is_valid():
            form.save()
            return redirect('manage_parking_places')
    else:
        form = ParkingPlaceForm(instance=parking_place)

    return render(request, 'edit_parking_place.html', {'form': form, 'parking_place': parking_place})

@login_required
def delete_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    if request.method == "POST":
        parking_place.delete()
        return redirect('manage_parking_places')
    

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


# ========================== PARKING LOTS ========================== #

@login_required
def parking_lot_list(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    parking_lots = ParkingLot.objects.filter(parking_place=parking_place)
    return render(request, 'parking_lot_list.html', {'parking_place': parking_place, 'parking_lots': parking_lots})

@login_required
def add_parking_lot(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    if request.method == 'POST':
        form = ParkingLotForm(request.POST)
        if form.is_valid():
            parking_lot = form.save(commit=False)
            parking_lot.parking_place = parking_place
            parking_lot.save()
            return redirect('parking_lot_list', pk=pk)
    else:
        form = ParkingLotForm()
    return render(request, 'add_parking_lot.html', {'form': form, 'parking_place': parking_place})

@login_required
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

@login_required
def delete_parking_lot(request, lot_pk):
    parking_lot = get_object_or_404(ParkingLot, pk=lot_pk)
    parking_lot.delete()
    return redirect('parking_lot_list', pk=parking_lot.parking_place.pk)

# ========================== PAYMENTS & LOGS ========================== #

@login_required
def payments(request):
    payments = PaymentDetails.objects.all()
    return render(request, 'payments.html', {"payments": payments})



def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
