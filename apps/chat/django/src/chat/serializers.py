from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
import io
from uuid import uuid4

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Prefetch
from django.db.models import Q

from channels.db import database_sync_to_async

import chat.validators as val
import chat.models as mod
import chat.enums as enu

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


class Relation(BaseSerializer):
    class Meta:
        model = mod.Relation
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
        qset = obj.get_outbox(status=mod.Relation.Types.BLOCK)
        return cleaner(Relation(qset, many=True, fields='to_user').data, 'to_user')
    
    def get_invitations(self, obj):
        qset = obj.get_outbox(status=mod.Relation.Types.INVIT)
        return cleaner(Relation(qset, many=True, fields='to_user').data, 'to_user')

    def get_blocked_by(self, obj):
        qset = obj.get_inbox(status=mod.Relation.Types.BLOCK)
        return cleaner(Relation(qset, many=True, fields='from_user').data, 'from_user')

    def get_invited_by(self, obj):
        qset = obj.get_inbox(status=mod.Relation.Types.INVIT)
        return cleaner(Relation(qset, many=True, fields='from_user').data, 'from_user')

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

    author = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser), required=False)
    group = serializers.PrimaryKeyRelatedField(
                queryset=mod.Group.objects.all(),
                required=True,
                allow_null=False,
                pk_field=serializers.UUIDField(format='hex_verbose'))

    def validate(self, data):
        if mod.GroupShip.objects.filter(
                group=data['group'], 
                user__name=data['author'], 
                role__gt=mod.GroupShip.Roles.READER).exists() is False: 
            raise ValidationError('user unauthorised t owrite in this group', code=403)
        return data


# ???
class RolesChoiceField(serializers.ChoiceField):
    def display_value(self, instance):
        return instance
    def to_representation(self, value):
        return str(mod.GroupShip.Roles(value).label)
    def to_internal_value(self, data):
        value = next((v for k, v in self.choices.items()), None)
        if value is not None:
            return value
        return super().to_internal_value(data)

class GroupShip(BaseSerializer):
    class Meta:
        model = mod.GroupShip
        fields = ['user', 'group', 'role', 'last_read']

    user = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    role = RolesChoiceField(choices=mod.GroupShip.Roles)


# drop owner and co if name == '@'
class Group(BaseSerializer):
    class Meta:
        model = mod.Group
        fields = ['id', 'name', 'owner', 'admins', 'members', 'restricts', 'messages']

    def get_owner(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.OWNER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_admins(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.ADMIN)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_members(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.WRITER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_restricts(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.READER)
        return cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    owner = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    restricts = serializers.SerializerMethodField()
    messages = Message(many=True, required=False, fields='id author date body')


# event serializer

class EventBaseSerializer(serializers.Serializer):
    author = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))

    def create(self, data):
        print(self.validated_data)

class EventContact(EventBaseSerializer):
    name = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    operation = serializers.ChoiceField(choices=enu.Operations)

class EventStatus(EventBaseSerializer):
    status = serializers.ChoiceField(choices=mod.User.Status)

class EventGroupCreatePrivate(EventBaseSerializer):
    target = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    body = serializers.CharField(required=False)

    def validate(self, data):
        if data['author'] == data['target']:
            raise ValidationError('no pgroup with yourself!', code=403)
        if mod.Group.objects.filter(name='@').filter(members__name=data['author']).filter(members__name=data['target']).exists() is True:
            raise ValidationError('pgroup already exist', code=403)
        return data


class EventGroupCreate(EventBaseSerializer):
    name = serializers.CharField(validators=[val.offensive_name, val.special_name])
    admins = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    members = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    restricts = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)

    def create(self, validated_data):
        group = mod.Group.objects.create(name=validated_data['name'])
        group.members.add(validated_data['author'], through_defaults={'role':mod.GroupShip.Roles.OWNER})
        for admin in validated_data['admins']:
            group.members.add(admin, through_defaults={'role':mod.GroupShip.Roles.ADMIN})
        for member in validated_data['members']:
            group.members.add(member, through_defaults={'role':mod.GroupShip.Roles.WRITER})
        for restrict in validated_data['restricts']:
            group.members.add(restrict, through_defaults={'role':mod.GroupShip.Roles.READER})
        group.save()
        return group

class EventGroupUpdate(EventBaseSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=mod.Group.objects.all())
    name = serializers.CharField(required=False, validators=[val.offensive_name])
    admins = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    members = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    restricts = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    remove = serializers.ListField(child=UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)

    def create(self, data):
        group = data['id']
        name = data.get('name', None)
        if name is not None:
            group.name = name
        for member in data['admins']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.GroupShip.Roles.ADMIN})
            else:
                group.memberships.get(user=member).role = mod.GroupShip.Roles.ADMIN
        for member in data['members']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.GroupShip.Roles.WRITER})
            else:
                group.memberships.get(user=member).role = mod.GroupShip.Roles.WRITER
        for member in data['restricts']:
            if group.members.filter(id=member.id).exists() is False:
                group.members.add(member, through_defaults={'role':mod.GroupShip.Roles.READER})
            else:
                group.memberships.get(user=member).role = mod.GroupShip.Roles.READER
        for member in data['remove']:
            group.members.remove(member)
        group.save()
        print(Group(group).data)
        return group



