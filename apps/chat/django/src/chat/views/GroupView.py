from django.http import HttpResponse
from chat.models import Group
from django.views import View


from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError

from django.views.decorators.csrf import csrf_exempt

import chat.serializers.db as ser
import chat.serializers.events as event
import chat.utils as uti

from logging import getLogger
logger = getLogger('django')


class GroupApiView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            s = event.GroupCreate(data=data)
            s.is_valid(raise_exception=True)
            s.create(s.validated_data)
            return HttpResponse(status=201)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
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
            data = uti.render_json(data)
            return HttpResponse(status=200, content=data)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def patch(self, request, *args, **kwargs):
        try :
            data = uti.parse_json(request.body)
            s = event.GroupUpdate(data=data)
            s.is_valid(raise_exception=True)
            s.update(s.validated_data)
            return HttpResponse(status=200)
        except (DrfValidationError, ParseError) as error:
            logger.error(error)
            return HttpResponse(status=400)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            Group.objects.get(id=id).delete()
            logger.info("group %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as error:
            logger.critical(f"{type(error).__name__} : {error})")
            return HttpResponse(status=500)


