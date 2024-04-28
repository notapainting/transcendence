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


class ChatUser(models.Model):
    def __str__(self):
        return self.name

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    contacts = models.ManyToManyField('self')
    blockeds = models.ManyToManyField('self', related_name='blocked', symmetrical=False)


class ChatGroup(models.Model):
    def __str__(self):
        return str(self.id)

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[validators.offensive_name])
    members = models.ManyToManyField(ChatUser, related_name='groups')

    
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
