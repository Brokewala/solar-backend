# Generated by Django 4.2.4 on 2024-11-01 04:48

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('prise', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriseData',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('tension', models.CharField(blank=True, max_length=200, null=True)),
                ('puissance', models.CharField(blank=True, max_length=200, null=True)),
                ('courant', models.CharField(blank=True, max_length=200, null=True)),
                ('consomation', models.CharField(blank=True, max_length=200, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('prise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prise_data', to='prise.prise')),
            ],
        ),
    ]
