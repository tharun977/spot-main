from genericpath import exists
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot , PaymentDetails, VehicleType, AllowedVehicleType, ParkingFee , ParkingDetails
from .forms import ParkingPlaceForm , ParkingFeeForm, LoginForm, ProfileUpdateForm,  StaffRegistrationForm , ParkingDetailsForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.timezone import now
from datetime import datetime 
from django.utils.timezone import make_aware
from django.db.models import OuterRef, Exists
import uuid

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
        form = ParkingPlaceForm(request.POST)
        if form.is_valid():
            form.save()  # Parking place + lots are created
            return redirect('manage_parking_places')
    else:
        form = ParkingPlaceForm()

    parking_places = ParkingPlace.objects.all()
    return render(request, 'manage_parking_places.html', {
        'place_form': form,
        'parking_places': parking_places,
    })



@login_required
# Show parking details when a lot is clicked
def parking_lot_details(request, lot_id):  
    parking_lot = get_object_or_404(ParkingLot, id=lot_id)  # Ensure ID is an integer
    parking_details = ParkingDetails.objects.filter(parking_lot=parking_lot)
    vehicle_types = VehicleType.objects.all()

    return render(request, 'parking_lot_details.html', {
        "parking_lot": parking_lot,
        "parking_details": parking_details,
        "vehicle_types": vehicle_types
    })


# Add parking entry linked to a parking lot
@login_required
def add_parking(request, lot_id):
    parking_lot = get_object_or_404(ParkingLot, id=lot_id)  # Fetch parking lot instance
    vehicle_types = VehicleType.objects.all()  # Fetch all vehicle types

    if request.method == 'POST':
        vehicle_reg_no = request.POST.get('vehicle_reg_no')
        mobile_number = request.POST.get('mobile_number')
        vehicle_type_id = request.POST.get('vehicle_type_id')
        occupied_by = request.POST.get('occupied_by')

        # ✅ Check if `vehicle_type_id` exists
        try:
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
        except VehicleType.DoesNotExist:
            return render(request, 'add_parking.html', {
                'parking_lot': parking_lot,
                'vehicle_types': vehicle_types,
                'error': "Selected Vehicle Type does not exist."
            })

        # ✅ Create Parking Entry

        ParkingDetails.objects.create(
            parking_lot=parking_lot,
            vehicle_reg_no=vehicle_reg_no,
            mobile_number=mobile_number,
            vehicle_type=vehicle_type,
            occupied_by=occupied_by,
            authorized_by=request.user,
            payment_amount=0.00  # Add this line to prevent the NULL error
        )

        return redirect('parking_lot_details', lot_id=lot_id)

    # ✅ Ensure `vehicle_types` is passed to the template
    return render(request, 'add_parking.html', {
        'parking_lot': parking_lot,
        'vehicle_types': vehicle_types
    })



# Checkout a vehicle
def checkout_parking(request, parking_id):
    parking = get_object_or_404(ParkingDetails, parking_id=parking_id)

    if not parking.out_time:
        parking.checkout()
        
        # Increase available spots in the parking lot
        parking.parking_lot.available_spots += 1
        parking.parking_lot.save()

    return redirect('parking_lot_details', lot_id=parking.parking_lot.id)



@login_required
def edit_parking_place(request, pk):
    
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    
    if request.method == "POST":
        form = ParkingPlaceForm(request.POST, instance=parking_place)
        if form.is_valid():
            form.save()
            return redirect("manage_parking_places")
    else:
        form = ParkingPlaceForm(instance=parking_place)

    return render(request, "edit_parking_place.html", {"form": form})



@login_required
def delete_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    if request.method == "POST":
        parking_place.delete()
        return redirect('manage_parking_places')
    
@login_required
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

@login_required
def edit_parking_fee(request, pk):
    parking_fee = get_object_or_404(ParkingFee, pk=pk)
    
    if request.method == "POST":
        form = ParkingFeeForm(request.POST, instance=parking_fee)
        if form.is_valid():
            form.save()
            return redirect('manage_parking_fees')
    else:
        form = ParkingFeeForm(instance=parking_fee)
    
    return render(request, 'edit_parking_fee.html', {'form': form})

@login_required
def delete_parking_fee(request, pk):
    parking_fee = get_object_or_404(ParkingFee, pk=pk)

    if request.method == "POST":
        parking_fee.delete()
        messages.success(request, "Parking fee deleted successfully!")
        return redirect('manage_parking_fees')  # Redirect after deletion

    return render(request, 'delete_parking_fee.html', {'parking_fee': parking_fee})

# ========================== PARKING LOTS ========================== #

