from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('register/', views.register_vehicle, name='register_vehicle'),
    path('sign-out/<int:pk>/', views.sign_out_vehicle, name='sign_out'),
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
    path('report/', views.daily_report, name='daily_report'),
    path('vehicle/edit/<int:pk>/',   views.vehicle_edit,   name='vehicle_edit'),
path('vehicle/delete/<int:pk>/', views.vehicle_delete, name='vehicle_delete'),
]