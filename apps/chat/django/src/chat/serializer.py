from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
import chat.models as mod
import io
from uuid import uuid4

from django.utils import timezone

from channels.db import database_sync_to_async

import chat.validators as val

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


class UserRelation(BaseSerializer):
    class Meta:
        model = mod.UserRelation
        fields = ['from_user', 'to_user', 'status']
        
    from_user = UserRelatedField(queryset=mod.User.objects.all())
    to_user = UserRelatedField(queryset=mod.User.objects.all())
        

class User(BaseSerializer):
    class Meta:
        model = mod.User
        fields = ['name', 'contacts', 'groups']
        extra_kwargs = {
                            'groups': {'required': False}
                        }
    # contacts = UserRelation(many=True)#source='contacts', 


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
        fields = ['user', 'group', 'role', 'last_read']

    user = UserRelatedField(queryset=mod.User.objects.all())
    # group = Group(fields='id')

class Group(BaseSerializer):
    class Meta:
        model = mod.Group
        fields = ['id', 'name', 'members', 'messages']

    members = GroupShip(source='memberships', many=True, fields='user role')
    messages = Message(many=True, required=False, fields='id author date body')


class GroupCreate(serializers.Serializer):
    name = serializers.CharField(validators=[val.offensive_name])
    owner = UserRelatedField(queryset=mod.User.objects.all())
    admins = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)
    members = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)
    restricts = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)

    def create(self, validated_data):
        m = mod.Group.objects.create(name=validated_data['name'])
        m.members.add(validated_data['owner'], through_defaults={'role':mod.User.Roles.OWNER})
        
        for admin in validated_data['admins']:
            m.members.add(admin, through_defaults={'role':mod.User.Roles.ADMIN})
            
        for member in validated_data['members']:
            m.members.add(member, through_defaults={'role':mod.User.Roles.WRITER})
            
        for restrict in validated_data['restricts']:
            m.members.add(restrict, through_defaults={'role':mod.User.Roles.READER})
        m.save()
        return m



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
