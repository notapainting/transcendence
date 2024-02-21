from django.db import models

# Create your models here.
class getFormInformation(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique = True)
    