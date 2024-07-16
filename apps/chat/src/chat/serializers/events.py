# chat/serializers/events.py

from rest_framework import serializers

from rest_framework.serializers import ValidationError
from django.core.exceptions import ObjectDoesNotExist


import chat.enums as enu
import chat.models as mod
import chat.serializers.db as ser
import chat.utils as uti
import chat.validators as val


from logging import getLogger
logger = getLogger('django')


class BaseSerializer(serializers.Serializer):
    author = ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))

    def create(self, data):
        logger.info(f"EVENT {__name__}")

class Status(BaseSerializer):
    status = serializers.ChoiceField(choices=mod.User.Status)


class MessageFirst(BaseSerializer):
    target = ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    body = serializers.CharField(required=False)

    def validate(self, data):
        if data['author'] == data['target']:
            raise ValidationError('no pgroup with yourself!', code=403)
        if mod.Group.objects.filter(name='@').filter(members__name=data['author']).filter(members__name=data['target']).exists() is True:
            raise ValidationError('pgroup already exist', code=403)
        return data

    def create(self, data):
        group = uti.create_private_conv(data['author'], data['target'])
        if  data.get('body', None) is not None:
            first_message = ser.Message(data={'author':data['author'], 'group':group.id, 'body':data['body']})
            first_message.is_valid(raise_exception=True)
            first_message.create(first_message.validated_data)
        self.obj = group
        logger.info(f"CREATE private group {group.id} by {data['author']}")
        return group

    def to_representation(self, instance):
        return ser.Group(self.obj).data

class MessageRead(BaseSerializer):
    group = serializers.PrimaryKeyRelatedField(
                queryset=mod.Group.objects.all(),
                allow_null=False,
                pk_field=serializers.UUIDField(format='hex_verbose'))
    date = serializers.DateTimeField(format=ser.DATETIME_FORMAT)

    def validate(self, data):
        group = data['group']
        if group.memberships.filter(user=data['author']).exists() is False:
            raise ValidationError("can't fetch group message if not in", code=403)
        return data

    def create(self, data):
        membership = data['group'].memberships.get(user=data['author'])
        membership.last_read = data['date']
        membership.save()
        return data

class MessageFetch(BaseSerializer):
    group = serializers.PrimaryKeyRelatedField(
                queryset=mod.Group.objects.all(),
                allow_null=False,
                pk_field=serializers.UUIDField(format='hex_verbose'))
    date = serializers.DateTimeField(format=ser.DATETIME_FORMAT)

    def validate(self, data):
        group = data['group']
        if group.memberships.filter(user=data['author']).exists() is False:
            raise ValidationError("can't fetch group message if not in", code=403)
        return data

    def create(self, data):
        self.qset = data['group'].messages.filter(date__lt=data['date'])[:10]
        self.obj = ser.Message(self.qset, many=True).data
        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['history'] = self.obj
        return ret

class ContactUpdate(BaseSerializer):
    name = ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser))
    operation = serializers.ChoiceField(choices=enu.Operations)

    def validate(self, data):
        if data['author'] == data['name']:
            raise ValidationError('no self contact operation with yourself!', code=403)
        if data['operation'] in [enu.Operations.CONTACT, enu.Operations.INVIT]:
            if data['name'].get_relation(data['author']) is mod.Relation.Types.BLOCK:
                raise ValidationError('your blocked', code=403)
        return data

    def alter_pgroup_if_exist(self, userA, userB, new_role):
        try : 
            group = mod.Group.objects.filter(name='@').filter(members__name=userA).filter(members__name=userB).get()
            group.memberships.get(user=userA).role = new_role
            group.memberships.get(user=userB).role = new_role
            group.save()
            logger.info(f"UNBLOCK - pgroup :{group.id}")
        except ObjectDoesNotExist:
            pass

    def create(self, data):
        if data['operation'] == enu.Operations.DENY:
            target_rel = data['name'].get_relation(data['author'])
            if target_rel is not None and target_rel == mod.Relation.Types.INVIT:
                data['name'].delete_relation(data['author'])

        elif data['operation'] == enu.Operations.REMOVE:
            data['author'].delete_relation(data['name'])
            target_rel = data['name'].get_relation(data['author'])
            if target_rel is not None and target_rel != mod.Relation.Types.BLOCK:
                data['name'].delete_relation(data['author'])
                self.alter_pgroup_if_exist(data['author'], data['name'], mod.GroupShip.Roles.WRITER)

        elif data['operation'] == enu.Operations.BLOCK:
            self.alter_pgroup_if(data['author'], data['name'], mod.GroupShip.Roles.READER)
            data['author'].update_relation(data['name'], mod.Relation.Types.BLOCK)
            if data['name'].get_relation(data['author']) != mod.Relation.Types.BLOCK:
                data['name'].delete_relation(data['author'])

        else:
            if data['name'].get_relation(data['author']) == mod.Relation.Types.INVIT:
                data['author'].update_relation(data['name'], mod.Relation.Types.COMRADE)
                data['name'].update_relation(data['author'], mod.Relation.Types.COMRADE)
                data['operation'] = enu.Operations.CONTACT
            else:
                data['author'].update_relation(data['name'], mod.Relation.Types.INVIT)
                data['operation'] = enu.Operations.INVIT

        return data