@login_required
def parking_lot_list(request, parking_place_id):
    parking_place = get_object_or_404(ParkingPlace, id=parking_place_id)
    
    # Get parking lots with occupancy status annotation
    parking_lots = ParkingLot.objects.filter(parking_place=parking_place).annotate(
        is_occupied=Exists(
            ParkingDetails.objects.filter(
                parking_lot=OuterRef('pk'),
                out_time__isnull=True
            )
        )
    )
    
    # Get allowed vehicle types (from your original code)
    allowed_vehicle_types = AllowedVehicleType.objects.filter(
        parking_place=parking_place
    ).select_related('vehicle_type')
    
    # Add the return statement with context
    return render(request, 'parking_lot_list.html', {
        'parking_place': parking_place,
        'parking_lots': parking_lots,
        'allowed_vehicle_types': allowed_vehicle_types
    })

@login_required
def delete_parking_lots(request, parking_place_id):
    parking_place = get_object_or_404(ParkingPlace, id=parking_place_id)
    parking_lots = ParkingLot.objects.filter(parking_place=parking_place)

    if request.method == "POST":
        selected_lots = request.POST.getlist('selected_lots')
        ParkingLot.objects.filter(id__in=selected_lots).delete()
        return redirect('parking_lot_list', parking_place_id=parking_place_id)

    return render(request, 'delete_parking_lots.html', {'parking_place': parking_place, 'parking_lots': parking_lots})

@login_required
def add_multiple_parking_lots(request, parking_place_id):
    parking_place = get_object_or_404(ParkingPlace, pk=parking_place_id)

    if request.method == "POST":
        try:
            num_lots = int(request.POST.get("num_lots", 0))  # Get the number of lots from form
            last_lot = ParkingLot.objects.filter(parking_place=parking_place).order_by('-lot_number').first()
            start_number = last_lot.lot_number + 1 if last_lot else 1

            for i in range(num_lots):
                ParkingLot.objects.create(parking_place=parking_place, lot_number=start_number + i)

            messages.success(request, f"✅ {num_lots} parking lots added successfully!")
        except ValueError:
            messages.error(request, "❌ Invalid input! Please enter a valid number.")

        return redirect('parking_lot_list', parking_place_id=parking_place.pk)

    return render(request, 'add_parking_lots.html', {'parking_place': parking_place})





def update_out_time(request, parking_id):
    if request.method == 'POST':
        parking_detail = get_object_or_404(ParkingDetails, parking_id=parking_id)

        out_time_str = request.POST.get('out_time')
        if not out_time_str:
            messages.error(request, "Out time is required.")
            return redirect('parking_lot_details', lot_id=parking_detail.parking_lot.id)

        try:
            # Convert the naive datetime to an aware datetime
            naive_out_time = datetime.strptime(out_time_str.replace('T', ' '), "%Y-%m-%d %H:%M")
            out_time = make_aware(naive_out_time)  # Convert to timezone-aware datetime

            # Ensure in_time is also timezone-aware
            if parking_detail.in_time and out_time <= parking_detail.in_time:
                messages.error(request, "Out time must be later than In time.")
                return redirect('parking_lot_details', lot_id=parking_detail.parking_lot.id)

            parking_detail.out_time = out_time
            duration = (out_time - parking_detail.in_time).total_seconds() / 60  # Convert to minutes
            parking_detail.parking_duration = duration
            parking_detail.save()

            messages.success(request, "Out time updated successfully.")

        except ValueError:
            messages.error(request, "Invalid date format. Please select a valid date and time.")

    return redirect('parking_lot_details', lot_id=parking_detail.parking_lot.id)



@login_required
def make_payment(request, parking_id):
    parking_detail = get_object_or_404(ParkingDetails, parking_id=parking_id)

    if request.method == "POST":
        selected_payment_method = request.POST.get("payment_method")

        if selected_payment_method:
            # Mark payment as completed
            parking_detail.payment_status = True
            parking_detail.save()
            
            messages.success(request, "Payment successful! Your parking record has been updated.")
            return redirect("parking_lot_details", lot_id=parking_detail.parking_lot.id)

        else:
            messages.error(request, "Please select a payment method.")

    return render(request, "payment_portal.html", {"parking_detail": parking_detail})



@login_required
def delete_parking(request, parking_id):
    parking_detail = get_object_or_404(ParkingDetails, parking_id=parking_id)
    parking_detail.delete()
    messages.success(request, "Parking record deleted successfully.")
    return redirect('parking_details')

# ========================== PAYMENTS & LOGS ========================== #

@login_required
def payments(request):
    payments = PaymentDetails.objects.all()
    return render(request, 'payments.html', {"payments": payments})



def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')