from django.contrib import admin

# Register your models here.
from .models import ParkingPlace , PaymentDetails , ParkingDetails , VehicleType , ParkingLot , ParkingFee , User

admin.site.register(ParkingPlace)




admin.site.register(PaymentDetails)

admin.site.register(ParkingDetails)

admin.site.register(VehicleType)

admin.site.register(ParkingLot)

admin.site.register(ParkingFee)

admin.site.register(User)