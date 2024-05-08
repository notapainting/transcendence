#chat/models.py

from django.db import models
from uuid import uuid4

import chat.validators as val
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Q



import logging
logger = logging.getLogger('django')


class Operations(models.TextChoices):
    ADD="a", "add"
    REMOVE="r", "remove"



class UserRelation(models.Model):
    class Types(models.TextChoices):
        INVIT="i"
        BLOCK="b"
        COMRADE="c"

    class Meta:
        unique_together = ('from_user', 'to_user')

    from_user = models.ForeignKey("User", related_name='outbox', on_delete=models.CASCADE)
    to_user = models.ForeignKey("User", related_name='inbox', on_delete=models.CASCADE)
    status = models.CharField(choices=Types)

    def __str__(self):
        return f'from {self.from_user.name} to {self.to_user.name}'


class User(models.Model):
    class Roles(models.IntegerChoices):
        READER = 0, 'restrict'
        WRITER = 1, 'member'
        ADMIN = 2, 'admin'
        OWNER = 3, 'owner'

    class Status(models.TextChoices):
        DISCONNECTED="d"
        ONLINE="o"
        AFK="a"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    contacts = models.ManyToManyField('self',
                                      through=UserRelation,
                                      symmetrical=False,
                                      related_name="+")

    def __str__(self):
        return self.name

    def update_relation(self, target, status=UserRelation.Types.INVIT):
        try :
            rel = self.outbox.get(from_user=self, to_user=target)
            rel.status = status
            rel.save()
        except ObjectDoesNotExist:
            self.outbox.create(to_user=target, status=status)

    def get_relation(self, target):
        try :
            return self.outbox.get(to_user=target).status
        except ObjectDoesNotExist:
            return None

    def delete_relation(self, target):
        self.outbox.get(to_user=target).delete()

    def get_outbox(self, status=None):
        if status is not None:
            return self.outbox.filter(status=status)
        else:
            return self.outbox.filter(Q(status='I') | Q(status='B'))

    def get_inbox(self, status=None):
        if status is not None:
            return self.inbox.filter(status=status)
        else:
            return self.inbox.filter(Q(status='I') | Q(status='B'))

    def get_contacts(self, status='C'):
        return self.contacts.filter(inbox__status=status)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[val.offensive_name])
    members = models.ManyToManyField(User, through='GroupShip', related_name='groups')

    def __str__(self):
        return str(self.id)

    def get_members_by_role(self, role=User.Roles.WRITER):
        return self.memberships.filter(role=role)





class GroupShip(models.Model):
    user = models.ForeignKey(User, related_name="groupships", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="memberships", on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=User.Roles, default=User.Roles.WRITER)
    last_read = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f'from {self.user.name} to {self.group.name}'


class Message(models.Model):
    class Meta:
        default_related_name = "messages"
        ordering = ["-date"]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name="Publication date")
    respond_to = models.ForeignKey(
        'Message',
        on_delete=models.SET_NULL, 
        related_name="response",
        default=None, 
        null=True
        )

    body = models.CharField(max_length=512)

    def __str__(self):
        return self.body







#     def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)

    # def delete(self,  *args, **kwargs):
        
    # 	return super().delete(args, kwargs)
 
    # def set_uuid(self):
    # 	if self.members == None:
    # 		raise ValidationError(
    # 			"Can't create Group uuid without users"
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
