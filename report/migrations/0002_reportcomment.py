# Generated by Django 4.2.4 on 2024-11-01 05:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportComment',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, max_length=700, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_Comment', to='report.report')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_Comment_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
