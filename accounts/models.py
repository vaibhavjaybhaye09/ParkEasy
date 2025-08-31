from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class UserProfile(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_OWNER = 'place_owner'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_OWNER, 'Place Owner'),
        (ROLE_ADMIN, 'Admin'),
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
    
    # Admin fields
    is_suspended = models.BooleanField(default=False, help_text='Suspended users cannot access the system')
    suspension_reason = models.TextField(blank=True, help_text='Reason for suspension')
    suspended_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='suspended_users')
    suspended_at = models.DateTimeField(blank=True, null=True)
    
    def suspend(self, admin_user, reason):
        """Suspend user account"""
        self.is_suspended = True
        self.suspension_reason = reason
        self.suspended_by = admin_user
        self.suspended_at = timezone.now()
        self.save()
    
    def activate(self, admin_user):
        """Activate suspended user account"""
        self.is_suspended = False
        self.suspension_reason = ''
        self.suspended_by = None
        self.suspended_at = None
        self.save()
    
    @property
    def is_active_user(self):
        """Check if user is active (not suspended and email verified)"""
        return not self.is_suspended and self.email_verified
    
    # Password Reset fields
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
