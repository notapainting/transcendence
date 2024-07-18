from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now 


class CustomUser(AbstractUser):
	isVerified = models.BooleanField(default = False)
	profile_picture = models.ImageField(upload_to="", null=True, blank=True)
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
	

class Match(models.Model):
    class Meta:
        default_related_name = "match"
        ordering = ["-date"]

    winner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='won_match')
    loser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lost_match')
    score_w = models.IntegerField()
    score_l = models.IntegerField()
    date = models.DateTimeField(default=now)
