from django.http import JsonResponse, HttpResponse
from chat.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from json import loads as jloads
from logging import getLogger
from django.db.models import Count

import chat.serializers as ser

logger = getLogger('django')



# check if user exist
# check if private groups exist
class GroupApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # check if user cant create conv (ie for private has un contact)
    def post(self, request, *args, **kwargs):
        try :
            data = ser.parse_json(request.body)
            s = ser.EventGroupCreate(data=data)
            if s.is_valid() is False:#trhow if user doesnt exit
                print(s.errors)
                return HttpResponse(status=400)
            print(s.validated_data)
            # implementer verification doublon conv ? 
            s.create(s.validated_data)
            return HttpResponse(status=201)

        except (ValidationError, ObjectDoesNotExist) as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            fields = request.GET.get("fields")
            many = False
            safe = True
            id = kwargs.get('id')
            if id == None:
                qset = Group.objects.all()
                many = True
                safe = False
            else:
                qset = Group.objects.get(id=id)
            data = ser.Group(qset, many=many, fields=fields).data
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
            s = ser.EventGroupUpdate(data=data)
            if s.is_valid() is False:
                print(s.errors)
                return HttpResponse(status=400)
            print(s.validated_data)
            s.update(s.validated_data)
            return HttpResponse(status=200)

        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            opt = request.GET.get("opt")
            ids = request.GET.get("id")
            if opt == 'all':
                Group.objects.all().delete()
                return HttpResponse(status=200)
            elif ids is None:
                return HttpResponse(status=400)
            if ids is not None:
                ids = ids.split()
                for id in ids:
                    Group.objects.get(id=id).delete()
                    logger.info("user %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)


