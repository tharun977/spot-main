from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError

# ========================== USER MODEL ========================== #
class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')

    groups = models.ManyToManyField(Group, related_name="user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_permissions", blank=True)

    def get_avatar(self):
        return self.avatar.url if self.avatar else '/static/images/default_user.png'

    def __str__(self):
        return f"{self.username}"

# ========================== PARKING PLACE ========================== #
class ParkingPlace(models.Model):
    place_name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    available_spaces = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)  # True = Active, False = Inactive

    def __str__(self):
        return f"{self.place_name} ({'Active' if self.status else 'Inactive'})"

# ========================== PARKING LOT ========================== #
class ParkingLot(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name='parking_lots', on_delete=models.CASCADE, null=True, blank=True
    )
    lot_name = models.CharField(max_length=50, unique=True, null=True)
    vehicle_number = models.CharField(
        max_length=12, unique=True, null=True, blank=True, help_text="Format: YYBH####XX"
    )
    status = models.BooleanField(default=False)  # False = Available, True = Occupied
    status_before = models.CharField(max_length=255, null=True, blank=True)
    status_after = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.lot_name} in {self.parking_place} - {'Occupied' if self.status else 'Available'}"

# ========================== VEHICLE TYPE ========================== #
class VehicleType(models.Model):
    vehicle_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.vehicle_type

# ========================== ALLOWED VEHICLE TYPE ========================== #
class AllowedVehicleType(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name="allowed_vehicle_types", on_delete=models.CASCADE
    )
    vehicle_type = models.ForeignKey(
        VehicleType, related_name="allowed_in_places", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('parking_place', 'vehicle_type')

    def __str__(self):
        return f"{self.vehicle_type} allowed in {self.parking_place}"

# ========================== VEHICLE NUMBER VALIDATION ========================== #
def validate_vehicle_number(value):
    pattern = r'^[A-Z]{2}[A-Z0-9]{2}[0-9]{4}[A-Z0-9]{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid vehicle number format. It should be in the format YYBH####XX.')

# ========================== PARKING DETAILS ========================== #
class ParkingDetails(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name="parking_details", on_delete=models.CASCADE
    )
    parking_lot = models.ForeignKey(
        ParkingLot, related_name="parking_details", on_delete=models.CASCADE
    )
    vehicle_reg_no = models.CharField(
        max_length=12, unique=True, null=True, blank=True, validators=[validate_vehicle_number]
    )
    vehicle_type = models.ForeignKey(
        VehicleType, related_name="parked_vehicles", on_delete=models.CASCADE
    )
    in_time = models.DateTimeField(default=timezone.now)
    out_time = models.DateTimeField(null=True, blank=True)
    parking_duration = models.DurationField(null=True, blank=True)
    occupied_by = models.ForeignKey(
        User, related_name="parking_records", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.vehicle_reg_no or 'Unknown'} at {self.parking_place}"

# ========================== PARKING FEE ========================== #
class ParkingFee(models.Model):
    parking_place = models.ForeignKey(
        ParkingPlace, related_name="fees", on_delete=models.CASCADE
    )
    vehicle_type = models.ForeignKey(
        VehicleType, related_name="fees", on_delete=models.CASCADE
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('parking_place', 'vehicle_type')

    def __str__(self):
        return f"{self.parking_place} - {self.vehicle_type}: ₹{self.fee}"

# ========================== PAYMENT DETAILS ========================== #
class PaymentDetails(models.Model):
    PAYMENT_METHODS = [
        ('Card', 'Card'),
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    ]

    user = models.ForeignKey(
        User, related_name="payments", on_delete=models.CASCADE
    )
    parking_detail = models.OneToOneField(  # Ensuring only 1 payment per parking detail
        ParkingDetails, related_name="payment", on_delete=models.CASCADE, null=True, blank=True
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"₹{self.amount_paid} - {self.user}"

# ========================== LOG DETAILS ========================== #
class LogDetails(models.Model):
    user = models.ForeignKey(
        User, related_name="logs", on_delete=models.CASCADE
    )
    action = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.timestamp} - {self.action}"
