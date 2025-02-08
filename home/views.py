from django.shortcuts import render
from django.http import HttpResponse

from .models import ParkingPlace

# Create your views here.
def index(request):
    return render(request, 'index.html')

def parking_place(request):
    dict_place = {
        'parking_place': ParkingPlace.objects.all() 
    }
    return render(request, 'parking_place.html', dict_place)

def about(request):
    return render(request, 'about.html')

def log(request):
    return render(request, 'log.html')

def contact(request):
    return render(request, 'contact.html')