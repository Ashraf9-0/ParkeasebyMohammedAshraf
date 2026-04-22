from django.contrib import admin
from .models import Vehicle, ParkingTransaction

admin.site.register(Vehicle)
admin.site.register(ParkingTransaction)