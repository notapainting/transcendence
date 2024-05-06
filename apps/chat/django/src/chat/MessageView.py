from django.http import JsonResponse, HttpResponse
from chat.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from json import loads as jloads
from logging import getLogger
from django.db.models import Count

import chat.serializer as ser

logger = getLogger('django')

    # path("", MessageApiView.as_view()),
    # path("<uuid:id>", MessageApiView.as_view()), # -> return message data (author/date/group/body)
    # path("<uuid:id>/body/", MessageApiView.as_view()), # -> return message body


class MessageApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            s = ser.Message(data=request.body)
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

    def get(self, *args, **kwargs):
        pass

    def patch(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


