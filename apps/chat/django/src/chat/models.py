#chat/models.py
from django.db import models
import uuid

from . import validators
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

SEED = b'8d41fd76-abb5-48ba-b383-84082c3a7bdb'

@database_sync_to_async
def get_user_by_username(userName):
	return ChatUser.object.filter(name=userName)

def create_deleted_user(user):
	deleted_user = ChatUser(user)
	deleted_user.name = 'deleted' #use seed + username for uuid5
	deleted_user.save()
	return deleted_user


class ChatUser(models.Model):

	buid = models.UUIDField(default=uuid.uuid4) #primary_key=True,
	name = models.CharField(max_length=20, unique=True)
	contact_list = models.ManyToManyField('ChatUser', related_name='contact')
	blocked_list = models.ManyToManyField('ChatUser', related_name='blocked')

	def __str__(self):
		return self.name


class ChatGroup(models.Model):

	uuid = models.UUIDField(verbose_name='ChatGroup UUID, generate from seed + usernames')
	name = models.CharField(max_length=200, validators=[validators.offensive_name])
	participants = models.ManyToManyField(ChatUser, related_name='conv')

	def __str__(self):
		return self.name
	
	def set_uuid(self):
		if self.participants == None:
			raise ValidationError(
				"Can't create ChatGroup uuid without users"
			)
		key = '';
		for users in participants:
			key += users.name
		self.uuid = uuid.uuid5(SEED, key)
	
	def save(self, *args, **kwargs):
		self.set_uuid(self)
		self.full-clean()
		super().save(*args, **kwargs)


# validate date message :
	# - no futur date
	# - timeline coherence ? message cant be older than previous one
# validate author (at higher level)
# validate conv (at higher level)
# validate body length (at higher level)
class ChatMessage(models.Model):

	uuid = models.UUIDField(default=uuid.uuid4) #primary_key=True, 

	author = models.ForeignKey(ChatUser, verbose_name="Author", on_delete=models.CASCADE)

	date_save = models.DateTimeField(verbose_name="Record date", auto_now_add=True)
	date_pub = models.DateTimeField(verbose_name="Publication date", validators=[validators.validate_futur])

	respond_to = models.ForeignKey(
		'ChatMessage',
		on_delete=models.SET_NULL, 
		verbose_name="In response to",
		default=None, 
		null=True
		)

	conv = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)

	body = models.CharField(max_length=512)

	def __str__():
		pass







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
