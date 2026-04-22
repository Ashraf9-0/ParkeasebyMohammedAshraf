from django.db import models
from django.utils import timezone

class BatteryItem(models.Model):

    BATTERY_TYPES = [
        ('hire', 'Hire'),
        ('sale', 'Sale'),
    ]

    name         = models.CharField(max_length=200)
    battery_type = models.CharField(max_length=10, choices=BATTERY_TYPES)
    price        = models.IntegerField(default=0)
    description  = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} — UGX {self.price}"


class BatteryTransaction(models.Model):

    battery      = models.ForeignKey(BatteryItem, on_delete=models.CASCADE)
    plate        = models.CharField(max_length=10)
    driver_name  = models.CharField(max_length=200)
    date         = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.plate} — {self.battery.name}"