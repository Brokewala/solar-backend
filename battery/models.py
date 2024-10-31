import uuid
from django.db import models
from module.models import Modules


# Create your models here.
class Battery(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    module = models.ForeignKey(
        Modules,
        on_delete=models.CASCADE,
        related_name="modules_battery",
    )
    marque = models.CharField(max_length=200, null=True, blank=True)
    puissance = models.CharField(max_length=200, null=True, blank=True)
    voltage = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class BatteryData(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    battery = models.ForeignKey(
        Battery,
        on_delete=models.CASCADE,
        related_name="battery_data",
    )
    tension = models.CharField(max_length=200, null=True, blank=True)
    puissance = models.CharField(max_length=200, null=True, blank=True)
    courant = models.CharField(max_length=200, null=True, blank=True)
    energy = models.CharField(max_length=200, null=True, blank=True)
    pourcentage = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class BatteryPlanning(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    battery = models.ForeignKey(
        Battery,
        on_delete=models.CASCADE,
        related_name="battery_planning",
    )
    energie = models.CharField(max_length=100, null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
