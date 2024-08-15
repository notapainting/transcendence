from django.http import HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.serializers import ValidationError as DrfValidationError
from rest_framework.exceptions import ParseError

from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


import chat.serializers.db as ser
import chat.models as mod
import chat.utils as uti
import chat.enums as enu

from logging import getLogger
logger = getLogger('base')
_channel_layer = get_channel_layer()

def _post_helper(data):
    s = ser.Message(data=data)
    s.is_valid(raise_exception=True)
    s.create(s.validated_data)
    return s.data

def _get_helper(id, fields='__all__'):
    qset = mod.Message.objects.get(id=id)
    return ser.Message(qset, fields=fields).data

def _patch_helper(id, data):
    message = mod.Message.objects.get(id=id)
    s = ser.Message(message, data=data, partial=True)
    s.is_valid(raise_exception=True)
    s.update(s.instance, s.validated_data)

def _delete_helper(id):
    mod.Message.objects.get(id=id).delete()

class MessageApiView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = uti.parse_json(request.body)
            data = await database_sync_to_async(_post_helper)(data)
            _channel_layer.group_send(data['group'], {'type':enu.Event.Message.TEXT, 'data':data})
            return HttpResponse(status=201)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def get(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id', None)
            if id is None:
                return HttpResponse(status=400)
            data = await database_sync_to_async(_get_helper)(id, request.GET.get("fields", '__all__'))
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def patch(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id is None:
                return HttpResponse(status=400)
            data = uti.parse_json(request.body)
            await database_sync_to_async(_patch_helper)(id, data)
            return HttpResponse(status=200)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def delete(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id is None:
                return HttpResponse(status=400)
            await database_sync_to_async(_delete_helper)(id)
            logger.info(f"message {id}, deleted")
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

