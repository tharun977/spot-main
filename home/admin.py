from django.contrib import admin

# Register your models here.
from .models import ParkingPlace , LogDetails , PaymentDetails , ParkingDetails , VehicleType , ParkingLot , ParkingFee

admin.site.register(ParkingPlace)


admin.site.register(LogDetails)


admin.site.register(PaymentDetails)

admin.site.register(ParkingDetails)

admin.site.register(VehicleType)

admin.site.register(ParkingLot)

admin.site.register(ParkingFee)