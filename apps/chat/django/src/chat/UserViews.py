# chat/views.py
from django.http import JsonResponse, HttpResponse
from chat.models import User

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError

from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from .validators import is_uuid

import chat.serializer as ser

from json import loads as jloads

from logging import getLogger
logger = getLogger('django')


from channels.db import database_sync_to_async



# handle IntegrityError
class UserApiView(View):

    @csrf_exempt
    @database_sync_to_async
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            data = ser.parse_json(data=request.body)
            s = ser.User(data=data)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            s.create(s.validated_data)
            return HttpResponse(status=201)

        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            fields = request.GET.get("fields")
            many = False
            safe = True
            name = kwargs.get('name')
            if name == None:
                qset = User.objects.all()
                many = True
                safe = False
            else:
                qset = User.objects.get(name=name)
            data = ser.User(qset, many=many, fields=fields).data
            data = ser.render_json(data)
            return HttpResponse(status=200, content=data)

        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def patch(self, request, *args, **kwargs):
        try :
            data = jloads(request.body)
            name = kwargs.get('name', data['name'])
            user = User.objects.get(name=name)
            s = ser.User(user, data=request.body, partial=True)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            logger.info(s.validated_data)
            s.update(s.instance, s.validated_data)
            return HttpResponse(status=200)

        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            opt = request.GET.get("opt")
            names = request.GET.get("name")
 
            if opt == 'all':
                User.objects.all().delete()
                return HttpResponse(status=200)
            elif names is None:
                return HttpResponse(status=400)

            if names is not None:
                names = names.split()
                for name in names:
                    User.objects.get(name=name).delete()	
                    logger.info("user %s, deleted", name)

            return HttpResponse(status=200)

        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)


class UserContactApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            user = User.objects.get(name=kwargs['id'])
            user.contacts.add(User.objects.get(name=kwargs['target']))
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
            return JsonResponse(status=200, data=User.objects.get(name=kwargs['id']).json_contact())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            user = User.objects.get(name=kwargs['id'])
            user.contacts.remove(User.objects.get(name=kwargs['target']))
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
            user = User.objects.get(name=kwargs['id'])
            user.blockeds.add(User.objects.get(name=kwargs['target']))
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
            return JsonResponse(status=200, data=User.objects.get(name=kwargs['id']).json_blocked())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            user = User.objects.get(name=kwargs['id'])
            user.blockeds.remove(User.objects.get(name=kwargs['target']))
            user.save()
            return HttpResponse(status=200)
        except KeyError:
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

