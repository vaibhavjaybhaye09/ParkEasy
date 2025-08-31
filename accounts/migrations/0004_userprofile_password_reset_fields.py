# Generated manually for password reset functionality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_email_verified_userprofile_otp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='password_reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password_reset_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
