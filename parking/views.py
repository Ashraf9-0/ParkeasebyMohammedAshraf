from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import Vehicle, ParkingTransaction
import uuid
from tyre.models import TyreService
from battery.models import BatteryTransaction
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


def calculate_fee(vehicle_type, arrival_time, sign_out_time):

    SHORT_STAY_FEES = {
        'truck':        2000,
        'personal_car': 2000,
        'taxi':         2000,
        'coaster':      3000,
        'boda_boda':    1000,
    }
    DAY_FEES = {
        'truck':        5000,
        'personal_car': 3000,
        'taxi':         3000,
        'coaster':      4000,
        'boda_boda':    2000,
    }
    NIGHT_FEES = {
        'truck':        10000,
        'personal_car': 2000,
        'taxi':         2000,
        'coaster':      2000,
        'boda_boda':    2000,
    }

    def is_daytime(dt):
        """Day = 06:00–18:59, Night = 19:00–05:59."""
        return 6 <= dt.hour <= 18

    def next_boundary(dt):
        if dt.hour < 6:
            return dt.replace(hour=6, minute=0, second=0, microsecond=0)
        elif dt.hour <= 18:
            return dt.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            return (dt + timedelta(days=1)).replace(
                hour=6, minute=0, second=0, microsecond=0
            )

    total_fee = 0
    cursor = arrival_time

    while cursor < sign_out_time:
        boundary   = next_boundary(cursor)
        period_end = min(boundary, sign_out_time)

        hours_in_slot = (period_end - cursor).total_seconds() / 3600

        if hours_in_slot < 3:
            total_fee += SHORT_STAY_FEES.get(vehicle_type, 0)
        elif is_daytime(cursor):
            total_fee += DAY_FEES.get(vehicle_type, 0)
        else:
            total_fee += NIGHT_FEES.get(vehicle_type, 0)

        cursor = period_end

    return total_fee


def generate_receipt():
    return 'PKE-' + str(uuid.uuid4()).upper()[:6]


@login_required
def dashboard(request):
    vehicles_in     = Vehicle.objects.filter(status='parked')
    signed_out      = Vehicle.objects.filter(status='signed_out')
    transactions    = ParkingTransaction.objects.filter(
        sign_out_time__date=timezone.now().date()
    )
    total_revenue   = sum(t.fee for t in transactions)
    boda_bodas      = vehicles_in.filter(vehicle_type='boda_boda').count()
    recent_vehicles = Vehicle.objects.all().order_by('-arrival_time')[:5]
    context = {
        'vehicles_in':     vehicles_in.count(),
        'signed_out':      signed_out.count(),
        'total_revenue':   total_revenue,
        'boda_bodas':      boda_bodas,
        'recent_vehicles': recent_vehicles,
    }
    return render(request, 'parking/dashboard.html', context)


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('-arrival_time')
    context  = {'vehicles': vehicles}
    return render(request, 'parking/vehicle_list.html', context)


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    context = {'vehicle': vehicle}
    return render(request, 'parking/vehicle_detail.html', context)


@login_required
def register_vehicle(request):
    error = None

    if request.method == 'POST':
        plate = request.POST['plate'].upper().strip()

        if Vehicle.objects.filter(plate=plate, status='parked').exists():
            error = f"A vehicle with plate {plate} is already checked in. Sign it out before registering again."
        else:
            arrival_date     = request.POST['arrival_date']
            arrival_time_str = request.POST['arrival_time']
            arrival_datetime = make_aware(
                parse_datetime(f"{arrival_date}T{arrival_time_str}:00")
            )
            Vehicle.objects.create(
                driver_name  = request.POST['driver_name'],
                phone        = request.POST['phone'],
                plate        = plate,
                vehicle_type = request.POST['vehicle_type'],
                model        = request.POST.get('model', ''),
                color        = request.POST.get('color', ''),
                nin          = request.POST.get('nin', ''),
                arrival_time = arrival_datetime,
                status       = 'parked',
            )
            return redirect('vehicle_list')

    now = timezone.localtime(timezone.now())  # respects your TIME_ZONE in settings.py
    return render(request, 'parking/register_vehicle.html', {
        'error':        error,
        'default_date': now.strftime('%Y-%m-%d'),
        'default_time': now.strftime('%H:%M'),
    })

