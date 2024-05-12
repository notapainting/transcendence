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
        UPDATE = 'group.update'
        QUIT = 'group.quit'
        DELETE = 'group.delete'

    class Contact(TextChoices):
        SUMMARY = 'contact.summary'
        UPDATE = 'contact.update'

    class Status(TextChoices):
        UPDATE = 'status.update'
        FETCH = 'status.fetch'

    class Message(TextChoices):
        FIRST = 'message.first'
        TEXT = 'message.text'
        FETCH = 'message.fetch'
        GAME = 'message.game'

    choices = [Group, Contact, Status, Message]

# change to Event.Contact.Operations
class Operations(TextChoices):
    INVIT = rel.Types.INVIT
    BLOCK = rel.Types.BLOCK
    CONTACT = rel.Types.COMRADE
    REMOVE = "remove"

class SpecialUser(TextChoices):
    ADMIN = 'admin'
    SYSTEM = 'system'
