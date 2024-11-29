import uuid
from django.db import models
from users.models import ProfilUser

def upload_to(instance, filename):
    return "modules/{filename}".format(filename=filename)


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
    gr_code = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        default="grcode.jpg",
    )
    name = models.CharField(max_length=200,blank=True,null=True)
    identifiant = models.CharField(max_length=200,blank=True,null=True)
    password = models.CharField(max_length=200,blank=True,null=True)
    active = models.BooleanField(default=False)
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
