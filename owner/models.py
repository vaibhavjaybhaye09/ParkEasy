from django.db import models
from django.conf import settings


class ParkingPlace(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parking_places', db_index=True)
    name = models.CharField(max_length=120, db_index=True)
    address = models.TextField()
    area = models.CharField(max_length=80, db_index=True)
    city = models.CharField(max_length=80, db_index=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    allowed_vehicle_types = models.TextField(blank=True, help_text='Comma-separated values of allowed vehicle types')
    # Image fields for parking place
    image1 = models.ImageField(upload_to='parking_places/', blank=True, null=True, help_text='First parking place image')
    image2 = models.ImageField(upload_to='parking_places/', blank=True, null=True, help_text='Second parking place image')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['city', 'area']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.area}, {self.city})"

    @property
    def has_images(self):
        """Check if the parking place has any images"""
        return bool(self.image1 or self.image2)

    @property
    def images_list(self):
        """Return a list of available images"""
        images = []
        if self.image1:
            images.append(self.image1)
        if self.image2:
            images.append(self.image2)
        return images


class ParkingSlot(models.Model):
    place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, related_name='slots', db_index=True)
    code = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True, db_index=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('place', 'code')
        indexes = [
            models.Index(fields=['place', 'is_available']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self) -> str:
        return f"{self.place.name} - {self.code}"


