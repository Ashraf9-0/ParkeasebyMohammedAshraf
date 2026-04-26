from django.db import models
from django.utils import timezone


class BatteryItem(models.Model):

    BATTERY_TYPES = [
        ('hire', 'Hire'),
        ('sale', 'Sale'),
    ]

    name         = models.CharField(max_length=200)
    battery_type = models.CharField(max_length=10, choices=BATTERY_TYPES)
    price        = models.IntegerField(default=0)       # sale price
    daily_rate   = models.IntegerField(default=0)       # hire cost per day
    description  = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_battery_type_display()})"


class BatteryTransaction(models.Model):

    STATUS = [
        ('out',      'Out'),
        ('returned', 'Returned'),
    ]

    battery       = models.ForeignKey(BatteryItem, on_delete=models.CASCADE)
    plate         = models.CharField(max_length=10)
    driver_name   = models.CharField(max_length=200)
    date_taken    = models.DateTimeField(default=timezone.now)

    
    status        = models.CharField(max_length=10, choices=STATUS, null=True, blank=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    total_charged = models.IntegerField(null=True, blank=True)

    def days_hired(self):
        if self.date_returned:
            delta = self.date_returned - self.date_taken
            days  = delta.total_seconds() / 86400
            return max(1, int(days) if days == int(days) else int(days) + 1)
        return None

    def calculate_charge(self):
        days = self.days_hired()
        if days:
            return days * self.battery.daily_rate
        return 0

    def __str__(self):
        return f"{self.plate} — {self.battery.name}"