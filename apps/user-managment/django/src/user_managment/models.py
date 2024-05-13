from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
	isVerified = models.BooleanField(default = False)
	profile_picture = models.ImageField(upload_to="", default="default_profile_picture.png")
	first_name = models.CharField(max_length=50, null=True, blank=True)
	last_name = models.CharField(max_length=50, null=True, blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	unique_id = models.CharField(max_length=100, blank=True)
	GENDER_CHOICES = (
		('M', 'Male'),
		('F', 'Female'),
		('O', 'Other'),
	)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)