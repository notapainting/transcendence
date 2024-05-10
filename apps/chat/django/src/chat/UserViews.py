# chat/views.py
from django.http import  HttpResponse

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError

from django.views import View
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

import chat.models as mod
import chat.serializers as ser



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
                qset = mod.User.objects.all()
                many = True
                safe = False
            else:
                qset = mod.User.objects.get(name=name)
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
            data = ser.parse_json(request.body)
            name = kwargs.get('name', data['name'])
            new_name = data.get('new_name', None)
            user = mod.User.objects.get(name=name)
            if new_name is not None:
                if mod.User.objects.all().filter(name=new_name).exists() is True:
                    return HttpResponse(status=403)
                user.name = new_name
                user.save()
                return HttpResponse(status=200)

            data_update = data.get('contact', None)
            if data_update is None:
                return HttpResponse(status=400)
            s = ser.EventContact(data=data_update)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            logger.info(s.validated_data)
            target = mod.User.objects.get(name=s.data['name'])
            if s.data['operation'] == 'a':
                user.update_relation(target, status=s.data['relation'])
            else:
                user.delete_relation(target)
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
                mod.User.objects.all().delete()
                return HttpResponse(status=200)
            elif names is None:
                return HttpResponse(status=400)
            if names is not None:
                names = names.split()
                for name in names:
                    mod.User.objects.get(name=name).delete()	
                    logger.info("user %s, deleted", name)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

