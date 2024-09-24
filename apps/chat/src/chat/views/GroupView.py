from django.http import HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.serializers import ValidationError as DrfValidationError
from rest_framework.exceptions import ParseError

from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.enums as enu
import chat.utils as uti

from logging import getLogger
logger = getLogger('base')
_channel_layer = get_channel_layer()

def _post_helper(data):
    s = event.GroupCreate(data=data)
    s.is_valid(raise_exception=True)
    s.create(s.validated_data)
    return s.data

def _get_helper(id=None, fields='name id'):
    if id == None:
        qset = mod.Group.objects.all()
        many = True
    else:
        qset = mod.Group.objects.get(id=id)
        many = False
    return ser.Group(qset, many=many, fields=fields).data

def _patch_helper(data):
    s = event.GroupUpdate(data=data)
    s.is_valid(raise_exception=True)
    s.update(s.validated_data)

def _delete_helper(id):
    group = mod.Group.objects.get(id=id)
    group_data = ser.Group(group).data
    group.delete()
    return group_data

class GroupApiView(View):
    async def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            data = await database_sync_to_async(_post_helper)(data)
            for user in data['members']:
                await _channel_layer.group_send(user, {'type':enu.Event.Group.UPDATE, 'data':data})
            return HttpResponse(status=201, content=uti.render_json({'id':data['id']}))
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
            data = await database_sync_to_async(_get_helper)(kwargs.get('id'), request.GET.get("fields", 'name id'))
            data = uti.render_json(data)
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def patch(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            await database_sync_to_async(_patch_helper)(data)
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
            group_id = kwargs.get('id')
            members = await database_sync_to_async(_delete_helper)(group_id)
            for user in members:
                await _channel_layer.group_send(user, {'type':enu.Event.Group.DELETE, 'data':str(group_id)})
            logger.info("group %s, deleted", group_id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)
