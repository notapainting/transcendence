# Generated by Django 5.0.2 on 2024-04-24 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_chatuser_contact_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='members',
            field=models.ManyToManyField(related_name='groups', to='chat.chatuser'),
        ),
        migrations.AlterField(
            model_name='chatuser',
            name='id',
            field=models.UUIDField(editable=False, primary_key=True, serialize=False),
        ),
    ]
