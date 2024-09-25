from django.db.models.signals import post_migrate
from django.conf import settings
from django.dispatch import receiver
from chat.models import User 
import chat.enums as enu

from logging import getLogger
logger = getLogger('base')


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if not User.objects.filter(name=settings.ADMIN_USERNAME).exists():
        user = User.objects.create(
            name=settings.ADMIN_USERNAME,
        )
        logger.info("Admin user created")
    for user in enu.SpecialUser.values:
        if not User.objects.filter(name=user).exists():
            user = User.objects.create(name=user)
            logger.info(f"Special user: {user} created")
    
    if not User.objects.filter(name='islem').exists():
        user = User.objects.create(
            name='islem',
        )
        logger.info("islem user created")
    if not User.objects.filter(name='lael').exists():
        user = User.objects.create(
            name='lael',
        )
        logger.info("Laël user created")
    if not User.objects.filter(name='loulou').exists():
        user = User.objects.create(
            name='loulou',
        )
        logger.info("Loulou user created")
    if not User.objects.filter(name='bilel').exists():
        user = User.objects.create(
            name='bilel',
        )
        logger.info("Bilel user created")