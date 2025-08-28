from django import forms
from .models import ParkingPlace, ParkingSlot

CITY_CHOICES = (
    ('Pune', 'Pune'),
    ('Mumbai', 'Mumbai'),
    ('Jalna', 'Jalna'),
)


class ParkingPlaceForm(forms.ModelForm):
    number_of_slots = forms.IntegerField(min_value=0, initial=0, help_text='Create this many slots initially')
    VEHICLE_CHOICES = (
        ('2_wheeler', '2 Wheeler'),
        ('3_wheeler', '3 Wheeler'),
        ('4_wheeler', '4 Wheeler'),
        ('single_axle', 'Single Axle'),
        ('double_axle', 'Double Axle'),
    )
    allowed_vehicle_types_field = forms.MultipleChoiceField(
        required=False,
        choices=VEHICLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Allowed vehicle types'
    )

    class Meta:
        model = ParkingPlace
        fields = ['name', 'address', 'area', 'city', 'price_per_hour', 'description']
        widgets = {
            'city': forms.Select(choices=CITY_CHOICES),
            'area': forms.TextInput(attrs={'placeholder': 'Area (required for Pune)'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize allowed_vehicle_types_field from model's CSV
        instance: ParkingPlace | None = kwargs.get('instance')
        if instance and instance.allowed_vehicle_types:
            current = [v.strip() for v in instance.allowed_vehicle_types.split(',') if v.strip()]
            self.fields['allowed_vehicle_types_field'].initial = current

    def clean(self):
        cleaned = super().clean()
        city = cleaned.get('city')
        area = cleaned.get('area')
        if city == 'Pune' and not area:
            self.add_error('area', 'Area is required for Pune')
        return cleaned

    def save(self, commit=True):
        obj: ParkingPlace = super().save(commit=False)
        selected = self.cleaned_data.get('allowed_vehicle_types_field') or []
        obj.allowed_vehicle_types = ','.join(selected)
        if commit:
            obj.save()
        return obj


class ParkingSlotForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = ['code', 'is_available', 'price_per_hour']
