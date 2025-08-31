from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'vehicle_type', 'vehicle_number_plate']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'required': True
                }
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'required': True
                }
            ),
            'vehicle_type': forms.Select(
                attrs={
                    'class': 'form-control form-select',
                    'required': True
                }
            ),
            'vehicle_number_plate': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter vehicle number plate (e.g., MH-12-AB-1234)',
                    'required': True,
                    'maxlength': 20
                }
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")
            
            # Check if booking is in the future
            from django.utils import timezone
            if start_time <= timezone.now():
                raise forms.ValidationError("Booking start time must be in the future.")
        
        return cleaned_data

    def clean_vehicle_number_plate(self):
        number_plate = self.cleaned_data.get('vehicle_number_plate')
        if number_plate:
            # Basic validation for vehicle number plate format
            number_plate = number_plate.strip().upper()
            if len(number_plate) < 5:
                raise forms.ValidationError("Vehicle number plate must be at least 5 characters long.")
        return number_plate
