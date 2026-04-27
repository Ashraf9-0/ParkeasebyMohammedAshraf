from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from .models import BatteryItem, BatteryTransaction


@login_required
def battery_form(request):
    batteries = BatteryItem.objects.all()
    if request.method == 'POST':
        battery  = get_object_or_404(BatteryItem, pk=request.POST['battery_id'])
        date_str = request.POST.get('date_taken', '').strip()
        try:
            date_taken = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%dT%H:%M'))
        except (ValueError, TypeError):
            date_taken = timezone.now()

        if battery.battery_type == 'hire':
            BatteryTransaction.objects.create(
                battery     = battery,
                plate       = request.POST['plate'].upper(),
                driver_name = request.POST['driver_name'],
                date_taken  = date_taken,
                status      = 'out',
            )
        else:
            BatteryTransaction.objects.create(
                battery     = battery,
                plate       = request.POST['plate'].upper(),
                driver_name = request.POST['driver_name'],
                date_taken  = date_taken,
            )
        return redirect('battery_list')

    now = timezone.localtime(timezone.now())
    return render(request, 'battery/battery_form.html', {
        'batteries':        batteries,
        'default_datetime': now.strftime('%Y-%m-%dT%H:%M'),
    })


@login_required
def battery_return(request, pk):
    transaction = get_object_or_404(BatteryTransaction, pk=pk, battery__battery_type='hire', status='out')

    if request.method == 'POST':
        date_str = request.POST.get('date_returned', '').strip()
        try:
            date_returned = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%dT%H:%M'))
        except (ValueError, TypeError):
            date_returned = timezone.now()

        transaction.date_returned = date_returned
        transaction.status        = 'returned'
        transaction.total_charged = transaction.calculate_charge()
        transaction.save()
        return redirect('battery_receipt', pk=transaction.pk)

    now = timezone.localtime(timezone.now())
    return render(request, 'battery/battery_return.html', {
        'transaction':      transaction,
        'default_datetime': now.strftime('%Y-%m-%dT%H:%M'),
    })


@login_required
def battery_receipt(request, pk):
    transaction = get_object_or_404(BatteryTransaction, pk=pk)
    return render(request, 'battery/battery_receipt.html', {'transaction': transaction})


@login_required
def battery_list(request):
    all_transactions   = BatteryTransaction.objects.all().order_by('-date_taken')
    batteries_out      = BatteryTransaction.objects.filter(battery__battery_type='hire', status='out')
    today              = timezone.now().date()
    today_transactions = BatteryTransaction.objects.filter(date_taken__date=today)

    total_revenue = 0
    for t in today_transactions:
        if t.battery.battery_type == 'sale':
            total_revenue += t.battery.price
        elif t.status == 'returned' and t.total_charged:
            total_revenue += t.total_charged

    context = {
        'transactions':       all_transactions,
        'batteries_out':      batteries_out,
        'total_transactions': today_transactions.count(),
        'total_revenue':      total_revenue,
        'all_transactions':   all_transactions.count(),
    }
    return render(request, 'battery/battery_list.html', context)


@login_required
def battery_prices(request):
    batteries = BatteryItem.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            BatteryItem.objects.create(
                name         = request.POST['name'],
                battery_type = request.POST['battery_type'],
                price        = request.POST.get('price', 0) or 0,
                daily_rate   = request.POST.get('daily_rate', 0) or 0,
                description  = request.POST.get('description', ''),
            )
        elif action == 'delete':
            battery = get_object_or_404(BatteryItem, pk=request.POST['battery_id'])
            battery.delete()
        return redirect('battery_prices')
    return render(request, 'battery/battery_prices.html', {'batteries': batteries})

@login_required
def battery_edit(request, pk):
    if request.user.username != 'admin':
        return redirect('battery_list')
    transaction = get_object_or_404(BatteryTransaction, pk=pk)
    if request.method == 'POST':
        battery  = get_object_or_404(BatteryItem, pk=request.POST['battery_id'])
        date_str = request.POST.get('date_taken', '').strip()
        try:
            date_taken = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%dT%H:%M'))
        except (ValueError, TypeError):
            date_taken = transaction.date_taken
        transaction.battery     = battery
        transaction.plate       = request.POST['plate'].upper()
        transaction.driver_name = request.POST['driver_name']
        transaction.date_taken  = date_taken
        transaction.save()
        return redirect('battery_list')
    now = timezone.localtime(timezone.now())
    batteries = BatteryItem.objects.all()
    return render(request, 'battery/battery_edit.html', {
        'transaction':      transaction,
        'batteries':        batteries,
        'default_datetime': transaction.date_taken.strftime('%Y-%m-%dT%H:%M'),
    })


@login_required
def battery_delete(request, pk):
    if request.user.username != 'admin':
        return redirect('battery_list')
    transaction = get_object_or_404(BatteryTransaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('battery_list')
    return render(request, 'battery/battery_confirm_delete.html', {'transaction': transaction})