#chat/utils/db.py

from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection

import chat.serializers as ser
import chat.models as mod
import chat.enums as enu

@database_sync_to_async
def get_group_summary(user):
    group_list = []
    group_summary = {}
    group_summary['type'] = 'group.summary'
    group_summary['data'] = ser.Group(user.groups.all(), many=True).data
    for group in group_summary['data']:
        group_list.append(group['id'])
        group['messages'] = group['messages'][:2]
    return group_list, group_summary

@database_sync_to_async
def get_contact_list(user, fields='contacts'):
    if fields == 'contacts':
        return ser.User(user, fields=fields).data['contacts']
    else:
        return ser.User(user, fields=fields).data

@database_sync_to_async
def get_group_list(user, fields='id'):
    pass

@database_sync_to_async
def serializer_wrapper(serializer, data):
    print(data)
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data

@database_sync_to_async
def auth(name):
    try:
        return mod.User.objects.exclude(name__in=enu.SpecialUser).get(name=name)
    except ObjectDoesNotExist:
        raise DenyConnection

def create_private_conv(user1, user2):
    pgroup = mod.Group.objects.create(name='@')
    pgroup.members.set([user1, user2], through_defaults={'role':mod.GroupShip.Roles.WRITER})
    pgroup.members.add(mod.User.objects.get(name=enu.SpecialUser.ADMIN), through_defaults={'role':mod.GroupShip.Roles.OWNER})
    return pgroup


