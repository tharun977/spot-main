from django.db import models

# Create your models here.
class ParkingPlace(models.Model):
    place_id = models.AutoField(primary_key=True)
    place_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    capacity = models.IntegerField()
    image =  models.ImageField(upload_to='parking_images')
    
    def __str__(self):
        return self.place_name