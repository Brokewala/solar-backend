import uuid
from django.db import models
from users.models import ProfilUser


# Create your models here.
class Rating(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    user = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="rating_user",
    )

    score = models.IntegerField(
        blank=True,
        null=True,
    )
    comment = models.TextField(max_length=500)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
