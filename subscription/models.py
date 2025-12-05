import uuid
from django.db import models
from users.models import ProfilUser


# Create your models here.
class Subscription(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    user = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        related_name="subscription_user",
    )
    stockage_ensuel = models.CharField(max_length=200, null=True, blank=True)
    assistance = models.CharField(max_length=200, null=True, blank=True)
    entretien = models.CharField(max_length=200, null=True, blank=True)
    monitoring = models.CharField(max_length=200, null=True, blank=True)
    remote_control = models.CharField(max_length=200, null=True, blank=True)
    planing = models.CharField(max_length=200, null=True, blank=True)
    alert = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

class SubscriptionPrice(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="subscription_price",
    )
    price = models.CharField(max_length=200, null=True, blank=True)
    subscription_type = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)