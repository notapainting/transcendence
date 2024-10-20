#chat/models.py

from django.db import models
from uuid import uuid4

import chat.validators as val
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now 
from django.db.models import Q

import logging
logger = logging.getLogger('base')


class Relation(models.Model):
    class Types(models.TextChoices):
        INVIT="invitation"
        BLOCK="block"
        COMRADE="contact"

    class Meta:
        unique_together = ('from_user', 'to_user')

    from_user = models.ForeignKey("User", related_name='outbox', on_delete=models.CASCADE)
    to_user = models.ForeignKey("User", related_name='inbox', on_delete=models.CASCADE)
    status = models.CharField(choices=Types)

    def __str__(self):
        return f"from {self.from_user.name} to {self.to_user.name}"

class User(models.Model):
    class Status(models.TextChoices):
        DISCONNECTED="disconnected"
        ONLINE="online"
        AFK="afk"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    contacts = models.ManyToManyField('self',
                                      through=Relation,
                                      symmetrical=False,
                                      related_name="+")

    def __str__(self):
        return self.name

    def update_relation(self, target, status=Relation.Types.INVIT):
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
        try:
            return self.outbox.get(to_user=target).delete()
        except ObjectDoesNotExist:
            return None

    def get_outbox(self, status=None):
        if status is not None:
            return self.outbox.filter(status=status)
        else:
            return self.outbox.filter(Q(status=Relation.Types.INVIT) | Q(status=Relation.Types.BLOCK))

    def get_inbox(self, status=None):
        if status is not None:
            return self.inbox.filter(status=status)
        else:
            return self.inbox.filter(Q(status=Relation.Types.INVIT) | Q(status=Relation.Types.BLOCK))

    def get_contacts(self, status=Relation.Types.COMRADE):
        return self.contacts.filter(inbox__status=status)

class GroupShip(models.Model):
    class Roles(models.IntegerChoices):
        READER = 0, 'restrict'
        WRITER = 1, 'member'
        ADMIN = 2, 'admin'
        OWNER = 3, 'owner'

    user = models.ForeignKey(User, related_name="groupships", on_delete=models.CASCADE)
    group = models.ForeignKey('Group', related_name="memberships", on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=Roles, default=Roles.WRITER)
    last_read = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"from {self.user.name} to {self.group.name}"

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, validators=[val.offensive_name])
    members = models.ManyToManyField(User, through=GroupShip, related_name='groups')

    def __str__(self):
        return str(self.id)

    def get_members_by_role(self, role=GroupShip.Roles.WRITER):
        return self.memberships.filter(role=role)


class Message(models.Model):
    class Meta:
        default_related_name = "messages"
        ordering = ["-date"]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
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

