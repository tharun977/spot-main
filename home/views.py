from django.shortcuts import render, redirect, get_object_or_404
from .models import ParkingPlace, Log, Payment
from .forms import ParkingPlaceForm, PaymentForm

def home(request):
    pages = ["home", "parking_place", "log", "about", "contact", "payments"]
    return render(request, 'home.html', {"pages": pages})


def parking_place(request):
    if request.method == "POST":
        form = ParkingPlaceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('parking_place')
    else:
        form = ParkingPlaceForm()
    parking_places = ParkingPlace.objects.all()
    return render(request, 'parking_place.html', {'form': form, 'parking_places': parking_places})

def log(request):
    logs = Log.objects.all()
    return render(request, 'log.html', {'logs': logs})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def payments(request):
    payments = Payment.objects.all()
    return render(request, 'payments.html', {'payments': payments})
