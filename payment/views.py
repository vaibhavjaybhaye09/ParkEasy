from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from customer.models import Booking, Receipt
from .models import Payment


@login_required
def checkout(request):
    booking_id = request.GET.get('booking')
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    amount = booking.total_amount  # Use calculated amount from booking
    
    if request.method == 'POST':
        payment = Payment.objects.create(booking=booking, amount=amount, status='success')
        booking.status = 'confirmed'
        booking.save(update_fields=['status'])
        
        # Generate receipt using the new method
        receipt = booking.generate_receipt(payment_status='success')
        
        messages.success(request, f'Payment successful! Receipt #{receipt.receipt_number} has been generated.')
        return redirect('payment_success', receipt_id=receipt.id)
    
    return render(request, 'payments/checkout.html', {'booking': booking, 'amount': amount})


@login_required
def success(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id, booking__customer=request.user)
    return render(request, 'payments/success.html', {'receipt': receipt})


@login_required
def failed(request):
    return render(request, 'payments/failed.html')


@login_required
def generate_receipt(request, booking_id):
    """Generate a receipt for a booking (for future payments or manual generation)"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    # Check if receipt already exists
    if hasattr(booking, 'receipt'):
        messages.info(request, f'Receipt #{booking.receipt.receipt_number} already exists for this booking.')
        return redirect('customer_view_receipt', receipt_id=booking.receipt.id)
    
    # Generate receipt
    receipt = booking.generate_receipt(payment_status='pending')
    
    messages.success(request, f'Receipt #{receipt.receipt_number} generated successfully!')
    return redirect('customer_view_receipt', receipt_id=receipt.id)


@login_required
def view_receipt(request, receipt_id):
    """View a specific receipt"""
    receipt = get_object_or_404(Receipt, id=receipt_id, booking__customer=request.user)
    return render(request, 'payments/receipt.html', {'receipt': receipt})


@login_required
def my_receipts(request):
    """View all receipts for the current user"""
    receipts = Receipt.objects.filter(booking__customer=request.user).order_by('-created_at')
    return render(request, 'payments/my_receipts.html', {'receipts': receipts})
