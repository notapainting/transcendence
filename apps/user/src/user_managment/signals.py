from django.db.models.signals import post_migrate
from django.conf import settings
from django.dispatch import receiver
from user_managment.models import CustomUser  # Assurez-vous que le chemin d'importation est correct
import requests

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if not CustomUser.objects.filter(username=settings.ADMIN_USERNAME).exists():
        user = CustomUser.objects.create_superuser(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
        )
