# Generated by Django 5.0.2 on 2024-04-08 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_managment', '0002_customuser_date_of_birth_customuser_gender_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='unique_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
