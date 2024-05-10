from django.db.models import TextChoices
from chat.models import Relation as rel

class Event():
    def val(self):
        ret = []
        for i in self.choices:
            ret = ret + i.values
        return ret

    class Group(TextChoices):
        SUMMARY = 'group.summary'
        CREATE = 'group.create'
        CREATE_PRIVATE = 'group.create.private'
        UPDATE = 'group.update'

    class Contact(TextChoices):
        SUMMARY = 'contact.summary'
        UPDATE = 'contact.update'

    class Status(TextChoices):
        UPDATE = 'status.update'
        FETCH = 'status.fetch'

    class Message(TextChoices):
        TEXT = 'message.text'
        GAME = 'message.game'
        FETCH = 'message.fetch'

    choices = [Group, Contact, Status, Message]

# change to Event.Contact.Operations
class Operations(TextChoices):
    INVIT = rel.Types.INVIT
    BLOCK = rel.Types.BLOCK
    CONTACT = rel.Types.COMRADE
    REMOVE = "r", "remove"

class SpecialUser(TextChoices):
    ADMIN = 'admin'