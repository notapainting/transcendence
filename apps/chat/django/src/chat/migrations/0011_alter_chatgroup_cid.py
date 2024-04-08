# Generated by Django 5.0.2 on 2024-04-08 08:50

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_rename_buid_chatuser_uid_alter_chatgroup_cid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='cid',
            field=models.UUIDField(default=uuid.UUID('19324fca-0583-4fdd-a455-618cc3e0860a'), verbose_name='ChatGroup UUID'),
        ),
    ]
