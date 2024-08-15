from django.http import HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.serializers import ValidationError as DrfValidationError
from rest_framework.exceptions import ParseError

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.views.decorators.csrf import csrf_exempt

import chat.serializers.db as ser
import chat.models as mod
import chat.utils as uti
import chat.enums as enu

from logging import getLogger
logger = getLogger('django')
_channel_layer = get_channel_layer()
 
class MessageApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            data = uti.parse_json(request.body)
            s = ser.Message(data=data)
            s.is_valid(raise_exception=True)
            s.create(s.validated_data)
            async_to_sync(_channel_layer.group_send)(s.data['group'], {'type':enu.Event.Message.TEXT, 'data':s.data})
            return HttpResponse(status=201)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            fields = request.GET.get("fields")
            id = kwargs.get('id', None)
            if id is None:
                return HttpResponse(status=400)
            qset = mod.Message.objects.get(id=id)
            data = ser.Message(qset, fields=fields).data
            data = uti.render_json(data)
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def patch(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id is None:
                return HttpResponse(status=400)
            message = mod.Message.objects.get(id=id)
            data = uti.parse_json(request.body)
            s = ser.Message(message, data=data, partial=True)
            s.is_valid(raise_exception=True)
            s.update(s.instance, s.validated_data)
            return HttpResponse(status=200)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id is None:
                return HttpResponse(status=400)
            mod.Message.objects.get(id=id).delete()
            logger.info(f"message {id}, deleted")
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

