from django.db import models
from django.utils import timezone
import uuid


class Vehicle(models.Model):

    VEHICLE_TYPES = [
        ('truck', 'Truck'),
        ('personal_car', 'Personal Car'),
        ('taxi', 'Taxi'),
        ('coaster', 'Coaster'),
        ('boda_boda', 'Boda-boda'),
    ]

    STATUS = [
        ('parked', 'Parked'),
        ('signed_out', 'Signed Out'),
    ]

    driver_name  = models.CharField(max_length=200)
    phone        = models.CharField(max_length=20)
    plate        = models.CharField(max_length=10)          
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model        = models.CharField(max_length=100, blank=True)
    color        = models.CharField(max_length=50, blank=True)
    nin          = models.CharField(max_length=20, blank=True)
    arrival_time = models.DateTimeField()
    status       = models.CharField(max_length=20, choices=STATUS, default='parked')

    def __str__(self):
        return f"{self.plate} — {self.driver_name}"


class ParkingTransaction(models.Model):

    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    
    vehicle        = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='transactions')
    receipt_number = models.CharField(max_length=20, unique=True)
    receiver_name  = models.CharField(max_length=200)
    receiver_phone = models.CharField(max_length=20)
    gender         = models.CharField(max_length=10, choices=GENDER)
    nin            = models.CharField(max_length=20, blank=True)
    sign_out_time  = models.DateTimeField()
    fee            = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.receipt_number} — {self.vehicle.plate}"