from django.db.models.signals import post_migrate
from django.conf import settings
from django.dispatch import receiver
from chat.models import User 


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if not User.objects.filter(name=settings.ADMIN_USERNAME).exists():
        user = User.objects.create(
            name=settings.ADMIN_USERNAME,
        )
        print("Admin user created")
    if not User.objects.filter(name='islem').exists():
        user = User.objects.create(
            name='islem',
        )
        print("islem user created")
    if not User.objects.filter(name='lael').exists():
        user = User.objects.create(
            name='lael',
        )
        print("Laël user created")
    if not User.objects.filter(name='loulou').exists():
        user = User.objects.create(
            name='loulou',
        )
        print("Loulou user created")
    if not User.objects.filter(name='bilel').exists():
        user = User.objects.create(
            name='bilel',
        )
        print("Bilel user created")