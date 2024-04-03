#chat/models.py
from django.db import models
import uuid

from . import validators


#add :
# contact list
# blocked list
#  conv list
class ChatUser(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=20)

	def __str__():
		pass


# validate date message :
	# - no futur date
	# - timeline coherence ? message cant be older than previous one
# validate author (at higher level)
# validate conv (at higher level)
# validate body length (at higher level)
class ChatMessage(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	author = models.OneToOneField(ChatUser, verbose_name="Author", on_delete=models.CASCADE)

	date_save = models.DateTimeField(verbose_name="Record date", auto_now_add=True)
	date_pub = models.DateTimeField(
		verbose_name="Publication date",
		validators=[validators.validate_futur]
		)

	respond_to = models.OneToOneField(
		'ChatMessage',
		verbose_name="In response to",
		on_delete=models.CASCADE, 
		db_default=None, 
		null=True
		)

	conv = models.OneToOneField('conv', on_delete=models.CASCADE)
	# maybe use textfield insteed ???
	body = models.CharField(max_length=512)

	def __str__():
		pass


# dont know if usefull ? conv are groups, groups are juste "name"
class Conv(models.Model):

	def __str__():
		pass