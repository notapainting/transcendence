# chat/views/relview.py
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

class RelationApiView(View):
    def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            target = mod.User.objects.get(name=data['target'])
            author = mod.User.objects.get(name=data['author'])
            if target.get_relation(author) == mod.Relation.Types.BLOCK:
                return HttpResponse(status=403)
            return HttpResponse(status=200)
        except KeyError:
                return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)
