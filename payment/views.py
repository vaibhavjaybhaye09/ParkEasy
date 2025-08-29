from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from customer.models import Booking
from .models import Payment


@login_required
def checkout(request):
    booking_id = request.GET.get('booking')
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    amount = 100  # placeholder fixed amount
    if request.method == 'POST':
        payment = Payment.objects.create(booking=booking, amount=amount, status='success')
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])
        return redirect('payment_success')
    return render(request, 'payments/checkout.html', {'booking': booking, 'amount': amount})


@login_required
def success(request):
    return render(request, 'payments/success.html')


@login_required
def failed(request):
    return render(request, 'payments/failed.html')
