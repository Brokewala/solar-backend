import uuid
from django.db import models
from users.models import ProfilUser

# Create your models here.
class Notification(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    user = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="notif_user",
    )
    fonction = models.CharField(max_length=100, null=True, blank=True)
    message = models.CharField(max_length=300, null=True, blank=True)
    read = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
