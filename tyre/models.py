from django.db import models
from django.utils import timezone

class TyreService(models.Model):

    SERVICE_TYPES = [
        ('pressure',        'Pressure Check'),
        ('puncture',        'Puncture Fixing'),
        ('valve',           'Valve Replacement'),
        ('tyre_13',         'Tyre Size 13'),
        ('tyre_14',         'Tyre Size 14'),
        ('tyre_15',         'Tyre Size 15'),
        ('tyre_16',         'Tyre Size 16'),
    ]

    plate        = models.CharField(max_length=10)
    driver_name  = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    price        = models.IntegerField(default=0)
    date         = models.DateTimeField(default=timezone.now)
    notes        = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plate} — {self.get_service_type_display()}"