class GroupCreate(BaseSerializer):
    name = serializers.CharField(validators=[val.offensive_name, val.special_name])
    admins = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    members = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    restricts = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)

    def create(self, data):
        group = mod.Group.objects.create(name=data['name'])
        group.members.add(data['author'], through_defaults={'role':mod.GroupShip.Roles.OWNER})
        for admin in data['admins']:
            group.members.add(admin, through_defaults={'role':mod.GroupShip.Roles.ADMIN})
        for member in data['members']:
            group.members.add(member, through_defaults={'role':mod.GroupShip.Roles.WRITER})
        for restrict in data['restricts']:
            group.members.add(restrict, through_defaults={'role':mod.GroupShip.Roles.READER})
        self.obj = group
        logger.info(f"CREATE group {group.id} by {data['author']}")
        return group
    
    def to_representation(self, instance):
        return ser.Group(self.obj).data

class GroupUpdate(BaseSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=mod.Group.objects.all())
    name = serializers.CharField(required=False, validators=[val.offensive_name])
    admins = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    members = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    restricts = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)
    remove = serializers.ListField(child=ser.UserRelatedField(queryset=mod.User.objects.exclude(name__in=enu.SpecialUser)), allow_empty=True)

    def validate(self, data):
        group = data['id']
        if group.memberships.filter(user=data['author']).exists() is False:
            raise ValidationError("can't update group if not in", code=403)
        if group.memberships.get(user=data['author']).role < mod.GroupShip.Roles.ADMIN:
            raise ValidationError("insuffisant permissions", code=403)
        return data

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
        self.obj = group
        logger.info(f"UPDATE group {group.id} by {data['author']}")
        return group
    
    def to_representation(self, instance):
        return ser.Group(self.obj).data


class GroupQuit(BaseSerializer):
    group = serializers.PrimaryKeyRelatedField(
                queryset=mod.Group.objects.all(),
                allow_null=False,
                pk_field=serializers.UUIDField(format='hex_verbose'))

    def validate(self, data):
        group = data['group']
        if group.memberships.filter(user=data['author']).exists() is False:
            raise ValidationError("can't quit group if not in", code=403)
        if group.name == '@':
            raise ValidationError("can't quit private conv", code=403)
        return data

    def create(self, data):
        group = data['group']
        role = group.memberships.get(user=data['author']).role
        group.memberships.remove(user=data['author'])
        if group.memberships.all().count() == 0:
            group.delete()
        elif role is mod.GroupShip.Roles.OWNER:
            if group.memberships.filter(role=mod.GroupShip.Roles.ADMIN).count() != 0:
                group.memberships.filter(role=mod.GroupShip.Roles.ADMIN).order_by("?").first().role = mod.GroupShip.Roles.OWNER
            elif group.memberships.filter(role=mod.GroupShip.Roles.WRITER).count() != 0:
                group.memberships.filter(role=mod.GroupShip.Roles.WRITER).order_by("?").first().role = mod.GroupShip.Roles.OWNER
            return data

