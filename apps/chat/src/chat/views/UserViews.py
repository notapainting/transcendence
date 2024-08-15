# chat/views.py
from django.http import  HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.serializers import ValidationError as DrfValidationError
from rest_framework.exceptions import ParseError

from channels.db import database_sync_to_async

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.utils as uti

from logging import getLogger
logger = getLogger('base')

def _post_helper(data):
    s = ser.User(data=data)
    s.is_valid(raise_exception=True)
    s.create(s.validated_data)

def _get_helper(name=None, fields='name'):
    if name == None:
        qset = mod.User.objects.all()
        many = True
    else:
        qset = mod.User.objects.get(name=name)
        many = False
    return ser.User(qset, many=many, fields=fields).data

def _patch_helper(name, new_name, data_update):
    user = mod.User.objects.get(name=name)
    if new_name is not None:
        s = ser.User(user, data={'name':new_name}, partial=True)
        s.is_valid(raise_exception=True)
        s.update(s.validated_data)
        return 200
    if data_update is not None:
        s = event.ContactUpdate(data=data_update)
        s.is_valid(raise_exception=True)
        s.create(s.validated_data)
        return 200
    return 400

def _delete_helper(name):
    mod.User.objects.get(name=name).delete()

class UserApiView(View):
    async def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(data=request.body)
            await database_sync_to_async(_post_helper)(data)
            return HttpResponse(status=201)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def get(self, request, *args, **kwargs):
        try :
            data = await database_sync_to_async(_get_helper)(kwargs.get('name'), request.GET.get("fields", 'name'))
            data = uti.render_json(data)
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def patch(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            status = await database_sync_to_async(_patch_helper)(kwargs.get('name'), data.get('new_name'), data.get('contact', None))
            return HttpResponse(status=status)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    async def delete(self, request, *args, **kwargs):
        try :
            await database_sync_to_async(_delete_helper)(kwargs.get('name'))
            logger.info(f"user {name}, deleted")
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)
