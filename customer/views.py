from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from accounts.utils import role_required
from owner.models import ParkingPlace, ParkingSlot
from .models import Booking
from django.db import models
from accounts.forms import UserProfileForm


@login_required
@role_required('customer')
def dashboard(request):
    total_bookings = Booking.objects.filter(customer=request.user).count()
    upcoming = Booking.objects.filter(customer=request.user, start_time__gte=timezone.now()).count()
    recent_bookings = Booking.objects.filter(customer=request.user).select_related('slot', 'slot__place').order_by('-created_at')[:5]
    ctx = {
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'customer/dashboard.html', ctx)


@login_required
@role_required('customer')
def search(request):
    city = (request.GET.get('city') or '').strip()
    area = (request.GET.get('area') or '').strip()
    vehicle_type = (request.GET.get('vehicle_type') or '').strip()
    places = ParkingPlace.objects.all()
    if city:
        places = places.filter(city__icontains=city)
    if area:
        places = places.filter(area__icontains=area)
    if vehicle_type:
        places = places.filter(allowed_vehicle_types__icontains=vehicle_type)
    vehicle_choices = [
        ('', 'Any'),
        ('2_wheeler', '2 Wheeler'),
        ('3_wheeler', '3 Wheeler'),
        ('4_wheeler', '4 Wheeler'),
        ('single_axle', 'Single Axle'),
        ('double_axle', 'Double Axle'),
    ]
    ctx = {
        'places': places,
        'city': city,
        'area': area,
        'vehicle_type': vehicle_type,
        'vehicle_choices': vehicle_choices,
    }
    return render(request, 'customer/search.html', ctx)


@login_required
@role_required('customer')
def place_detail(request, place_id: int):
    place = get_object_or_404(ParkingPlace, id=place_id)
    slots = place.slots.all().order_by('code')
    return render(request, 'customer/place_detail.html', {'place': place, 'slots': slots})


@login_required
@role_required('customer')
def book(request, slot_id: int):
    slot = get_object_or_404(ParkingSlot, id=slot_id, is_available=True)
    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
        if start_time >= end_time:
            messages.error(request, 'End time must be after start time.')
            return redirect('customer_place_detail', place_id=slot.place.id)
        booking = Booking.objects.create(
            customer=request.user,
            slot=slot,
            start_time=start_time,
            end_time=end_time,
            status='pending',
        )
        slot.is_available = False
        slot.save(update_fields=['is_available'])
        return redirect(f'/payment/checkout/?booking={booking.id}')
    return render(request, 'customer/book.html', {'slot': slot})


@login_required
@role_required('customer')
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).select_related('slot', 'slot__place').order_by('-created_at')
    return render(request, 'customer/mybookings.html', {'bookings': bookings})


@login_required
@role_required('customer')
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('customer_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'customer/profile_form.html', {'form': form})


@login_required
@role_required('customer')
def settings_view(request):
    # Placeholder page for account/password preferences
    return render(request, 'customer/settings.html')
