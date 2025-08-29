from django.db import models
from django.conf import settings
from owner.models import ParkingSlot


class Booking(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, confirmed, cancelled

    def __str__(self) -> str:
        return f"Booking #{self.id} - {self.customer.username} - {self.slot.code}"


