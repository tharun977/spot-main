from django.contrib.auth.models import AbstractUser , Group, Permission
from django.db import models
from django.utils import timezone


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
        ('User', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')

    groups = models.ManyToManyField(Group, related_name="user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_permissions", blank=True)

    def get_avatar(self):
        if self.role == 'Admin':
            return '/static/images/admin.png'
        return self.avatar.url if self.avatar else '/static/images/default_user.png'

    def __str__(self):
        return self.username



class ParkingPlace(models.Model):
    place_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    available_spaces = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.place_name


class ParkingLot(models.Model):  # ✅ Defined before ParkingDetails
    parking_place = models.ForeignKey(
        ParkingPlace, related_name='parking_lots', on_delete=models.CASCADE, null=True, blank=True
    )
    lot_name = models.CharField(max_length=50, unique=True, null=True)  # Ensuring unique lot names
    status_before = models.CharField(max_length=255, null=True, blank=True)
    status_after = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.lot_name} in {self.parking_place}"


class VehicleType(models.Model):
    vehicle_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.vehicle_type


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


class ParkingDetails(models.Model):  # ✅ Now `ParkingLot` is defined before this
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
    in_time = models.DateTimeField(default=timezone.now)
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
        unique_together = ('parking_place', 'vehicle_type')

    def __str__(self):
        return f"{self.parking_place} - {self.vehicle_type}: ₹{self.fee}"


class PaymentDetails(models.Model):
    user_id = models.ForeignKey(
        User, related_name="payments", on_delete=models.CASCADE
    )
    parking_id = models.OneToOneField(  # ✅ Changed to OneToOneField
        ParkingDetails, related_name="payments", on_delete=models.CASCADE
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=50, choices=[('Card', 'Card'), ('Cash', 'Cash'), ('Online', 'Online')]
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=True)

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
