# Generated by Django 5.0.2 on 2024-07-15 17:38

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_managment', '0004_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_w', models.IntegerField()),
                ('score_l', models.IntegerField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('loser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lost_match', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='won_match', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'default_related_name': 'match',
            },
        ),
    ]
