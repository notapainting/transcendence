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
        CREATE  = 'group.create'
        UPDATE  = 'group.update'
        QUIT    = 'group.quit'
        DELETE  = 'group.delete'

    class Contact(TextChoices):
        SUMMARY = 'contact.summary'
        UPDATE  = 'contact.update'

    class Status(TextChoices):
        UPDATE  = 'status.update'
        FETCH   = 'status.fetch'

    class Message(TextChoices):
        FIRST   = 'message.first'
        TEXT    = 'message.text'
        FETCH   = 'message.fetch'
        GAME    = 'message.game'
        READ    = 'message.read'

    class Errors(TextChoices):
        ENCODE  = 'error.encode'
        DECODE  = 'error.decode'
        TYPE    = 'error.type'
        DATA    = 'error.data'
        HANDLER = 'error.handler'


    CLIENT = [
                Message.FIRST,
                Message.READ,
                Message.TEXT,
                Message.FETCH,
                Status.UPDATE,
                Contact.UPDATE,
                Group.CREATE,
                Group.UPDATE,
                Group.QUIT,
                Group.DELETE
        ]
    
    choices = [Group, Contact, Status, Message]

# change to Event.Contact.Operations
class Operations(TextChoices):
    INVIT   = rel.Types.INVIT
    BLOCK   = rel.Types.BLOCK
    CONTACT = rel.Types.COMRADE
    REMOVE  = "remove"
    DENY    = "deny"

class SpecialUser(TextChoices):
    ADMIN   = 'admin'
    SYSTEM  = 'system'
    TOURNAMENT = 'tournament'

class Self(TextChoices):
    LOCAL   = 'local'

