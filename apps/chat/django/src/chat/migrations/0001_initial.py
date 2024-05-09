# Generated by Django 5.0.2 on 2024-05-07 16:24

import chat.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, validators=[chat.validators.offensive_name])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Publication date')),
                ('body', models.CharField(max_length=512)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.group')),
                ('respond_to', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='response', to='chat.message')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.user')),
            ],
            options={
                'ordering': ['-date'],
                'default_related_name': 'messages',
            },
        ),
        migrations.CreateModel(
            name='GroupShip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(choices=[(0, 'Reader'), (1, 'Writer'), (2, 'Admin'), (3, 'Owner')], default=1)),
                ('last_read', models.DateTimeField(default=None, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='chat.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupships', to='chat.user')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='groups', through='chat.GroupShip', to='chat.user'),
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('I', 'Invit'), ('B', 'Block'), ('C', 'Comrade')])),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbox', to='chat.user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='chat.user')),
            ],
            options={
                'unique_together': {('from_user', 'to_user')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='contacts',
            field=models.ManyToManyField(related_name='+', through='chat.UserRelation', to='chat.user'),
        ),
    ]