from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.utils import send_otp_email, send_welcome_email

User = get_user_model()

class Command(BaseCommand):
    help = 'Test OTP system by creating a test user and sending OTP'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email for test user')
        parser.add_argument('--username', type=str, help='Username for test user')

    def handle(self, *args, **options):
        email = options.get('email', 'test@example.com')
        username = options.get('username', 'testuser')
        
        self.stdout.write(f"Testing OTP system for {email}...")
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f"User {username} already exists with email {email}")
        except User.DoesNotExist:
            # Create test user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                role='customer',
                is_active=False,
                email_verified=False
            )
            self.stdout.write(f"Created test user: {username}")
        
        # Generate OTP
        otp = user.generate_otp()
        self.stdout.write(f"Generated OTP: {otp}")
        
        # Test sending OTP email
        if send_otp_email(email, otp, username):
            self.stdout.write(self.style.SUCCESS("✅ OTP email sent successfully!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Failed to send OTP email"))
        
        # Test welcome email (simulate verification)
        if send_welcome_email(email, username):
            self.stdout.write(self.style.SUCCESS("✅ Welcome email sent successfully!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Failed to send welcome email"))
        
        self.stdout.write(f"\nTest user details:")
        self.stdout.write(f"Username: {user.username}")
        self.stdout.write(f"Email: {user.email}")
        self.stdout.write(f"OTP: {user.otp}")
        self.stdout.write(f"OTP Created: {user.otp_created_at}")
        self.stdout.write(f"Email Verified: {user.email_verified}")
        self.stdout.write(f"Is Active: {user.is_active}")
        
        self.stdout.write(self.style.SUCCESS("\nOTP system test completed!"))
