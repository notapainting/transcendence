# Generated by Django 5.0.2 on 2024-04-29 19:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_chatmessage_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatuser',
            old_name='blocked_list',
            new_name='blockeds',
        ),
        migrations.RenameField(
            model_name='chatuser',
            old_name='contact_list',
            new_name='contacts',
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Publication date'),
        ),
    ]