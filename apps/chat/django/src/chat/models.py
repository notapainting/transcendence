#chat/models.py

from django.db import models
from uuid import uuid4

from . import validators
from django.core.exceptions import ValidationError
from django.utils import timezone

import logging
logger = logging.getLogger('django')

SEED = b'8d41fd76-abb5-48ba-b383-84082c3a7bdb'



import json
from django.core.serializers.json import DjangoJSONEncoder


# class ChatUser(models.Model):
#     def __str__(self):
#         return self.name

#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     name = models.CharField(max_length=20, unique=True)
#     contacts = models.ManyToManyField('self')
#     blockeds = models.ManyToManyField('self', related_name='blocked_by', symmetrical=False)
#     invitations = models.ManyToManyField('self', related_name='invited_by', symmetrical=False)

class UserRelation(models.Model):
    class RelationType(models.TextChoices):
        INVIT="I"
        INVITED="ID"
        BLOCK="B"
        BLOCKED="BD"
        COMRADE="C"

    inverse = {
        RelationType.INVIT: RelationType.INVITED,
        RelationType.BLOCK: RelationType.BLOCKED,
        RelationType.COMRADE: RelationType.COMRADE,
    }

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'from {self.from_user.name} to {self.to_user.name}'

    from_user = models.ForeignKey("ChatUser", related_name='outbox', on_delete=models.CASCADE)
    to_user = models.ForeignKey("ChatUser", related_name='inbox', on_delete=models.CASCADE)
    status = models.CharField(choices=RelationType)

class ChatUser(models.Model):
    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    contacts = models.ManyToManyField('self',
                                      through=UserRelation,
                                      symmetrical=False,
                                      related_name="+")

    def add_relationship(self, target, status=UserRelation.RelationType.INVIT, symm=True):
        relationship, created = UserRelation.objects.get_or_create(
            from_user=self,
            to_user=target)
        if symm is True and status == UserRelation.RelationType.COMRADE:
            target.add_relationship(self, status, False)
        return relationship


    def get_contacts_by_status(self, status='C'):
        return self.contacts.filter(
            inbox__status=status)


    def remove_relationship(self, target, symm=True):
        r = UserRelation.objects.get(
            from_user=self,
            to_user=target)
        
        if symm is True and r.status == UserRelation.RelationType.COMRADE:
            target.remove_relationship(self, False)
        r.delete()


class ChatGroup(models.Model):
    def __str__(self):
        return str(self.id)

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[validators.offensive_name])
    members = models.ManyToManyField(ChatUser, through='GroupShip', related_name='groups')

class GroupShip(models.Model):
    def __str__(self):
        return f'from {self.user.name} to {self.group.name}'

    user = models.ForeignKey(ChatUser, related_name="groupship", on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, related_name="groupships", on_delete=models.CASCADE)
    last_read = models.DateTimeField(default=None)

    
class ChatMessage(models.Model):
    def __str__(self):
        return self.body

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    author = models.ForeignKey(ChatUser, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now, verbose_name="Publication date")
    respond_to = models.ForeignKey(
        'ChatMessage',
        on_delete=models.SET_NULL, 
        related_name="response",
        default=None, 
        null=True
        )

    body = models.CharField(max_length=512)
    
    class Meta:
        default_related_name = "messages"
        ordering = ["-date"]







#     def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)

    # def delete(self,  *args, **kwargs):
        
    # 	return super().delete(args, kwargs)
 
    # def set_uuid(self):
    # 	if self.members == None:
    # 		raise ValidationError(
    # 			"Can't create ChatGroup uuid without users"
    # 		)
    # 	key = '';
    # 	for users in self.members:
    # 		key += users.name
    # 	self.uuid = uuid.uuid5(SEED, key)
 
    # def save(self, *args, **kwargs):
    # 	# self.set_uuid(self)
    # 	# self.full_clean()
    # 	super().save(*args, **kwargs)

# class C:
#     def __init__(self):
#         self._x = None

#     @property
#     def x(self):
#         """I'm the 'x' property."""
#         return self._x

#     @x.setter
#     def x(self, value):
#         self._x = value

#     @x.deleter
#     def x(self):
#         del self._x
