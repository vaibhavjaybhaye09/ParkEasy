from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_OWNER = 'place_owner'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_OWNER, 'Place Owner'),
    ]

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.username} - {self.get_role_display()}"
