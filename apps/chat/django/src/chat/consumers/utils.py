# chat/consumers/utils.py

from channels.db import database_sync_to_async

from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection
from rest_framework.serializers import ValidationError as DrfValidationError

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.enums as enu
import chat.utils as uti


# faire getgrouplist + ser group summary better

async def validate_data(username, data):
    type = data.get('type', None)
    data = data.get('data', None)
    if data is None:
        raise DrfValidationError("malformed event", code=404)
    data['author'] = username
    if type in enu.Event.CLIENT:
        return type
    else:
        raise DrfValidationError(f"event type unknow : {type}", code=404)

async def get_serializer(type):
    serializers = {
        enu.Event.Message.FIRST : event.MessageFirst,
        enu.Event.Message.READ : event.MessageRead,
        enu.Event.Message.TEXT : ser.Message,
        enu.Event.Message.FETCH : event.MessageFetch,
        enu.Event.Status.UPDATE : event.Status,
        enu.Event.Contact.UPDATE : event.ContactUpdate,
        enu.Event.Group.CREATE : event.GroupCreate,
        enu.Event.Group.UPDATE : event.GroupUpdate,
    }
    return serializers[type]

@database_sync_to_async
def serializer_wrapper(serializer, data):
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data

# import datetime


@database_sync_to_async
def get_group_summary(user, n_messages=20):
    group_summary = {}
    group_summary['type'] = enu.Event.Group.SUMMARY
    group_summary['data'] = ser.Group(user.groups.all(), many=True).data
    for group in group_summary['data']:
        group['messages'] = group['messages'][:n_messages]
        date = user.groupships.get(group=group['id']).last_read
        if date is not None:
            group['last_read'] = date.strftime(ser.DATETIME_FORMAT)
        else:
            group['last_read'] = None
    return group_summary

@database_sync_to_async
def get_contact_summary(user):
    contact_summary = {}
    contact_summary['type'] = enu.Event.Contact.SUMMARY
    contact_summary['data'] = ser.User(user, fields='contacts blockeds blocked_by invitations invited_by').data
    return contact_summary


@database_sync_to_async
def get_contact_list(user):
        return ser.User(user, fields='contacts').data['contacts']

@database_sync_to_async
def get_group_list(user):
        return ser.User(user, fields='groups').data['groups']


