# Generated by Django 5.0.2 on 2024-04-07 09:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_remove_chatgroup_uuid_chatgroup_cid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='cid',
            field=models.UUIDField(default=uuid.UUID('9c331d04-92bb-4ebb-8535-a144dc47d717'), verbose_name='ChatGroup UUID'),
        ),
    ]
