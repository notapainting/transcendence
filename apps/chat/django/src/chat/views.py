# chat/views.py
from django.http import JsonResponse, HttpResponse

def create_user(request):
    try :
        username = request.data['username']
        buid = request.data['buid']
    except KeyError as e:
        return JsonResponse(status_code=400, data={'error': 'KeyNotfound', 'key': e.message})
    try :
        new_user = ChatUser(buid=buid, name=username)
        new_user.save()
    except BaseException as e:
        return JsonResponse(status_code=500, data={'error': 'Internal', 'type': e.message})
    return HttpResponse(status_code=200)

def delete_user(request):
    try :
        buid = request.data['buid']
    except KeyError as e:
        return JsonResponse(status_code=400, data={'error': 'KeyNotfound', 'key': e.message})
    try :
        user = ChatUser.objects.get(buid=buid)
        user.delete()
    except BaseException as e:
        return JsonResponse(status_code=500, data={'error': 'Internal', 'type': e.message})
    return HttpResponse(status_code=200)

