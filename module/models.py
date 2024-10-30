import uuid
from django.db import models
from users.models import ProfilUser


# Create your models here.
class Modules(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    user = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="module_user",
    )
    gr_code = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200)
    identifiant = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class ModulesInfo(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    module = models.ForeignKey(
        Modules,
        on_delete=models.CASCADE,
        related_name="module_info",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class ModulesDetail(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    module_info = models.ForeignKey(
        ModulesInfo,
        on_delete=models.CASCADE,
        related_name="module_detail",
    )
    value = models.CharField(max_length=200)
    description = models.TextField(max_length=500, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
