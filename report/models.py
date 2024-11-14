import uuid
from django.db import models
from users.models import ProfilUser

# Create your models here.
class Report(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    user = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        related_name="user_reports",
    )
    description = models.TextField(max_length=600, null=True, blank=True)
    priority = models.CharField(max_length=50, null=True, blank=True)
    closed = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class ReportComment(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    sender = models.ForeignKey(
        ProfilUser,
        on_delete=models.CASCADE,
        related_name="report_Comment_user",
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="report_Comment",
    )
    description = models.TextField(max_length=700, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class ReportState(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="report_state",
    )
    state = models.CharField(max_length=200, null=True, blank=True)
    value = models.CharField(max_length=200, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
