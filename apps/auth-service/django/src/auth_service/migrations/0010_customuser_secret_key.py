# Generated by Django 5.0.2 on 2024-04-19 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_service', '0009_rename_user_picture_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='secret_key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]