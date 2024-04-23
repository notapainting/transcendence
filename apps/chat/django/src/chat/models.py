#chat/models.py
from typing import Any
from django.db import models
import uuid

from . import validators
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError


import logging
logger = logging.getLogger('django')

SEED = b'8d41fd76-abb5-48ba-b383-84082c3a7bdb'

@database_sync_to_async
def get_user_by_username(userName):
	return ChatUser.object.filter(name=userName)

import json
from django.core.serializers.json import DjangoJSONEncoder


class ChatUser(models.Model):

	id = models.UUIDField(primary_key=True, editable=False)
	name = models.CharField(max_length=20, unique=True)
	contact_list = models.ManyToManyField('self')
	blocked_list = models.ManyToManyField('self', related_name='blocked', symmetrical=False)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

	def json_contact(self):
		return {
			'contact': json.dumps(list(self.contact_list.all().values("id", "name")), cls=DjangoJSONEncoder)
		}

	def json_blocked(self):
		return {
			'blocked': json.dumps(list(self.blocked_list.all().values("id", "name")), cls=DjangoJSONEncoder)
		}
	
	def json_group(self):
		return {
			'groups': json.dumps(list(self.groups.all().values("id")), cls=DjangoJSONEncoder)
		}

	def json(self):
		return {
			'id': self.id,
			'name': self.name,
			'contact': json.dumps(list(self.contact_list.all().values("id", "name")), cls=DjangoJSONEncoder),
			'blocked': json.dumps(list(self.blocked_list.all().values("id", "name")), cls=DjangoJSONEncoder),
			'groups': json.dumps(list(self.groups.all().values("id")), cls=DjangoJSONEncoder),
		}

	def json_short(self):
		return {
			'id': self.id,
			'name': self.name,
		}


# see how to knoe number of manytomany item
class ChatGroup(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=200, validators=[validators.offensive_name])
	members = models.ManyToManyField(ChatUser, related_name='groups')

	def __str__(self):
		return self.name
	
	def json(self):
		return {
			'id': self.id,
			'name': self.name,
			'n': '0',
			'members': json.dumps(list(self.members.all().values("id", "name")), cls=DjangoJSONEncoder),
		}

	def json_short(self):
		return {
			'id': self.id,
			'name': self.name,
		}
	



# validate date message :
	# - no futur date
	# - timeline coherence ? message cant be older than previous one
# validate author (at higher level)
# validate conv (at higher level)
# validate body length (at higher level)
class ChatMessage(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	author = models.ForeignKey(ChatUser, verbose_name="Author", on_delete=models.CASCADE)

	date_save = models.DateTimeField(verbose_name="Record date", auto_now_add=True)
	date_pub = models.DateTimeField(verbose_name="Publication date",  auto_now_add=True, validators=[validators.validate_futur])

	respond_to = models.ForeignKey(
		'ChatMessage',
		on_delete=models.SET_NULL, 
		verbose_name="In response to",
		default=None, 
		null=True
		)

	group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)

	body = models.CharField(max_length=512)

	def __str__(self):
		return self.body



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
