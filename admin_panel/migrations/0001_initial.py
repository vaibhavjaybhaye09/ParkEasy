# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0005_userprofile_admin_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('booking_created', 'Booking Created'), ('booking_cancelled', 'Booking Cancelled'), ('payment_made', 'Payment Made'), ('profile_updated', 'Profile Updated'), ('account_suspended', 'Account Suspended'), ('account_activated', 'Account Activated')], max_length=50)),
                ('description', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='accounts.userprofile')),
            ],
            options={
                'verbose_name_plural': 'User Activities',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'System Settings',
            },
        ),
        migrations.CreateModel(
            name='AdminAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('user_suspended', 'User Suspended'), ('user_activated', 'User Activated'), ('user_deleted', 'User Deleted'), ('role_changed', 'User Role Changed'), ('booking_modified', 'Booking Modified'), ('payment_refunded', 'Payment Refunded'), ('system_settings_changed', 'System Settings Changed')], max_length=50)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_actions', to='accounts.userprofile')),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_actions_against', to='accounts.userprofile')),
            ],
            options={
                'verbose_name_plural': 'Admin Actions',
                'ordering': ['-created_at'],
            },
        ),
    ]
