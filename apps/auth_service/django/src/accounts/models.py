from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
	isVerified = models.BooleanField(default = False)
	email = models.EmailField(unique=True)