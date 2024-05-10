#chat/utils/asynchronous.py

from rest_framework.serializers import ValidationError as DrfValidationError

import chat.serializers as ser
import chat.enums as enu


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
        enu.Event.Message.TEXT : ser.Message,
        enu.Event.Status.UPDATE : ser.EventStatus,
        enu.Event.Contact.UPDATE : ser.EventContact,
        enu.Event.Group.CREATE : ser.EventGroupCreate,
        enu.Event.Group.CREATE_PRIVATE : ser.EventGroupCreatePrivate,
        enu.Event.Group.UPDATE : ser.EventGroupUpdate,
    }
    return serializers[type]

