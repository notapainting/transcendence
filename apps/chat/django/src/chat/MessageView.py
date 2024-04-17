from django.http import JsonResponse, HttpResponse
from chat.models import ChatGroup, ChatUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from json import loads as jloads
from logging import getLogger
from django.db.models import Count

logger = getLogger('django')

    # path("", MessageApiView.as_view()),
    # path("<uuid:id>", MessageApiView.as_view()), # -> return message data (author/date/group/body)
    # path("<uuid:id>/body/", MessageApiView.as_view()), # -> return message body


class MessageApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            data = jloads(request.body)#can throw

            group = ChatGroup.objects.get(id=kwargs.get('id'))
            author = ChatUser.object.get(name=data['author'])
            respond_to ChatMessage.object.get(id=data['respond_to'])

            date_pub = data['date_pub']
            body = data['body']

            message = ChatMessage.object.create(author=author, 
                                                date_pub=pub, 
                                                conv=group, 
                                                respond_to=respond_to, 
                                                body=body)
            return HttpResponse(status=201)
        except KeyError as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


