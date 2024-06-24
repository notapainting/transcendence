from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    isVerified = models.BooleanField(default=False)
    unique_id = models.CharField(max_length=100, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    is_42 = models.BooleanField(default=False)
    profile_picture = models.CharField(max_length=300, null=True, blank=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True)
    oauth_id = models.CharField(max_length=255, unique=True, null=True)

class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tokens')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)