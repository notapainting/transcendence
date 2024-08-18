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
        print("Admin user created")
    if not CustomUser.objects.filter(username='islem').exists():
        user = CustomUser.objects.create(
            username='islem',
            email='islem@islem.com',
        )
        print("islem user created")
    if not CustomUser.objects.filter(username='lael').exists():
        user = CustomUser.objects.create(
            username='lael',
            email='lael@lael.com',
        )
        print("lael user created")
    if not CustomUser.objects.filter(username='loulou').exists():
        user = CustomUser.objects.create(
            username='loulou',
            email='loulou@loulou.com',
        )
        print("loulou user created")
    if not CustomUser.objects.filter(username='bilel').exists():
        user = CustomUser.objects.create(
            username='bilel',
            email='bilel@bilel.com',
        )
        print("bilel user created")