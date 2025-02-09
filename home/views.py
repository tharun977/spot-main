from django.shortcuts import render, redirect, get_object_or_404
from .models import User, ParkingPlace, ParkingLot, ParkingDetails, PaymentDetails, LogDetails, VehicleType
from .forms import ParkingPlaceForm, PaymentForm, VehicleTypeForm, UserForm  # Ensure UserForm exists

def home(request):
    return render(request, 'home.html')

def parking_places(request):
    if request.method == "POST":
        form = ParkingPlaceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('parking_places')
    else:
        form = ParkingPlaceForm()

    parking_places = ParkingPlace.objects.all()
    
    return render(request, 'parking_place.html', {
        "form": form, 
        "parking_places": parking_places
    })

def delete_parking_place(request, pk):
    parking_place = get_object_or_404(ParkingPlace, pk=pk)
    parking_place.delete()
    return redirect('parking_places')

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
