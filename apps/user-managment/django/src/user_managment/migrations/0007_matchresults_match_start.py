# Generated by Django 5.0.2 on 2024-05-21 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_managment', '0006_matchresults_match_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchresults',
            name='match_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
