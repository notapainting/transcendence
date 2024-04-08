# chat/views.py
from django.http import JsonResponse, HttpResponse
from chat.models import ChatUser

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError

from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .validators import is_uuid

from json import loads as jloads

from logging import getLogger
logger = getLogger('django')




# handle IntegrityError
class UserApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            data = jloads(request.body)
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
            id = kwargs.get('id')
            if id == None or id == 'oname':
                return self.list_user(id)
            if is_uuid(id):
                return JsonResponse(status=200, data=ChatUser.objects.get(uid=id).json())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=id).json())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def put(self, request, *args, **kwargs):
        try :
            data = jloads(request.body)
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


class UserContactApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(uid=kwargs['id'])
                user.contact_list.add(ChatUser.objects.get(uid=kwargs['target']))
            else:
                user = ChatUser.objects.get(name=kwargs['id'])
                user.contact_list.add(ChatUser.objects.get(name=kwargs['target']))
            user.save()
            return HttpResponse(status=200)
        except KeyError:
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                return JsonResponse(status=200, data=ChatUser.objects.get(uid=kwargs['id']).json_contact())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=kwargs['id']).json_contact())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(uid=kwargs['id'])
                user.contact_list.remove(ChatUser.objects.get(uid=kwargs['target']))
            else:
                user = ChatUser.objects.get(name=kwargs['id'])
                user.contact_list.remove(ChatUser.objects.get(name=kwargs['target']))
            user.save()
            return HttpResponse(status=200)
        except KeyError:
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)



class UserBlockedApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(uid=kwargs['id'])
                user.blocked_list.add(ChatUser.objects.get(uid=kwargs['target']))
            else:
                user = ChatUser.objects.get(name=kwargs['id'])
                user.blocked_list.add(ChatUser.objects.get(name=kwargs['target']))
            user.save()
            return HttpResponse(status=200)
        except KeyError:
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                return JsonResponse(status=200, data=ChatUser.objects.get(uid=kwargs['id']).json_blocked())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=kwargs['id']).json_blocked())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(uid=kwargs['id'])
                user.blocked_list.remove(ChatUser.objects.get(uid=kwargs['target']))
            else:
                user = ChatUser.objects.get(name=kwargs['id'])
                user.blocked_list.remove(ChatUser.objects.get(name=kwargs['target']))
            user.save()
            return HttpResponse(status=200)
        except KeyError:
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

