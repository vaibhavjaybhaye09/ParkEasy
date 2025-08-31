from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.utils import role_required
from .models import ParkingPlace, ParkingSlot
from .forms import ParkingPlaceForm, ParkingSlotForm
from customer.models import Booking
from payment.models import Payment
from accounts.forms import UserProfileForm
from django import forms


@login_required
@role_required('place_owner')
def dashboard(request):
    places = ParkingPlace.objects.filter(owner=request.user).order_by('-created_at')
    total_places = places.count()
    total_slots = ParkingSlot.objects.filter(place__owner=request.user).count()
    booked_slots = ParkingSlot.objects.filter(place__owner=request.user, is_available=False).count()
    
    # Get recent bookings with vehicle details
    recent_bookings = Booking.objects.filter(
        slot__place__owner=request.user
    ).select_related('customer', 'slot', 'slot__place').order_by('-created_at')[:10]
    
    # Get active bookings
    active_bookings = Booking.objects.filter(
        slot__place__owner=request.user, 
        status__in=['active', 'pending']
    ).select_related('customer', 'slot', 'slot__place').order_by('-start_time')[:5]
    
    # Get booking statistics
    total_bookings = Booking.objects.filter(slot__place__owner=request.user).count()
    completed_bookings = Booking.objects.filter(slot__place__owner=request.user, status='completed').count()
    
    profile = request.user
    return render(request, 'owner/panel.html', {
        'places': places,
        'total_places': total_places,
        'total_slots': total_slots,
        'booked_slots': booked_slots,
        'active_bookings': active_bookings,
        'recent_bookings': recent_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'profile': profile,
    })


@login_required
@role_required('place_owner')
def add_place(request):
    if request.method == 'POST':
        form = ParkingPlaceForm(request.POST, request.FILES)
        if form.is_valid():
            city = form.cleaned_data.get('city')
            area = form.cleaned_data.get('area')
            if city == 'Pune' and not area:
                form.add_error('area', 'Area is required for Pune')
            else:
                place: ParkingPlace = form.save(commit=False)
                place.owner = request.user
                place.save()
                # auto create slots
                count = form.cleaned_data.get('number_of_slots', 0)
                for i in range(1, count + 1):
                    ParkingSlot.objects.create(place=place, code=f"S{i:03}", is_available=True)
                messages.success(request, 'Parking place created successfully!')
                return redirect('owner_dashboard')
    else:
        form = ParkingPlaceForm()
    return render(request, 'owner/add_place.html', {'form': form})


@login_required
@role_required('place_owner')
def edit_place(request, place_id: int):
    place = get_object_or_404(ParkingPlace, id=place_id, owner=request.user)
    if request.method == 'POST':
        form = ParkingPlaceForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            city = form.cleaned_data.get('city')
            area = form.cleaned_data.get('area')
            if city == 'Pune' and not area:
                form.add_error('area', 'Area is required for Pune')
            else:
                form.save()
                messages.success(request, 'Parking place updated successfully!')
                return redirect('owner_dashboard')
    else:
        form = ParkingPlaceForm(instance=place)
        if 'number_of_slots' in form.fields:
            form.fields['number_of_slots'].widget = forms.HiddenInput()
    return render(request, 'owner/edit_place.html', {'form': form, 'place': place})


@login_required
@role_required('place_owner')
def delete_place(request, place_id: int):
    place = get_object_or_404(ParkingPlace, id=place_id, owner=request.user)
    if request.method == 'POST':
        place.delete()
        messages.success(request, 'Parking place deleted.')
        return redirect('owner_dashboard')
    return render(request, 'owner/delete_place_confirm.html', {'place': place})


@login_required
@role_required('place_owner')
def profile_edit(request):
    profile = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('owner_dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'owner/profile_form.html', {'form': form})


@login_required
@role_required('place_owner')
def slots(request, place_id: int):
    place = get_object_or_404(ParkingPlace, id=place_id, owner=request.user)
    if request.method == 'POST':
        # simple add slot
        code = request.POST.get('code')
        if code:
            ParkingSlot.objects.create(place=place, code=code, is_available=True)
            messages.success(request, 'Slot added.')
            return redirect('owner_slots', place_id=place.id)
    return render(request, 'owner/slots.html', {'place': place, 'slots': place.slots.all().order_by('code')})


@login_required
@role_required('place_owner')
def slot_edit(request, slot_id: int):
    slot = get_object_or_404(ParkingSlot, id=slot_id, place__owner=request.user)
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slot updated.')
            return redirect('owner_slots', place_id=slot.place.id)
    else:
        form = ParkingSlotForm(instance=slot)
    return render(request, 'owner/slot_edit.html', {'form': form, 'slot': slot})


@login_required
@role_required('place_owner')
def slot_delete(request, slot_id: int):
    slot = get_object_or_404(ParkingSlot, id=slot_id, place__owner=request.user)
    place_id = slot.place.id
    slot.delete()
    messages.success(request, 'Slot deleted.')
    return redirect('owner_slots', place_id=place_id)


@login_required
@role_required('place_owner')
def bookings(request):
    # Get all bookings with vehicle details and customer info
    bookings_qs = Booking.objects.filter(
        slot__place__owner=request.user
    ).select_related('customer', 'slot', 'slot__place').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings_qs = bookings_qs.filter(status=status_filter)
    
    # Filter by vehicle type if provided
    vehicle_type = request.GET.get('vehicle_type')
    if vehicle_type:
        bookings_qs = bookings_qs.filter(vehicle_type=vehicle_type)
    
    return render(request, 'owner/bookings.html', {
        'bookings': bookings_qs,
        'status_filter': status_filter,
        'vehicle_type_filter': vehicle_type,
        'status_choices': Booking.STATUS_CHOICES,
        'vehicle_type_choices': Booking.VEHICLE_TYPE_CHOICES,
    })


@login_required
@role_required('place_owner')
def payments(request):
    payments_qs = Payment.objects.filter(booking__slot__place__owner=request.user).select_related('booking', 'booking__slot', 'booking__slot__place').order_by('-created_at')
    return render(request, 'owner/payments.html', {'payments': payments_qs})


@login_required
@role_required('place_owner')
def booked_slots(request):
    # Get all booked slots with customer details and vehicle information
    booked_slots = ParkingSlot.objects.filter(
        place__owner=request.user, 
        is_available=False
    ).select_related('place').prefetch_related('bookings__customer')
    
    # Get active bookings for these slots with vehicle details
    active_bookings = Booking.objects.filter(
        slot__place__owner=request.user,
        status__in=['active', 'pending']
    ).select_related('customer', 'slot', 'slot__place').order_by('-start_time')
    
    # Get completed bookings for history
    completed_bookings = Booking.objects.filter(
        slot__place__owner=request.user,
        status='completed'
    ).select_related('customer', 'slot', 'slot__place').order_by('-end_time')[:20]
    
    return render(request, 'owner/booked_slots.html', {
        'booked_slots': booked_slots,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
    })
