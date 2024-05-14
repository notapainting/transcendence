# chat/consumers/utils.py

from channels.db import database_sync_to_async

from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection
from rest_framework.serializers import ValidationError as DrfValidationError

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.enums as enu


# faire getgrouplist + ser group summary better

async def validate_data(username, data):
    type = data.get('type', None)
    data = data.get('data', None)
    if type is None or data is None:
        raise DrfValidationError("invalid event")
    data['author'] = username
    if type in enu.Event.val(enu.Event):
        return type
    else:
        raise DrfValidationError(f"event type unknow : {type}")

async def get_serializer(type):
    serializers = {
        enu.Event.Message.FIRST : event.MessageFirst,
        enu.Event.Message.FETCH : event.MessageFetch,
        enu.Event.Message.TEXT : ser.Message,
        enu.Event.Status.UPDATE : event.Status,
        enu.Event.Contact.UPDATE : event.ContactUpdate,
        enu.Event.Group.CREATE : event.GroupCreate,
        enu.Event.Group.UPDATE : event.GroupUpdate,
    }
    return serializers[type]


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
        return {"type":enu.Event.Contact.SUMMARY, "data":ser.User(user, fields=fields).data}

@database_sync_to_async
def get_group_list(user, fields='id'):
    pass

@database_sync_to_async
def serializer_wrapper(serializer, data):
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data


    