@login_required
def sign_out_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        sign_out_date     = request.POST['sign_out_date']
        sign_out_time_str = request.POST['sign_out_time']
        sign_out_time     = make_aware(
            parse_datetime(f"{sign_out_date}T{sign_out_time_str}:00")
        )
        fee = calculate_fee(
            vehicle.vehicle_type,
            vehicle.arrival_time,
            sign_out_time
        )
        transaction = ParkingTransaction.objects.create(
            vehicle        = vehicle,
            receipt_number = generate_receipt(),
            receiver_name  = request.POST['receiver_name'],
            receiver_phone = request.POST['phone'],
            gender         = request.POST['gender'],
            nin            = request.POST.get('nin', ''),
            sign_out_time  = sign_out_time,
            fee            = fee,
        )
        vehicle.status = 'signed_out'
        vehicle.save()
        return redirect('receipt', pk=transaction.pk)

    now = timezone.localtime(timezone.now())
    return render(request, 'parking/sign_out.html', {
        'vehicle':      vehicle,
        'default_date': now.strftime('%Y-%m-%d'),
        'default_time': now.strftime('%H:%M'),
    })


@login_required
def receipt(request, pk):
    transaction = get_object_or_404(ParkingTransaction, pk=pk)
    vehicle     = transaction.vehicle
    duration    = transaction.sign_out_time - vehicle.arrival_time
    hours       = int(duration.total_seconds() // 3600)
    minutes     = int((duration.total_seconds() % 3600) // 60)
    context     = {
        'transaction': transaction,
        'vehicle':     vehicle,
        'hours':       hours,
        'minutes':     minutes,
    }
    return render(request, 'parking/receipt.html', context)


@login_required
def daily_report(request):
    date             = request.GET.get('date', timezone.now().date())
    transactions     = ParkingTransaction.objects.filter(
        sign_out_time__date=date
    ).order_by('-sign_out_time')
    tyre_services    = TyreService.objects.filter(date__date=date)
    battery_trans    = BatteryTransaction.objects.filter(date_taken__date=date)
    parking_revenue  = sum(t.fee for t in transactions)
    tyre_revenue     = sum(s.price for s in tyre_services)
    battery_revenue  = sum(
    t.battery.price if t.battery.battery_type == 'sale'
    else (t.total_charged or 0)
    for t in battery_trans
)
    total_revenue    = parking_revenue + tyre_revenue + battery_revenue
    context = {
        'transactions':    transactions,
        'tyre_services':   tyre_services,
        'battery_trans':   battery_trans,
        'parking_revenue': parking_revenue,
        'tyre_revenue':    tyre_revenue,
        'battery_revenue': battery_revenue,
        'total_revenue':   total_revenue,
        'date':            date,
    }
    return render(request, 'parking/daily_report.html', context)
@login_required
def vehicle_edit(request, pk):
    if request.user.username != 'admin':
        return redirect('vehicle_list')
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        arrival_date     = request.POST['arrival_date']
        arrival_time_str = request.POST['arrival_time']
        arrival_datetime = make_aware(
            parse_datetime(f"{arrival_date}T{arrival_time_str}:00")
        )
        vehicle.driver_name  = request.POST['driver_name']
        vehicle.phone        = request.POST['phone']
        vehicle.plate        = request.POST['plate'].upper().strip()
        vehicle.vehicle_type = request.POST['vehicle_type']
        vehicle.model        = request.POST.get('model', '')
        vehicle.color        = request.POST.get('color', '')
        vehicle.nin          = request.POST.get('nin', '')
        vehicle.arrival_time = arrival_datetime
        vehicle.save()
        return redirect('vehicle_detail', pk=vehicle.pk)
    return render(request, 'parking/vehicle_edit.html', {'vehicle': vehicle})


@login_required
def vehicle_delete(request, pk):
    if request.user.username != 'admin':
        return redirect('vehicle_list')
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        return redirect('vehicle_list')
    return render(request, 'parking/vehicle_confirm_delete.html', {'vehicle': vehicle})