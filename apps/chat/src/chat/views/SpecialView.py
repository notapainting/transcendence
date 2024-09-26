# chat/views/specialview.py
from django.http import  HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError


from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

import chat.models as mod
import chat.utils as uti

from logging import getLogger
logger = getLogger('base')
channel_layer = get_channel_layer()


def _relation_helper(author_name, target_name):
    author = mod.User.objects.get(name=author_name)
    target = mod.User.objects.get(name=target_name)
    if target.get_relation(author) == mod.Relation.Types.BLOCK:
        return 403
    return 200

class RelationApiView(View):
    async def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            status = await database_sync_to_async(_relation_helper)(data['author'], data['target'])
            return HttpResponse(status=status)
        except KeyError:
                return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)
