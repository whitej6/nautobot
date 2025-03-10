# Generated by Django 3.2.14 on 2022-07-25 21:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.fields
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0042_job__add_is_job_hook_receiver"),
    ]

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("assigned_object_id", models.UUIDField(db_index=True)),
                ("user_name", models.CharField(editable=False, max_length=150)),
                (
                    "slug",
                    nautobot.core.fields.AutoSlugField(
                        blank=True, max_length=100, populate_from="assigned_object", unique=True
                    ),
                ),
                ("note", models.TextField()),
                (
                    "assigned_object_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="note",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
            },
        ),
    ]
