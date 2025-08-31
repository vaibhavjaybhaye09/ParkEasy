from django import forms
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from customer.models import Booking
from owner.models import ParkingPlace, ParkingSlot
from payment.models import Payment

User = get_user_model()


class UserSearchForm(forms.Form):
    """Form for searching users"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username, email, or role...'
        })
    )
    role = forms.ChoiceField(
        choices=[('', 'All Roles')] + UserProfile.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('unverified', 'Email Not Verified'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class UserEditForm(forms.ModelForm):
    """Form for editing user details"""
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserSuspendForm(forms.Form):
    """Form for suspending users"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter reason for suspension...'
        }),
        help_text='Provide a clear reason for suspending this user account.'
    )


class BookingSearchForm(forms.Form):
    """Form for searching bookings"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by customer name, vehicle number, or slot...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Booking.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_type = forms.ChoiceField(
        choices=[('', 'All Vehicle Types')] + Booking.VEHICLE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class SystemSettingsForm(forms.Form):
    """Form for managing system settings"""
    max_booking_duration_hours = forms.IntegerField(
        min_value=1,
        max_value=168,  # 1 week
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Maximum booking duration in hours'
    )
    min_advance_booking_hours = forms.IntegerField(
        min_value=0,
        max_value=72,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Minimum advance booking time in hours'
    )
    max_cancellation_hours = forms.IntegerField(
        min_value=0,
        max_value=24,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Maximum hours before booking start time to allow cancellation'
    )
    system_maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Enable maintenance mode (only admins can access)'
    )
    maintenance_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Message to display during maintenance...'
        })
    )
