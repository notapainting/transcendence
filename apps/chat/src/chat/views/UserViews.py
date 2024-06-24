# chat/views.py
from django.http import  HttpResponse
from django.views import View

from rest_framework.serializers import ValidationError as DrfValidationError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import ParseError

from channels.db import database_sync_to_async
from django.views.decorators.csrf import csrf_exempt

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.utils as uti

from logging import getLogger
logger = getLogger('django')


class UserApiView(View):

    @csrf_exempt
    @database_sync_to_async
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(data=request.body)
            s = ser.User(data=data)
            s.is_valid(raise_exception=True)
            s.create(s.validated_data)
            return HttpResponse(status=201)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        many = False
        safe = True
        try :
            name = kwargs.get('name')
            fields = request.GET.get("fields")
            if name == None:
                qset = mod.User.objects.all()
                many = True
                safe = False
            else:
                qset = mod.User.objects.get(name=name)
            data = ser.User(qset, many=many, fields=fields).data
            data = uti.render_json(data)
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def patch(self, request, *args, **kwargs):
        try :
            user = mod.User.objects.get(name=kwargs.get('name'))
            data = uti.parse_json(request.body)
            new_name = data.get('new_name')
            if new_name is not None:
                s = ser.User(user, data={'name':new_name}, partial=True)
                s.is_valid(raise_exception=True)
                s.update(s.validated_data)
                return HttpResponse(status=200)
            data_update = data.get('contact', None)
            if data_update is not None:
                s = event.ContactUpdate(data=data_update)
                s.is_valid(raise_exception=True)
                s.create(s.validated_data)
                return HttpResponse(status=200)
            return HttpResponse(status=400)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            name = kwargs.get('name')
            mod.User.objects.get(name=name).delete()
            logger.info(f"user {name}, deleted")
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)
