# Generated by Django 5.0.2 on 2024-04-14 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_service', '0005_rename_verification_key_customuser_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_42',
            field=models.BooleanField(default=False),
        ),
    ]
