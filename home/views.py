from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot, ParkingDetails, PaymentDetails, LogDetails, VehicleType , AllowedVehicleType
from .forms import ParkingPlaceForm, PaymentForm, UserForm   , ParkingLotFormSet

def home(request):
    return render(request, 'home.html')

from django.shortcuts import render, redirect
from .forms import ParkingPlaceForm, ParkingFeeForm
from .models import ParkingPlace, ParkingFee

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


def logs(request):
    logs = LogDetails.objects.all()
    return render(request, 'log.html', {"logs": logs})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
