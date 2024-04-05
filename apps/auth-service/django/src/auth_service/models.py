from django.db import models
from django.contrib.auth.models import AbstractUser





class CustomUser(AbstractUser):
    isVerified = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=100, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)

class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tokens')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)