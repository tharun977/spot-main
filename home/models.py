from django.db import models

class ParkingPlace(models.Model):
    location = models.CharField(max_length=100)
    number_of_slots = models.IntegerField()
    available_slots = models.IntegerField()

    def __str__(self):
        return f"{self.location} ({self.available_slots}/{self.number_of_slots})"

class Log(models.Model):
    parking_place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Vehicle {self.vehicle_number} at {self.parking_place.location}"

class Payment(models.Model):
    log = models.OneToOneField(Log, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.log.vehicle_number}"
