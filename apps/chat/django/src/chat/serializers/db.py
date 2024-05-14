from rest_framework import serializers

from rest_framework.serializers import ValidationError
from uuid import uuid4

from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist


import chat.models as mod
import chat.enums as enu
import chat.utils as uti

from logging import getLogger
logger = getLogger('django')

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

# fields
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


# a check ??
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

# serializer
class BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None and fields != '__all__':
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

    def get_contacts(self, obj):
        qset = obj.get_contacts()
        return uti.cleaner(User(qset, many=True, fields='name').data, 'name')

    def get_blockeds(self, obj):
        qset = obj.get_outbox(status=mod.Relation.Types.BLOCK)
        return uti.cleaner(Relation(qset, many=True, fields='to_user').data, 'to_user')
    
    def get_invitations(self, obj):
        qset = obj.get_outbox(status=mod.Relation.Types.INVIT)
        return uti.cleaner(Relation(qset, many=True, fields='to_user').data, 'to_user')

    def get_blocked_by(self, obj):
        qset = obj.get_inbox(status=mod.Relation.Types.BLOCK)
        return uti.cleaner(Relation(qset, many=True, fields='from_user').data, 'from_user')

    def get_invited_by(self, obj):
        qset = obj.get_inbox(status=mod.Relation.Types.INVIT)
        return uti.cleaner(Relation(qset, many=True, fields='from_user').data, 'from_user')

    groups = serializers.PrimaryKeyRelatedField(queryset=mod.Group.objects.all(), 
                                                many=True, 
                                                pk_field=serializers.UUIDField(format='hex_verbose'),
                                                required=False)

    contacts = serializers.SerializerMethodField(required=False)
    blockeds = serializers.SerializerMethodField(required=False)
    blocked_by = serializers.SerializerMethodField(required=False)
    invitations = serializers.SerializerMethodField(required=False)
    invited_by = serializers.SerializerMethodField(required=False)


class Message(BaseSerializer):
    class Meta:
        model = mod.Message
        fields = ['id', 'author', 'group', 'date', 'respond_to', 'body']
        extra_kwargs = {
                'date': {'format': DATETIME_FORMAT, 'default': now},
                'id': {'format': 'hex_verbose', 'default': uuid4}
            }

    author = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser), required=False)
    group = serializers.PrimaryKeyRelatedField(
                queryset=mod.Group.objects.all(),
                allow_null=False,
                pk_field=serializers.UUIDField(format='hex_verbose'))

    def validate(self, data):
        if mod.GroupShip.objects.filter(
                group=data['group'], 
                user__name=data['author'], 
                role__gt=mod.GroupShip.Roles.READER).exists() is False: 
            raise ValidationError('user unauthorised to write in this group', code=403)
        return data


class GroupShip(BaseSerializer):
    class Meta:
        model = mod.GroupShip
        fields = ['user', 'group', 'role', 'last_read']

    user = UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    role = RolesChoiceField(choices=mod.GroupShip.Roles)


class Group(BaseSerializer):
    class Meta:
        model = mod.Group
        fields = ['id', 'name', 'owner', 'admins', 'members', 'restricts', 'messages']

    def get_owner(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.OWNER)
        return uti.cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_admins(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.ADMIN)
        return uti.cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_members(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.WRITER)
        return uti.cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    def get_restricts(self, obj):
        qset = obj.get_members_by_role(mod.GroupShip.Roles.READER)
        return uti.cleaner(GroupShip(qset, many=True, fields='user').data, 'user')

    owner = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    restricts = serializers.SerializerMethodField()
    messages = Message(many=True, required=False, fields='id author date body')

