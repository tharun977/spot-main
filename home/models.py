from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError
import uuid
from home.validators import validate_vehicle_number
from django.utils.timezone import now
from datetime import timedelta
from django.utils.timezone import is_aware, make_aware

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
    status = models.BooleanField(default=True)  # True = Active, False = Inactive

    def __str__(self):
        return f"{self.place_name} ({'Active' if self.status else 'Inactive'})"

    def total_parking_lots(self):
        return self.parkinglot_set.count()  # Get total lots linked to this place



# ========================== PARKING LOT ========================== #
class ParkingLot(models.Model):
    id = models.AutoField(primary_key=True)  # Use AutoField instead of UUIDField
    parking_place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, null=True)
    lot_number = models.PositiveIntegerField(null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.BooleanField(default=False)  # False = Available, True = Occupied
    def __str__(self):
        place_name = self.parking_place.place_name if self.parking_place else "No Place Assigned"
        return f"Parking Lot {self.lot_number} - {place_name}"
    

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

# # ========================== VEHICLE NUMBER VALIDATION ========================== #
# def validate_vehicle_number(value):
#     pattern = r'^[A-Z]{2}[A-Z0-9]{2}[0-9]{4}[A-Z0-9]{2}$'
#     if not re.match(pattern, value):
#         raise ValidationError('Invalid vehicle number format. It should be in the format YYBH####XX.')

# ========================== PARKING DETAILS ========================== #
class ParkingDetails(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="parking_sessions")
    parking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    vehicle_reg_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=True)
    in_time = models.DateTimeField(auto_now_add=True)
    out_time = models.DateTimeField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    parking_duration = models.DurationField(null=True, blank=True)  # Stores timedelta
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    occupied_by = models.CharField(max_length=255, blank=True, null=True)
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_parking_duration(self):
        """Ensure both datetimes are timezone-aware before subtraction."""
        if self.in_time and self.out_time:
            in_time = make_aware(self.in_time) if not is_aware(self.in_time) else self.in_time
            out_time = make_aware(self.out_time) if not is_aware(self.out_time) else self.out_time
            duration = out_time - in_time
            return max(duration, timedelta(0))  # Prevents negative duration
        return None

    def calculate_payment(self, rate_per_hour=10):
        """Calculate payment amount based on parking duration and rate."""
        duration = self.calculate_parking_duration()
        if duration:
            hours_parked = duration.total_seconds() / 3600  # Convert to hours
            return round(hours_parked * rate_per_hour, 2)  # Rounded to 2 decimal places
        return None

    def save(self, *args, **kwargs):
        """Auto-calculate duration and payment before saving."""
        self.parking_duration = self.calculate_parking_duration()
        self.payment_amount = self.calculate_payment()

        super().save(*args, **kwargs)

    def __str__(self):
        place_name = self.parking_lot.parking_place.place_name if self.parking_lot.parking_place else "Unknown"
        return f"{place_name} - {self.vehicle_reg_no}"

    # def checkout(self):
    #     """Marks the parking as completed and calculates duration."""
    #     if not self.out_time:
    #         self.out_time = now()
    #         self.parking_duration = self.out_time - self.in_time
    #         self.payment_status = True
    #         self.save()



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