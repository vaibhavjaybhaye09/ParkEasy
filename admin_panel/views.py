from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from accounts.models import UserProfile
from accounts.utils import role_required
from customer.models import Booking
from owner.models import ParkingPlace, ParkingSlot
from payment.models import Payment
from .models import UserActivity, AdminAction, SystemSettings
from .forms import (
    UserSearchForm, UserEditForm, UserSuspendForm, 
    BookingSearchForm, SystemSettingsForm
)
import json


def admin_required(view_func):
    """Custom decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != UserProfile.ROLE_ADMIN:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    # Get system statistics
    total_users = UserProfile.objects.count()
    total_customers = UserProfile.objects.filter(role=UserProfile.ROLE_CUSTOMER).count()
    total_owners = UserProfile.objects.filter(role=UserProfile.ROLE_OWNER).count()
    suspended_users = UserProfile.objects.filter(is_suspended=True).count()
    unverified_users = UserProfile.objects.filter(email_verified=False).count()
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='active').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    
    # Parking statistics
    total_places = ParkingPlace.objects.count()
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(is_available=True).count()
    
    # Payment statistics
    total_payments = Payment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Recent activities
    recent_activities = UserActivity.objects.select_related('user').order_by('-created_at')[:10]
    recent_admin_actions = AdminAction.objects.select_related('admin_user', 'target_user').order_by('-created_at')[:10]
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('customer', 'slot', 'slot__place').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_owners': total_owners,
        'suspended_users': suspended_users,
        'unverified_users': unverified_users,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'total_places': total_places,
        'total_slots': total_slots,
        'available_slots': available_slots,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities,
        'recent_admin_actions': recent_admin_actions,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@admin_required
def user_management(request):
    """User management page with search and filtering"""
    form = UserSearchForm(request.GET)
    users = UserProfile.objects.all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        role = form.cleaned_data.get('role')
        status = form.cleaned_data.get('status')
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if role:
            users = users.filter(role=role)
        
        if status:
            if status == 'active':
                users = users.filter(is_suspended=False, email_verified=True)
            elif status == 'suspended':
                users = users.filter(is_suspended=True)
            elif status == 'unverified':
                users = users.filter(email_verified=False)
    
    # Pagination
    paginator = Paginator(users.order_by('-date_joined'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_users': users.count(),
    }
    
    return render(request, 'admin_panel/user_management.html', context)


@login_required
@admin_required
def user_detail(request, user_id):
    """Detailed view of a specific user"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    # Get user's bookings
    bookings = Booking.objects.filter(customer=user).select_related('slot', 'slot__place').order_by('-created_at')
    
    # Get user's activities
    activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:20]
    
    # Get user's payments
    payments = Payment.objects.filter(booking__customer=user).select_related('booking').order_by('-created_at')
    
    # If user is owner, get their parking places
    parking_places = []
    if user.role == UserProfile.ROLE_OWNER:
        parking_places = ParkingPlace.objects.filter(owner=user).order_by('-created_at')
    
    context = {
        'user_detail': user,
        'bookings': bookings,
        'activities': activities,
        'payments': payments,
        'parking_places': parking_places,
    }
    
    return render(request, 'admin_panel/user_detail.html', context)


@login_required
@admin_required
def user_edit(request, user_id):
    """Edit user details"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            old_role = user.role
            form.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action='role_changed' if old_role != user.role else 'profile_updated',
                target_user=user,
                description=f'User profile updated by admin. Role changed from {old_role} to {user.role}' if old_role != user.role else 'User profile updated by admin.',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('admin_panel:user_detail', user_id=user.id)
    else:
        form = UserEditForm(instance=user)
    
    context = {
        'form': form,
        'user_detail': user,
    }
    
    return render(request, 'admin_panel/user_edit.html', context)


@login_required
@admin_required
def user_suspend(request, user_id):
    """Suspend a user account"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        form = UserSuspendForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            user.suspend(request.user, reason)
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action='user_suspended',
                target_user=user,
                description=f'User suspended. Reason: {reason}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.username} has been suspended.')
            return redirect('admin_panel:user_detail', user_id=user.id)
    else:
        form = UserSuspendForm()
    
    context = {
        'form': form,
        'user_detail': user,
    }
    
    return render(request, 'admin_panel/user_suspend.html', context)


