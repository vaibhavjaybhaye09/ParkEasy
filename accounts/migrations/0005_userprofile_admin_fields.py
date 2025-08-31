# Generated manually for admin functionality

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_userprofile_password_reset_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_suspended',
            field=models.BooleanField(default=False, help_text='Suspended users cannot access the system'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='suspension_reason',
            field=models.TextField(blank=True, help_text='Reason for suspension'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='suspended_by',
            field=models.ForeignKey(blank=True, help_text='Admin who suspended this user', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suspended_users', to='accounts.userprofile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='suspended_at',
            field=models.DateTimeField(blank=True, help_text='When the user was suspended', null=True),
        ),
    ]
