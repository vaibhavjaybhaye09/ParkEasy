from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from owner.models import ParkingSlot


class Booking(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('2_wheeler', '2 Wheeler'),
        ('3_wheeler', '3 Wheeler'),
        ('4_wheeler', '4 Wheeler'),
        ('single_axle', 'Single Axle'),
        ('double_axle', 'Double Axle'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('suv', 'SUV'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', db_index=True)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings', db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Vehicle details
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, db_index=True)
    vehicle_number_plate = models.CharField(max_length=20, help_text='Vehicle registration number')

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['slot', 'status']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['status', 'start_time']),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.id} - {self.customer.username} - {self.slot.code}"

    @property
    def duration_hours(self):
        """Calculate booking duration in hours"""
        duration = self.end_time - self.start_time
        return round(duration.total_seconds() / 3600, 2)

    @property
    def total_amount(self):
        """Calculate total amount based on duration and slot price"""
        slot_price = self.slot.price_per_hour or self.slot.place.price_per_hour
        # Convert duration_hours to Decimal to avoid type mismatch
        duration_decimal = Decimal(str(self.duration_hours))
        return round(slot_price * duration_decimal, 2)

    def generate_receipt(self, payment_status='success'):
        """Generate a receipt for this booking"""
        from decimal import Decimal
        
        # Check if receipt already exists
        if hasattr(self, 'receipt'):
            return self.receipt
        
        # Calculate amount
        amount = self.total_amount
        
        # Create receipt
        receipt = Receipt.objects.create(
            booking=self,
            customer_name=f"{self.customer.first_name} {self.customer.last_name}".strip() or self.customer.username,
            parking_place_name=self.slot.place.name,
            slot_code=self.slot.code,
            vehicle_type=self.get_vehicle_type_display(),
            vehicle_number_plate=self.vehicle_number_plate,
            start_time=self.start_time,
            end_time=self.end_time,
            duration_hours=Decimal(str(self.duration_hours)),
            amount_per_hour=self.slot.price_per_hour or self.slot.place.price_per_hour,
            total_amount=amount,
            payment_status=payment_status
        )
        
        return receipt


class Receipt(models.Model):
    """Receipt model for successful bookings and payments"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='receipt', db_index=True)
    receipt_number = models.CharField(max_length=20, unique=True, db_index=True)
    customer_name = models.CharField(max_length=100)
    parking_place_name = models.CharField(max_length=120)
    slot_code = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    vehicle_number_plate = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    amount_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='success')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['customer_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"Receipt #{self.receipt_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number: RCPT-YYYYMMDD-XXXX
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            last_receipt = Receipt.objects.filter(
                receipt_number__startswith=f'RCPT-{today}'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_number = int(last_receipt.receipt_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.receipt_number = f'RCPT-{today}-{new_number:04d}'
        
        super().save(*args, **kwargs)


