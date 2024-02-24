from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
	isVerified = models.BooleanField(default = False)
	emailToken = models.CharField(max_length=100, blank = True, null = True)