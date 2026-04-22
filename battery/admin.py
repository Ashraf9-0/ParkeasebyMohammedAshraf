from django.contrib import admin
from .models import BatteryItem, BatteryTransaction

admin.site.register(BatteryItem)
admin.site.register(BatteryTransaction)