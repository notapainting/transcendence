# Generated by Django 5.0.2 on 2024-03-05 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='verification_key',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
    ]
