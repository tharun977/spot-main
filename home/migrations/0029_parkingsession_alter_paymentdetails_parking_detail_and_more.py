# Generated by Django 5.1.6 on 2025-03-01 14:28

import django.db.models.deletion
import home.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_alter_parkinglot_lot_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parking_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('vehicle_reg_no', models.CharField(blank=True, max_length=20, null=True, validators=[home.validators.validate_vehicle_number])),
                ('mobile_number', models.CharField(max_length=15)),
                ('vehicle_type_id', models.CharField(max_length=10)),
                ('in_time', models.DateTimeField(auto_now_add=True)),
                ('out_time', models.DateTimeField(blank=True, null=True)),
                ('payment_status', models.BooleanField(default=False)),
                ('parking_duration', models.DurationField(blank=True, null=True)),
                ('occupied_by', models.CharField(blank=True, max_length=100, null=True)),
                ('parking_lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.parkinglot')),
            ],
        ),
        migrations.AlterField(
            model_name='paymentdetails',
            name='parking_detail',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='home.parkingsession'),
        ),
        migrations.DeleteModel(
            name='ParkingDetails',
        ),
    ]
