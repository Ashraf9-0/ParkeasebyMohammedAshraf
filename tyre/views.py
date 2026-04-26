from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import TyreService

TYRE_PRICES = {
    'pressure': 500,
    'puncture': 5000,
    'valve':    5000,
}

@login_required
def tyre_form(request):
    if request.method == 'POST':
        service_type = request.POST['service_type']
        if service_type.startswith('tyre_'):
            price = int(request.POST.get('custom_price', 0))
        else:
            price = TYRE_PRICES.get(service_type, 0)
        service = TyreService.objects.create(
            plate        = request.POST['plate'].upper(),
            driver_name  = request.POST['driver_name'],
            service_type = service_type,
            price        = price,
            notes        = request.POST.get('notes', ''),
        )
        return redirect('tyre_receipt', pk=service.pk)
    return render(request, 'tyre/tyre_form.html')


@login_required
def tyre_list(request):
    services       = TyreService.objects.all().order_by('-date')
    today          = timezone.now().date()
    today_services = TyreService.objects.filter(date__date=today)
    total_revenue  = sum(s.price for s in today_services)
    context = {
        'services':       services,
        'total_services': today_services.count(),
        'total_revenue':  total_revenue,
        'all_services':   services.count(),
    }
    return render(request, 'tyre/tyre_list.html', context)


@login_required
def tyre_receipt(request, pk):
    service = get_object_or_404(TyreService, pk=pk)
    return render(request, 'tyre/tyre_receipt.html', {'service': service})

@login_required
def tyre_edit(request, pk):
    service = get_object_or_404(TyreService, pk=pk)
    if request.method == 'POST':
        service_type = request.POST['service_type']
        if service_type.startswith('tyre_'):
            price = int(request.POST.get('custom_price', 0))
        else:
            price = TYRE_PRICES.get(service_type, service.price)
        service.plate        = request.POST['plate'].upper()
        service.driver_name  = request.POST['driver_name']
        service.service_type = service_type
        service.price        = price
        service.notes        = request.POST.get('notes', '')
        service.save()
        return redirect('tyre_receipt', pk=service.pk)
    return render(request, 'tyre/tyre_edit.html', {'service': service})


@login_required
def tyre_delete(request, pk):
    service = get_object_or_404(TyreService, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('tyre_list')
    return render(request, 'tyre/tyre_confirm_delete.html', {'service': service})