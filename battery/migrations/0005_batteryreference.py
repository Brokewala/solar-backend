# Generated by Django 4.2.4 on 2024-11-01 02:37

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('battery', '0004_batteryrelaistate'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatteryReference',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('checked_data', models.BooleanField(default=False)),
                ('checked_state', models.BooleanField(default=False)),
                ('duration', models.CharField(blank=True, max_length=100, null=True)),
                ('energy', models.CharField(blank=True, max_length=100, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('battery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battery_reference', to='battery.battery')),
            ],
        ),
    ]
