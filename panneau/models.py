import uuid
from django.db import models
from module.models import Modules


# Create your models here.
class Panneau(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    module = models.ForeignKey(
        Modules,
        on_delete=models.CASCADE,
        related_name="modules_panneau",
    )
    marque = models.CharField(max_length=200, null=True, blank=True)
    puissance = models.CharField(max_length=200, null=True, blank=True)
    voltage = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class PanneauData(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    panneau = models.ForeignKey(
        Panneau,
        on_delete=models.CASCADE,
        related_name="panneau_data",
    )
    tension = models.CharField(max_length=200, null=True, blank=True)
    puissance = models.CharField(max_length=200, null=True, blank=True)
    courant = models.CharField(max_length=200, null=True, blank=True)
    production = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class PanneauPlanning(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    panneau = models.ForeignKey(
        Panneau,
        on_delete=models.CASCADE,
        related_name="panneau_planning",
    )
    energie = models.CharField(max_length=100, null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# Panneau_ relai_state
# valeur /0-1
# state /low-high
# couleur /vert-rouge
class PanneauRelaiState(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    panneau = models.ForeignKey(
        Panneau,
        on_delete=models.CASCADE,
        related_name="panneau_relai_state",
    )
    active = models.BooleanField(default=False)
    state = models.CharField(max_length=100,  blank=True, default="low")
    couleur = models.CharField(max_length=100, blank=True, default="red")
    valeur = models.CharField(max_length=100, blank=True, default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# reference_Panneau
class PanneauReference(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    panneau = models.OneToOneField(
        Panneau,
        on_delete=models.CASCADE,
        related_name="panneau_reference",
    )
    checked_data = models.BooleanField(default=False)
    checked_state = models.BooleanField(default=False)
    duration = models.CharField(max_length=100, null=True, blank=True)
    energy = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
