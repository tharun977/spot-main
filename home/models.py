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
    

class ParkingPlace(models.Model):
    place_name = models.CharField(max_length=255, unique=True)  # Unique for clarity
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()  # PositiveInteger to prevent negatives
    available_spaces = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)  # True = Active, False = Inactive

    def __str__(self):
        return self.place_name


class ParkingLot(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name="lots", on_delete=models.CASCADE , null=True, blank=True
    )
    lot_name = models.CharField(max_length=50 , null=True, blank=True)  # Lot A1, B2, etc.
    status_before = models.CharField(max_length=255, null=True, blank=True)
    status_after = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.lot_name} in {self.parking_place}"


class VehicleType(models.Model):
    vehicle_type = models.CharField(max_length=50, unique=True)  # Unique to prevent duplicates
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return self.vehicle_type


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
