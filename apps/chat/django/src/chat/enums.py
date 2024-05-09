from django.db.models import TextChoices


class Event():
    def val(self):
        ret = []
        for i in self.choices:
            ret = ret + i.values
        return ret

    class Group(TextChoices):
        SUMMARY = 'group.summary'
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


class Operations(TextChoices):
    ADD="a", "add"
    REMOVE="r", "remove"

