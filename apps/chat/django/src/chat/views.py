# chat/views.py
from django.http import JsonResponse, HttpResponse
from chat.models import ChatUser
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

import logging
logger = logging.getLogger('django')

# TODO: move log in models


import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except :
        raise ValueError



@csrf_exempt
@require_http_methods(["POST"])
def create_user(request, id=None):
    data = json.loads(request.body)

    try :
        if id == None:
            id = data['id']
        username = data['name']
    except KeyError as e:
        return JsonResponse(status=400, data={'error': 'KeyNotfound', 'key': e.args[0]})

    try :
        user, new = ChatUser.objects.get_or_create(buid=id)
        user.name = username
        user.save()
    except BaseException as e:
        return JsonResponse(status=500, data={'error': 'Internal', 'context': e.args[0]})

    if new == True:
        logger.info("create user: id %s, name %s", id, username)
        return HttpResponse(status=201)
    logger.info("update user id %s, name %s", id, username)
    return HttpResponse(status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, id):
    if id == 'all':
        ChatUser.objects.all().delete()
        return HttpResponse(status=200)
    try :
        is_valid_uuid(id)
        user = ChatUser.objects.get(buid=id)
    except ValueError:
        logger.warning("Not a valid uuid : %s", id)
        return HttpResponse(status=400)
    except ObjectDoesNotExist as e:
        logger.warning("user does not exist : %s", id)
        return HttpResponse(status=404)
    except BaseException as e:
        return JsonResponse(status=500, data={'error': 'Internal', 'context': e.args[0]})

    user.delete()
    logger.info("user %s, deleted", id)
    return HttpResponse(status=200)

# catch other except
@csrf_exempt
@require_http_methods(["GET"])
def get_user_by_name(request, name):
    try :
        user = ChatUser.objects.get(name=name)

    except ObjectDoesNotExist:
        return HttpResponse(status=404)

    return JsonResponse(status=200, data={'name': user.name})

@csrf_exempt
@require_http_methods(["GET"])
def get_user_by_id(request, id):
    try :
        is_valid_uuid(id)
        user = ChatUser.objects.get(buid=id)
    except ValueError:
        logger.warning("Not a valid uuid : %s", id)
        return HttpResponse(status=400)
    except ObjectDoesNotExist as e:
        logger.warning("user does not exist : %s", id)
        return HttpResponse(status=404)
    except BaseException as e:
        return JsonResponse(status=500, data={'error': 'Internal', 'context': e.args[0]})

    return JsonResponse(status=200, data=user.json())

@csrf_exempt
@require_http_methods(["GET"])
def list_user(request, opt=''):
    if opt == 'oname':
        users = [i.__str__() for i in ChatUser.objects.all()]
    else:
        users = [i.json() for i in ChatUser.objects.all()]
    return JsonResponse(status=200, data={'n': len(users), 'users': users}, safe=False)

@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def contact_add(request, id, target):
    try :
        is_valid_uuid(id)
        is_valid_uuid(target)
        user = ChatUser.objects.get(buid=id)
        user2 = ChatUser.objects.get(buid=target)
        print(user.json())
        user.contact_list.add(user2)
        print(user.json())
        user.save()
        print(user.json())
    except ValueError:
        logger.warning("Not a valid uuid : %s", id)
        return HttpResponse(status=400)
    except ObjectDoesNotExist as e:
        logger.warning("user does not exist : %s", id)
        return HttpResponse(status=404)
    except BaseException as e:
        return JsonResponse(status=500, data={'error': 'Internal', 'context': e.args[0]})

    return HttpResponse(status=200)


