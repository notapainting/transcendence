# chat/views.py
from django.http import JsonResponse, HttpResponse
from models import ChatUser
from django.core.exceptions import ObjectDoesNotExist

#private API 
# create/update user
# delete user
# get user data

def create_user(request):
    try :
        buid = request.data['buid']
        username = request.data['username']
    except KeyError as e:
        return JsonResponse(status_code=400, data={'error': 'KeyNotfound', 'key': e.message})

    try :
        user, new = ChatUser.objects.get_or_create(buid=buid)
        user.name = username
        user.save()
    except BaseException as e:
        return JsonResponse(status_code=500, data={'error': 'Internal', 'context': e.message})

    if new == True:
        return HttpResponse(status_code=201)
    return HttpResponse(status_code=200)

# see if delete can throw
def delete_user(request):

    try :
        buid = request.data['buid']
    except KeyError as e:
        return JsonResponse(status_code=400, data={'error': 'KeyNotfound', 'key': e.message})

    try :
        user = ChatUser.objects.get(buid=buid)
        user.delete()
    except ObjectDoesNotExist as e:
        return JsonResponse(status_code=400, data={'error': 'UserDoesNotExist'})
    except BaseException as e:
        return JsonResponse(status_code=500, data={'error': 'Internal', 'context': e.message})

    return HttpResponse(status_code=200)

