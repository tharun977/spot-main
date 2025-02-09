from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('User', 'User')])

    def __str__(self):
        return self.username
    

class ParkingPlace(models.Model):
    place_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    available_spaces = models.IntegerField(default=0)  # Added field
    status = models.BooleanField(default=True)  # Active/Inactive

    def __str__(self):
        return self.place_name

class ParkingLot(models.Model):
    parking_id = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE)
    status_before = models.CharField(max_length=255)
    status_after = models.CharField(max_length=255)

class VehicleType(models.Model):
    vehicle_type_id = models.AutoField(primary_key=True)
    vehicle_reg_no = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.vehicle_type} ({self.vehicle_reg_no})"

class ParkingDetails(models.Model):
    place_id = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE)
    lot_id = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    vehicle_type_id = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    in_time = models.DateTimeField(auto_now_add=True)
    out_time = models.DateTimeField(null=True, blank=True)
    parking_duration = models.DurationField(null=True, blank=True)
    occupied_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Parking {self.place_id} - {self.occupied_by}"

class PaymentDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_id = models.ForeignKey(ParkingDetails, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('Card', 'Card'), ('Cash', 'Cash'), ('Online', 'Online')])
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=True)  # Completed/Pending

    def __str__(self):
        return f"Payment by {self.user_id} - {self.amount_paid}"

class LogDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log: {self.user_id} - {self.timestamp}"
