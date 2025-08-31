from django.core.management.base import BaseCommand
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create an admin user for ParkEasy'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if UserProfile.objects.filter(role=UserProfile.ROLE_ADMIN).exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )
            return

        # Create admin user with unique username
        username = 'parkeasy_admin'
        email = 'admin@parkeasy.com'
        
        # Check if username already exists
        if UserProfile.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Username {username} already exists!')
            )
            return

        admin_user = UserProfile.objects.create_user(
            username=username,
            email=email,
            password='admin123',
            first_name='ParkEasy',
            last_name='Admin',
            role=UserProfile.ROLE_ADMIN,
            email_verified=True,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'Username: {admin_user.username}\n'
                f'Email: {admin_user.email}\n'
                f'Password: admin123\n'
                f'Role: {admin_user.get_role_display()}'
            )
        )