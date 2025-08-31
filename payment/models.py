from django.db import models
from customer.models import Booking


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending', db_index=True)  # pending, success, failed
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['booking', 'status']),
        ]

    def __str__(self) -> str:
        return f"Payment #{self.id} - {self.status}"


