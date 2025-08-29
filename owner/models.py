from django.db import models
from django.conf import settings


class ParkingPlace(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parking_places')
    name = models.CharField(max_length=120)
    address = models.TextField()
    area = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    allowed_vehicle_types = models.TextField(blank=True, help_text='Comma-separated values of allowed vehicle types')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.area}, {self.city})"


class ParkingSlot(models.Model):
    place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, related_name='slots')
    code = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('place', 'code')

    def __str__(self) -> str:
        return f"{self.place.name} - {self.code}"


