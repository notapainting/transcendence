from django.http import HttpResponse
from django.views import View


from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError


from django.views.decorators.csrf import csrf_exempt
from logging import getLogger

import chat.serializers.db as ser
import chat.models as mod
import chat.utils as uti

logger = getLogger('django')

 
class MessageApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            data = uti.parse_json(request.body)
            s = ser.Message(data=data)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            print(s.validated_data)
            s.create(s.validated_data)
            return HttpResponse(status=201)
        
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
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
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def patch(self, request, *args, **kwargs):
        try :
            message = mod.Message.objects.get(id=kwargs.get('id'))
            data = uti.parse_json(request.body)
            s = ser.Message(message, data=data, partial=True)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            print(s.validated_data)
            s.update(s.instance, s.validated_data)
            return HttpResponse(status=200)

        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            id = request.GET.get("id")
            mod.Message.objects.get(id=id).delete()
            logger.info("message %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)