@login_required
@admin_required
def user_activate(request, user_id):
    """Activate a suspended user account"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        user.activate(request.user)
        
        # Log admin action
        AdminAction.objects.create(
            admin_user=request.user,
            action='user_activated',
            target_user=user,
            description='User account activated by admin',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'User {user.username} has been activated.')
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    context = {
        'user_detail': user,
    }
    
    return render(request, 'admin_panel/user_activate.html', context)


@login_required
@admin_required
def user_delete(request, user_id):
    """Delete a user account"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        
        # Log admin action before deletion
        AdminAction.objects.create(
            admin_user=request.user,
            action='user_deleted',
            target_user=None,  # User will be deleted
            description=f'User {username} deleted by admin',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        user.delete()
        messages.success(request, f'User {username} has been deleted.')
        return redirect('admin_panel:user_management')
    
    context = {
        'user_detail': user,
    }
    
    return render(request, 'admin_panel/user_delete.html', context)


@login_required
@admin_required
def booking_management(request):
    """Booking management page"""
    form = BookingSearchForm(request.GET)
    bookings = Booking.objects.select_related('customer', 'slot', 'slot__place').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        vehicle_type = form.cleaned_data.get('vehicle_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            bookings = bookings.filter(
                Q(customer__username__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(vehicle_number_plate__icontains=search) |
                Q(slot__code__icontains=search)
            )
        
        if status:
            bookings = bookings.filter(status=status)
        
        if vehicle_type:
            bookings = bookings.filter(vehicle_type=vehicle_type)
        
        if date_from:
            bookings = bookings.filter(start_time__date__gte=date_from)
        
        if date_to:
            bookings = bookings.filter(start_time__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(bookings.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_bookings': bookings.count(),
    }
    
    return render(request, 'admin_panel/booking_management.html', context)


@login_required
@admin_required
def system_settings(request):
    """System settings management"""
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST)
        if form.is_valid():
            # Save settings to database
            settings_data = form.cleaned_data
            for key, value in settings_data.items():
                setting, created = SystemSettings.objects.get_or_create(key=key)
                setting.value = str(value)
                setting.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=request.user,
                action='system_settings_changed',
                target_user=None,
                description='System settings updated by admin',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'System settings updated successfully.')
            return redirect('admin_panel:system_settings')
    else:
        # Load current settings
        current_settings = {}
        for setting in SystemSettings.objects.all():
            current_settings[setting.key] = setting.value
        
        form = SystemSettingsForm(initial=current_settings)
    
    context = {
        'form': form,
    }
    
    return render(request, 'admin_panel/system_settings.html', context)


@login_required
@admin_required
def admin_activity_log(request):
    """Admin activity log"""
    activities = AdminAction.objects.select_related('admin_user', 'target_user').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'admin_panel/activity_log.html', context)


@login_required
@admin_required
def user_activity_log(request):
    """User activity log"""
    activities = UserActivity.objects.select_related('user').order_by('-created_at')
    
    # Filter by user if provided
    user_id = request.GET.get('user_id')
    if user_id:
        activities = activities.filter(user_id=user_id)
    
    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'admin_panel/user_activity_log.html', context)


# AJAX views for dynamic updates
@login_required
@admin_required
@csrf_exempt
def ajax_user_stats(request):
    """AJAX endpoint for user statistics"""
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'get_user_stats':
            stats = {
                'total_users': UserProfile.objects.count(),
                'active_users': UserProfile.objects.filter(is_suspended=False, email_verified=True).count(),
                'suspended_users': UserProfile.objects.filter(is_suspended=True).count(),
                'unverified_users': UserProfile.objects.filter(email_verified=False).count(),
            }
            return JsonResponse(stats)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@admin_required
@require_POST
def ajax_suspend_user(request, user_id):
    """AJAX endpoint for suspending users"""
    user = get_object_or_404(UserProfile, id=user_id)
    reason = request.POST.get('reason', 'No reason provided')
    
    user.suspend(request.user, reason)
    
    # Log admin action
    AdminAction.objects.create(
        admin_user=request.user,
        action='user_suspended',
        target_user=user,
        description=f'User suspended via AJAX. Reason: {reason}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True, 'message': f'User {user.username} suspended successfully.'})


@login_required
@admin_required
@require_POST
def ajax_activate_user(request, user_id):
    """AJAX endpoint for activating users"""
    user = get_object_or_404(UserProfile, id=user_id)
    
    user.activate(request.user)
    
    # Log admin action
    AdminAction.objects.create(
        admin_user=request.user,
        action='user_activated',
        target_user=user,
        description='User activated via AJAX',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({'success': True, 'message': f'User {user.username} activated successfully.'})
