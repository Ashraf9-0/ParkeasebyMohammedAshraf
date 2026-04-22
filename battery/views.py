from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import BatteryItem, BatteryTransaction

@login_required
def battery_form(request):
    batteries = BatteryItem.objects.all()
    if request.method == 'POST':
        battery = get_object_or_404(BatteryItem, pk=request.POST['battery_id'])
        BatteryTransaction.objects.create(
            battery     = battery,
            plate       = request.POST['plate'].upper(),
            driver_name = request.POST['driver_name'],
        )
        return redirect('battery_list')
    return render(request, 'battery/battery_form.html', {'batteries': batteries})


@login_required
def battery_list(request):
    transactions      = BatteryTransaction.objects.all().order_by('-date')
    today             = timezone.now().date()
    today_transaction = BatteryTransaction.objects.filter(date__date=today)
    total_revenue     = sum(t.battery.price for t in today_transaction)
    context = {
        'transactions':       transactions,
        'total_transactions': today_transaction.count(),
        'total_revenue':      total_revenue,
        'all_transactions':   transactions.count(),
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
                price        = request.POST['price'],
                description  = request.POST.get('description', ''),
            )
        elif action == 'delete':
            battery = get_object_or_404(BatteryItem, pk=request.POST['battery_id'])
            battery.delete()
        return redirect('battery_prices')
    return render(request, 'battery/battery_prices.html', {'batteries': batteries})