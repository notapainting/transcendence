# Generated by Django 5.0.2 on 2024-05-05 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userrelation',
            old_name='type',
            new_name='status',
        ),
    ]
