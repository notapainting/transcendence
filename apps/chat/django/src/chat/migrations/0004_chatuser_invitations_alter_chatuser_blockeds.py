# Generated by Django 5.0.2 on 2024-05-01 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_rename_blocked_list_chatuser_blockeds_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatuser',
            name='invitations',
            field=models.ManyToManyField(related_name='invited_by', to='chat.chatuser'),
        ),
        migrations.AlterField(
            model_name='chatuser',
            name='blockeds',
            field=models.ManyToManyField(related_name='blocked_by', to='chat.chatuser'),
        ),
    ]