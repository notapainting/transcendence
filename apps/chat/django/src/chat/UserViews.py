# chat/views.py
from django.http import JsonResponse, HttpResponse
from chat.models import ChatUser

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError

from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from .validators import is_uuid
from .serializer import ChatUserSerializer

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
            if ChatUser.objects.filter(Q(name=data['name']) | Q(id=id)).exists():
                return HttpResponse(status=403)
            ChatUser.objects.create(id=id, name=data['name'])
            return HttpResponse(status=201)
        except (ValidationError, KeyError) as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            fields = request.GET.get("fields")

            print(fields)
            id = kwargs.get('id')
            if id == None:
                return JsonResponse(status=200, data=self.list_user(fields), safe=False)
            if is_uuid(id):
                qset = ChatUser.objects.get(id=id)
            else:
                qset = ChatUser.objects.get(name=id)
            data =ChatUserSerializer(qset, fields=fields).data
            print(data)
            return JsonResponse(status=200, data=data)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def put(self, request, *args, **kwargs):
        try :
            data = jloads(request.body)
            id = kwargs.get('id', data['id'])
            user = ChatUser.objects.get(id=id)
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
                ChatUser.objects.get(id=id).delete()
                logger.info("user %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def list_user(self, opt=''):
        qset = ChatUser.objects.all()
        if opt == 'oname':
            return ChatUserSerializer(qset, many=True, fields={'name', ''}).data
        else:
            return ChatUserSerializer(qset, many=True).data



class UserContactApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(id=kwargs['id'])
                user.contact_list.add(ChatUser.objects.get(id=kwargs['target']))
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
                return JsonResponse(status=200, data=ChatUser.objects.get(id=kwargs['id']).json_contact())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=kwargs['id']).json_contact())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(id=kwargs['id'])
                user.contact_list.remove(ChatUser.objects.get(id=kwargs['target']))
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
                user = ChatUser.objects.get(id=kwargs['id'])
                user.blocked_list.add(ChatUser.objects.get(id=kwargs['target']))
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
                return JsonResponse(status=200, data=ChatUser.objects.get(id=kwargs['id']).json_blocked())
            return JsonResponse(status=200, data=ChatUser.objects.get(name=kwargs['id']).json_blocked())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            if is_uuid(kwargs['id']):
                user = ChatUser.objects.get(id=kwargs['id'])
                user.blocked_list.remove(ChatUser.objects.get(id=kwargs['target']))
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

