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

def cleaner(data, key):
    ret = []
    for element in data:
        ret.append(element[key])
    return ret

# field
# try stringrelatedfield ??
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
        return cleaner(User(qset, many=True, fields='name').data, 'name')

    def get_blockeds(self, obj):
        qset = obj.get_outbox(status=mod.UserRelation.Types.BLOCK)
        return cleaner(UserRelation(qset, many=True, fields='to_user').data, 'to_user')
    
    def get_invitations(self, obj):
        qset = obj.get_outbox(status=mod.UserRelation.Types.INVIT)
        return UserRelation(qset, many=True, fields='to_user').data

    def get_blocked_by(self, obj):
        qset = obj.get_inbox(status=mod.UserRelation.Types.BLOCK)
        return UserRelation(qset, many=True, fields='from_user').data

    def get_invited_by(self, obj):
        qset = obj.get_inbox(status=mod.UserRelation.Types.INVIT)
        return UserRelation(qset, many=True, fields='from_user').data

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

# ???
class RolesChoiceField(serializers.ChoiceField):
    def display_value(self, instance):
        return instance
    def to_representation(self, value):
        return str(mod.User.Roles(value).label)
    def to_internal_value(self, data):
        value = next((v for k, v in self.choices.items()), None)
        if value is not None:
            return value
        return super().to_internal_value(data)

class GroupShip(BaseSerializer):
    class Meta:
        model = mod.GroupShip
        fields = ['user', 'group', 'role', 'last_read']

    user = UserRelatedField(queryset=mod.User.objects.all())
    role = RolesChoiceField(choices=mod.User.Roles)



class Group(BaseSerializer):
    class Meta:
        model = mod.Group
        fields = ['id', 'name', 'owner', 'admins', 'members', 'restricts', 'messages']

    def get_owner(self, obj):
        qset = obj.get_members_by_role(mod.User.Roles.OWNER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_admins(self, obj):
        qset = obj.get_members_by_role(mod.User.Roles.ADMIN)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_members(self, obj):
        qset = obj.get_members_by_role(mod.User.Roles.WRITER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_restricts(self, obj):
        qset = obj.get_members_by_role(mod.User.Roles.READER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    owner = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    restricts = serializers.SerializerMethodField()

    messages = Message(many=True, required=False, fields='id author date body')


class GroupUpdater(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=mod.Group.objects.all())
    name = serializers.CharField(required=False, validators=[val.offensive_name])
    admins = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)
    members = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)
    restricts = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)
    remove = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.all()), allow_empty=True)


    def update(self, data):
        group = data['id']
        name = data.get('name', None)
        print(Group(group).data)

        if name is not None:
            group.name = name

        for member in data['admins']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.User.Roles.ADMIN})
            else:
                group.memberships.get(user=member).role = mod.User.Roles.ADMIN

        for member in data['members']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.User.Roles.WRITER})
            else:
                group.memberships.get(user=member).role = mod.User.Roles.WRITER

        for member in data['restricts']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.User.Roles.READER})
            else:
                group.memberships.get(user=member).role = mod.User.Roles.READER

        for member in data['remove']:
            group.members.remove(member)

        group.save()
        print(Group(group).data)




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
    



# event serializer
class EventBaseSerializer(serializers.Serializer):
    author = serializers.CharField(required=False)

    def create(self, data):
        pass
        # print(self.validated_data)



class EventContact(EventBaseSerializer):
    name = UserRelatedField(queryset=mod.User.objects.all())
    relation = serializers.ChoiceField(choices=mod.UserRelation.Types)
    operation = serializers.ChoiceField(choices=mod.Operations, required=False)


class EventStatus(EventBaseSerializer):
    status = serializers.ChoiceField(choices=mod.User.Status)


