# Generated by Django 5.0.2 on 2024-04-08 11:34

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0013_alter_chatgroup_gid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='gid',
            field=models.UUIDField(default=uuid.UUID('a6c1e50e-3587-470c-9a26-c30c8e68805b'), unique=True, verbose_name='ChatGroup ID'),
        ),
    ]
