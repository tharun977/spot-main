from django.db import models
from django.utils import timezone  # To set default timestamps

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50, choices=[('Admin', 'Admin'), ('User', 'User')]
    )

    def __str__(self):
        return self.username
    

from django.db import models

class ParkingPlace(models.Model):
    place_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    available_spaces = models.IntegerField(default=0)
    status = models.BooleanField(default=True)  # Active/Inactive

    def __str__(self):
        return self.place_name

class ParkingLot(models.Model):
    parking_place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, related_name="lots" ,null=True)
    lot_name = models.CharField(max_length=50 , null=True)  # Example: "A1", "B2"
    status = models.BooleanField(default=True)  # Available/Occupied

    def __str__(self):
        return f"{self.lot_name} ({self.parking_place})"

class VehicleType(models.Model):
    vehicle_type = models.CharField(max_length=50)

    def __str__(self):
        return self.vehicle_type

class AllowedVehicleType(models.Model):
    parking_place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, related_name="allowed_vehicle_types")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('parking_place', 'vehicle_type')

    def __str__(self):
        return f"{self.vehicle_type} allowed in {self.parking_place}"


class ParkingDetails(models.Model):
    place_id = models.ForeignKey(
        ParkingPlace, related_name="parking_details", on_delete=models.CASCADE
    )
    lot_id = models.ForeignKey(
        ParkingLot, related_name="parking_details", on_delete=models.CASCADE
    )
    vehicle_reg_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    vehicle_type_id = models.ForeignKey(
        VehicleType, related_name="parked_vehicles", on_delete=models.CASCADE
    )
    in_time = models.DateTimeField(default=timezone.now)  # Ensures accurate entry timestamps
    out_time = models.DateTimeField(null=True, blank=True)
    parking_duration = models.DurationField(null=True, blank=True)
    occupied_by = models.ForeignKey(
        User, related_name="parking_records", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Parking at {self.place_id} by {self.occupied_by}"


class ParkingFee(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name="fees", on_delete=models.CASCADE
    )
    vehicle_type = models.ForeignKey(
        VehicleType, related_name="fees", on_delete=models.CASCADE
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('parking_place', 'vehicle_type')  # Prevents duplicate entries

    def __str__(self):
        return f"{self.parking_place} - {self.vehicle_type}: ₹{self.fee}"


class PaymentDetails(models.Model):
    user_id = models.ForeignKey(
        User, related_name="payments", on_delete=models.CASCADE
    )
    parking_id = models.ForeignKey(
        ParkingDetails, related_name="payments", on_delete=models.CASCADE
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=50, choices=[('Card', 'Card'), ('Cash', 'Cash'), ('Online', 'Online')]
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=True)  # True = Completed, False = Pending

    class Meta:
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment by {self.user_id} - ₹{self.amount_paid}"


class LogDetails(models.Model):
    user_id = models.ForeignKey(
        User, related_name="logs", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log: {self.user_id} - {self.timestamp}"
