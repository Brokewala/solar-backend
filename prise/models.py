import uuid
from django.db import models
from module.models import Modules


# Create your models here.
class Prise(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    module = models.ForeignKey(
        Modules,
        on_delete=models.CASCADE,
        related_name="modules_prise",
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    voltage = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class PriseData(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    prise = models.ForeignKey(
        Prise,
        on_delete=models.CASCADE,
        related_name="prise_data",
    )
    tension = models.CharField(max_length=200, null=True, blank=True)
    puissance = models.CharField(max_length=200, null=True, blank=True)
    courant = models.CharField(max_length=200, null=True, blank=True)
    consomation = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class PrisePlanning(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    prise = models.ForeignKey(
        Prise,
        on_delete=models.CASCADE,
        related_name="prise_planning",
    )
    consomation = models.CharField(max_length=100, null=True, blank=True)
    date_debut = models.TimeField(null=True, blank=True)
    date_fin = models.TimeField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# Prise relai_state
class PriseRelaiState(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    prise = models.ForeignKey(
        Prise,
        on_delete=models.CASCADE,
        related_name="prise_relai_state",
    )
    active = models.BooleanField(default=False)
    state = models.CharField(max_length=100,  blank=True, default="low")
    couleur = models.CharField(max_length=100, blank=True, default="red")
    valeur = models.CharField(max_length=100, blank=True, default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# reference
class PriseReference(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    prise = models.ForeignKey(
        Prise,
        on_delete=models.CASCADE,
        related_name="prise_reference",
    )
    checked_data = models.BooleanField(default=False)
    checked_state = models.BooleanField(default=False)
    duration = models.CharField(max_length=100, null=True, blank=True)
    consommation = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
