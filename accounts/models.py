from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


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
    
    # OTP Verification fields
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.username} - {self.get_role_display()}"
    
    def is_otp_expired(self):
        """Check if OTP has expired (15 minutes)"""
        if not self.otp_created_at:
            return True
        return timezone.now() > self.otp_created_at + timedelta(minutes=15)
    
    def generate_otp(self):
        """Generate a new 6-digit OTP"""
        import random
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp', 'otp_created_at'])
        return self.otp
