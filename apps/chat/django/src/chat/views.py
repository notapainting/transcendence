# chat/views.py
from django.http import JsonResponse, HttpResponse
from chat.models import ChatUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


import json

import logging
logger = logging.getLogger('django')

# TODO: move log in models



def is_uuid(val):
    from uuid import UUID
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False
    

# handle IntegrityError
class UserApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            data = json.loads(request.body)
            id = kwargs.get('id', data['id'])
            if ChatUser.objects.filter(Q(name=data['name']) | Q(uid=id)).exists():
                return HttpResponse(status=403)
            ChatUser.objects.create(uid=id, name=data['name'])
            return HttpResponse(status=201)
        except (ValidationError, KeyError) as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                return JsonResponse(status=200, data=ChatUser.objects.get(uid=kwargs['id']).json())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=kwargs['id']).json())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def put(self, request, *args, **kwargs):
        try :
            data = json.loads(request.body)
            id = kwargs.get('id', data['id'])
            user = ChatUser.objects.get(uid=id)
            if ChatUser.objects.filter(name=data['name']).exists():
                return HttpResponse(status=403)
            user.name = data['name']
            user.save()
            return HttpResponse(status=200)
        except (ValidationError, KeyError) as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id == 'all':
                ChatUser.objects.all().delete()
            else :
                ChatUser.objects.get(uid=id).delete()
                logger.info("user %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def list_user(request, opt=''):
        try :
            if opt == 'oname':
                users = [i.__str__() for i in ChatUser.objects.all()]
            else:
                users = [i.json() for i in ChatUser.objects.all()]
            return JsonResponse(status=200, data={'n': len(users), 'users': users}, safe=False)

        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

# logger.info(f'{"create" if new else "update"} user: id %s, name %s', user.id, user.name)


class ContactApiView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def m(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        try :
            data = json.loads(request.body)
            id = kwargs.get('id', data['id'])
            target = kwargs.get('target', data['target'])
            user = ChatUser.objects.get(uid=id)
            user.contact_list.add(ChatUser.objects.get(uid=target))
            user.save()
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass

@csrf_exempt
def contact_add(request, id, target):
    try :
        user = ChatUser.objects.get(uid=id)
        user2 = ChatUser.objects.get(uid=target)
        user.contact_list.add(user2)
        user.save()
        return HttpResponse(status=200)

    except (ValidationError, ObjectDoesNotExist):
        return HttpResponse(status=404)
    except BaseException as e:
        logger.error(f"Internal : {e.args[0]}")
        return HttpResponse(status=500)


@csrf_exempt
def contact_remove(request, id, target):
    try :
        user = ChatUser.objects.get(uid=id)
        user2 = ChatUser.objects.get(uid=target)
        user.contact_list.remove(user2)
        user.save()
        return HttpResponse(status=200)

    except (ValidationError, ObjectDoesNotExist):
        return HttpResponse(status=404)
    except BaseException as e:
        logger.error(f"Internal : {e.args[0]}")
        return HttpResponse(status=500)



