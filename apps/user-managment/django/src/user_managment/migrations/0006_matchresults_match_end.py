# Generated by Django 5.0.2 on 2024-05-21 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_managment', '0005_alter_matchresults_user_one_powerups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchresults',
            name='match_end',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
