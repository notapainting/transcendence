# Generated by Django 5.0.2 on 2024-04-14 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_service', '0008_remove_customuser_profile_picture_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='user_picture',
            new_name='profile_picture',
        ),
    ]
