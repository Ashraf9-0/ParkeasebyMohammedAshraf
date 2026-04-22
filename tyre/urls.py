from django.urls import path
from . import views

urlpatterns = [
    path('tyre/', views.tyre_list, name='tyre_list'),
    path('tyre/new/', views.tyre_form, name='tyre_form'),
    path('tyre/receipt/<int:pk>/', views.tyre_receipt, name='tyre_receipt'),
]