# chat/views/specialview.py
from django.http import  HttpResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.exceptions import ParseError

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.models as mod
import chat.utils as uti
import chat.enums as enu

from logging import getLogger
logger = getLogger('django')
channel_layer = get_channel_layer()


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


class TournamentAlertAPIView(View):
    def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            player_a = data['host']
            player_b = data['guest']
            async_to_sync(channel_layer.group_send)(player_a, {
                "type":enu.Event.Message.GAME,
                "author":player_b
                })
            async_to_sync(channel_layer.group_send)(player_b, {
                "type":enu.Event.Message.GAME,
                "author":player_a
                })
            return HttpResponse(status=200)
        except KeyError:
                return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist) as error:
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

# from chat -> invite to match
# from game -> trn alert when waiting for match