# Generated manually for vehicle details

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='vehicle_type',
            field=models.CharField(
                choices=[
                    ('bike', 'Bike'),
                    ('car', 'Car'),
                    ('truck', 'Truck'),
                    ('bus', 'Bus'),
                    ('van', 'Van'),
                    ('suv', 'SUV'),
                    ('other', 'Other')
                ],
                max_length=20,
                default='car'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle_number_plate',
            field=models.CharField(
                help_text='Vehicle registration number',
                max_length=20,
                default='UNKNOWN'
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('active', 'Active'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
    ]
