# Generated by Django 5.0.2 on 2024-04-06 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatuser_blocked_list_chatuser_contact_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatuser',
            name='buid',
            field=models.UUIDField(),
        ),
    ]
