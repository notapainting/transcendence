from django.db.models.signals import post_migrate
from django.conf import settings
from django.dispatch import receiver
from chat.models import User 
import chat.enums as enu

from logging import getLogger
logger = getLogger('base')


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    for user in enu.SpecialUser.values:
        if not User.objects.filter(name=user).exists():
            user = User.objects.create(name=user)
            logger.info(f"Special user: {user} created")
    