from django.urls import path
from . import views

urlpatterns = [
    path('battery/', views.battery_list, name='battery_list'),
    path('battery/new/', views.battery_form, name='battery_form'),
    path('battery/prices/', views.battery_prices, name='battery_prices'),
]