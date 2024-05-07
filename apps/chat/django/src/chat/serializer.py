from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
import chat.models as mod
import io
from uuid import uuid4

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Prefetch
from django.db.models import Q

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
        except ObjectDoesNotExist:
            raise ValidationError({'User': 'User not found'})


# serializer
class BaseSerializer(serializers.ModelSerializer):
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
        fields = ['name', 'contacts', 'groups', 'blockeds', 'blocked_by', 'invitations', 'invited_by']
        extra_kwargs = {
                            'groups': {'required': False},
                            'blockeds': {'required': False},
                            'blockeds_by': {'required': False},
                            'invitations': {'required': False},
                            'invited_by': {'required': False},
                        }

    def get_contacts(self, obj):
        qset = obj.get_contacts()
        ser = User(qset, many=True, fields='name')
        return ser.data

    def get_blockeds(self, obj):
        qset = obj.get_outbox(status=mod.UserRelation.Types.BLOCK)
        ser = UserRelation(qset, many=True, fields='to_user')
        return ser.data
    
    def get_invitations(self, obj):
        qset = obj.get_outbox(status=mod.UserRelation.Types.INVIT)
        ser = UserRelation(qset, many=True, fields='to_user')
        return ser.data

    def get_blocked_by(self, obj):
        qset = obj.get_inbox(status=mod.UserRelation.Types.BLOCK)
        ser = UserRelation(qset, many=True, fields='from_user')
        return ser.data

    def get_invited_by(self, obj):
        qset = obj.get_inbox(status=mod.UserRelation.Types.INVIT)
        ser = UserRelation(qset, many=True, fields='from_user')
        return ser.data

    contacts = serializers.SerializerMethodField()
    blockeds = serializers.SerializerMethodField()
    blocked_by = serializers.SerializerMethodField()
    invitations = serializers.SerializerMethodField()
    invited_by = serializers.SerializerMethodField()


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


class GroupCreater(serializers.Serializer):
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

class UserCreater(serializers.Serializer):
    name = UserRelatedField(queryset=mod.User.objects.all())
    new_name = serializers.CharField()
    


# event serializer
class EventBaseSerializer(serializers.Serializer):
    author = serializers.CharField(required=False)

    def create(self, data):
        pass
        # print(self.validated_data)



OPERATIONS = [
    ('a', 'add'),
    ('r', 'remove'),
]
class EventContact(EventBaseSerializer):
    name = UserRelatedField(queryset=mod.User.objects.all())
    relation = serializers.ChoiceField(choices=mod.UserRelation.Types)
    operation = serializers.ChoiceField(choices=OPERATIONS, required=False)


class EventStatus(EventBaseSerializer):
    status = serializers.ChoiceField(choices=mod.User.Status)


