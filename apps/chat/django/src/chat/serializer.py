from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
import chat.models as mod
import io
from uuid import uuid4

from django.utils import timezone

from channels.db import database_sync_to_async

def parse_json(data):
    return JSONParser().parse(io.BytesIO(data))


def render_json(data):
        return (JSONRenderer().render(data))

# field
class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        try :
            return mod.User.objects.get(name=data)
        except BaseException:
            raise ValidationError({'User': 'User not found'})


# https://stackoverflow.com/questions/17256724/include-intermediary-through-model-in-responses-in-django-rest-framework/17263583#17263583
# serializer
class   BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            fields = fields.split()
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)



class User(BaseSerializer):
    class Meta:
        model = mod.User
        fields = ['name', 'contacts', 'blockeds', 'invitations', 'invited_by', 'groups']
        extra_kwargs = {
                            'groups': {'required': False}
                        }
    contacts = UserRelatedField(queryset=mod.User.objects.all(), many=True, required=False)
    blockeds = UserRelatedField(queryset=mod.User.objects.all(), many=True, required=False)
    invitations = UserRelatedField(queryset=mod.User.objects.all(), many=True, required=False)
    invited_by = UserRelatedField(queryset=mod.User.objects.all(), many=True, required=False)
    

# import chat.serializer as ser
# import chat.models as mod
# g = mod.GroupShip.objects.all().get(id=11)
# 
# 

# restrain group to users groups
class Message(BaseSerializer):
    class Meta:
        model = mod.Message
        fields = ['id', 'author', 'group', 'date', 'respond_to', 'body']
        extra_kwargs = {
            'date': {'format' : '%Y-%m-%dT%H:%M:%S.%fZ%z', 'default':timezone.now},
            'id': {'format' : 'hex_verbose', 'default': uuid4}
            }

    author = UserRelatedField(queryset=mod.User.objects.all(), required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=mod.Group.objects.all(),
                                            required=True,
                                            allow_null=False,
                                            pk_field=serializers.UUIDField(format='hex_verbose'))


class GroupShip(BaseSerializer):
    class Meta:
        model = mod.GroupShip
        fields = ['user', 'role', 'last_read']
    user = UserRelatedField(queryset=mod.User.objects.all())
    

class Group(BaseSerializer):
    class Meta:
        model = mod.Group
        fields = ['id', 'name', 'members', 'messages']

    members = GroupShip(source='memberships', many=True)
    # members = UserRelatedField(queryset=mod.User.objects.all(), many=True)
    messages = Message(many=True, required=False, fields='id author date body')


# event serializer
class EventBaseSerializer(serializers.Serializer):
    author = serializers.CharField(required=False)

    def create(self, data):
        pass
        # print(self.validated_data)


RELATIONS = [
    ('c', 'contact'),
    ('b', 'blocked'),
    ('i', 'invitation'),
]
OPERATIONS = [
    ('a', 'add'),
    ('r', 'remove'),
]
class EventContact(EventBaseSerializer):
    name = UserRelatedField(queryset=mod.User.objects.all())
    relation = serializers.ChoiceField(choices=RELATIONS)
    operation = serializers.ChoiceField(choices=OPERATIONS, required=False)

STATUS = [
    ('d', 'disconnected'),
    ('o', 'online'),
    ('a', 'afk'),
]
class EventStatus(EventBaseSerializer):
    status = serializers.ChoiceField(choices=STATUS)

# from client, invit is ignored

# if invit -> error 400




# -> send invit : if author already invited by target, 
#   -> accept and add to contact
# -> user not in db -> 404



content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'
