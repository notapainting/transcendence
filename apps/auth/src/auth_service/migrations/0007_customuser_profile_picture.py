# Generated by Django 5.0.2 on 2024-04-14 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_service', '0006_customuser_is_42'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
