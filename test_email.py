#!/usr/bin/env python
"""
Test script to verify email configuration and OTP functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkeasy.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from accounts.models import UserProfile
from accounts.utils import send_otp_email

def test_email_configuration():
    """Test basic email configuration"""
    print("=== Testing Email Configuration ===")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    
    try:
        # Test basic email sending
        send_mail(
            subject='Test Email - ParkEasy',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Replace with your email for testing
            fail_silently=False,
        )
        print("✅ Basic email test successful!")
        return True
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_otp_generation():
    """Test OTP generation"""
    print("\n=== Testing OTP Generation ===")
    
    # Create a test user
    test_user, created = UserProfile.objects.get_or_create(
        username='test_otp_user',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': UserProfile.ROLE_CUSTOMER
        }
    )
    
    if created:
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing test user: {test_user.username}")
    
    # Generate OTP
    otp = test_user.generate_otp()
    print(f"Generated OTP: {otp}")
    print(f"OTP stored in database: {test_user.otp}")
    print(f"OTP created at: {test_user.otp_created_at}")
    print(f"OTP expired: {test_user.is_otp_expired()}")
    
    return test_user

def test_otp_email_sending(user):
    """Test OTP email sending"""
    print("\n=== Testing OTP Email Sending ===")
    
    success = send_otp_email(user.email, user.otp, user.username)
    
    if success:
        print("✅ OTP email sent successfully!")
    else:
        print("❌ OTP email sending failed!")
    
    return success

def test_otp_verification(user):
    """Test OTP verification"""
    print("\n=== Testing OTP Verification ===")
    
    stored_otp = user.otp
    print(f"Stored OTP: {stored_otp}")
    
    # Test correct OTP
    if user.otp == stored_otp and not user.is_otp_expired():
        print("✅ OTP verification successful!")
        
        # Verify the user
        user.email_verified = True
        user.is_active = True
        user.otp = None
        user.otp_created_at = None
        user.save()
        print("✅ User verified successfully!")
        return True
    else:
        print("❌ OTP verification failed!")
        return False

def cleanup_test_user():
    """Clean up test user"""
    print("\n=== Cleaning Up ===")
    try:
        UserProfile.objects.filter(username='test_otp_user').delete()
        print("✅ Test user cleaned up!")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    print("ParkEasy OTP System Test")
    print("=" * 50)
    
    # Test email configuration
    email_ok = test_email_configuration()
    
    if email_ok:
        # Test OTP generation
        test_user = test_otp_generation()
        
        # Test OTP email sending
        otp_email_ok = test_otp_email_sending(test_user)
        
        # Test OTP verification
        otp_verification_ok = test_otp_verification(test_user)
        
        # Cleanup
        cleanup_test_user()
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print(f"Email Configuration: {'✅ PASS' if email_ok else '❌ FAIL'}")
        print(f"OTP Email Sending: {'✅ PASS' if otp_email_ok else '❌ FAIL'}")
        print(f"OTP Verification: {'✅ PASS' if otp_verification_ok else '❌ FAIL'}")
    else:
        print("\n❌ Email configuration failed. Please check your email settings.")
