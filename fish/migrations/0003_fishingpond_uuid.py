# Generated by Django 5.1 on 2024-08-30 16:11

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fish", "0002_alter_fishingpond_image_base64_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fishingpond",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="唯一标识符"
            ),
        ),
    ]
