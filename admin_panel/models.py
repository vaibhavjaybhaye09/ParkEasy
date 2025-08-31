from django.db import models
from django.conf import settings
from django.utils import timezone


class UserActivity(models.Model):
    """Track user activities for admin monitoring"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('booking_created', 'Booking Created'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('payment_made', 'Payment Made'),
        ('profile_updated', 'Profile Updated'),
        ('account_suspended', 'Account Suspended'),
        ('account_activated', 'Account Activated'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"


class AdminAction(models.Model):
    """Track admin actions for audit purposes"""
    ACTION_CHOICES = [
        ('user_suspended', 'User Suspended'),
        ('user_activated', 'User Activated'),
        ('user_deleted', 'User Deleted'),
        ('role_changed', 'User Role Changed'),
        ('booking_modified', 'Booking Modified'),
        ('payment_refunded', 'Payment Refunded'),
        ('system_settings_changed', 'System Settings Changed'),
    ]
    
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_actions_against', blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Admin Actions'
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action} - {self.created_at}"


class SystemSettings(models.Model):
    """System-wide settings that can be managed by admin"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"{self.key}: {self.value}"
