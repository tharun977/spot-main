from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot, ParkingDetails, PaymentDetails, LogDetails, VehicleType ,AllowedVehicleType
from .forms import ParkingPlaceForm, PaymentForm, UserForm   , ParkingLotFormSet

def home(request):
    return render(request, 'home.html')

from django.shortcuts import render, redirect
from .forms import ParkingPlaceForm, ParkingFeeForm
from .models import ParkingPlace, ParkingFee

def manage_parking_places(request):
    if request.method == "POST":
        place_form = ParkingPlaceForm(request.POST)
        lot_formset = ParkingLotFormSet(request.POST)

        if place_form.is_valid() and lot_formset.is_valid():
            parking_place = place_form.save()

            # Save allowed vehicle types
            for vehicle_type in place_form.cleaned_data['allowed_vehicle_types']:
                AllowedVehicleType.objects.create(parking_place=parking_place, vehicle_type=vehicle_type)

            # Save parking lots
            lots = lot_formset.save(commit=False)
            for lot in lots:
                lot.parking_place = parking_place
                lot.save()

            return redirect('manage_parking_places')

    else:
        place_form = ParkingPlaceForm()
        lot_formset = ParkingLotFormSet()

    parking_places = ParkingPlace.objects.all()

    return render(request, 'manage_parking_places.html', {
        'place_form': place_form,
        'lot_formset': lot_formset,
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
            form.save()
            return redirect('manage_parking_places')
    else:
        form = ParkingPlaceForm(instance=parking_place)
    
    return render(request, 'edit_parking_place.html', {'form': form})

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
