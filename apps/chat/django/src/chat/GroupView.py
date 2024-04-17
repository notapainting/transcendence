from django.http import JsonResponse, HttpResponse
from chat.models import ChatGroup, ChatUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.views import View
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from json import loads as jloads
from logging import getLogger
from django.db.models import Count

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
            data = jloads(request.body)#can throw
            name = kwargs.get('name', data['name'])
            members = data['members']
            members_name = data['members_name']
            query_set = ChatUser.objects.filter(Q(uid__in=members) | Q(name__in=members_name))
            print(query_set)
            diff = len(members) + len(members_name) - len( query_set)
            if diff != 0:
                return JsonResponse(status=400, data={'error': 'MissingMembers'})

            # implementer verification doublon conv ? 
            # q2 = ChatGroup.objects.annotate(nb=Count("members"), distinct=True, filter=Q(members__uid__in=members))
            # print(f"q2: {q2}")
            # print(f"q2: {ChatGroup.objects.annotate(nb=Count("members")).values('nb').filter(nb=2)}")
            # if ChatGroup.objects.annotate(nb=Count("members")).values('nb').filter(nb=2).exists():
                # return HttpResponse(status=403)



            c = ChatGroup.objects.create(name=name)
            c.members.set(query_set)
            c.save()

            return HttpResponse(status=201)
        except KeyError as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def get(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            if id == None or id == 'short':
                return self.list(id)
            return JsonResponse(status=200, data=ChatGroup.objects.get(id=id).json())
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

# add/remove members
# chekc if user can manage group
    def put(self, request, *args, **kwargs):
        try :
            data = jloads(request.body)
            group = ChatGroup.objects.get(id=kwargs.get('id'))
            name = data.get('name')
            if name != None:
                group.name = name
            add = data.get('add')
            if add != None:
                add = ChatUser.objects.filter(uid__in=add)
                group.members.set(members__in=add)
            remove = data.get('remove')
            if remove != None:
                remove = ChatUser.objects.filter(uid__in=remove)
                group.members.remove(members__in=remove)
            group.save()
            return HttpResponse(status=200)
        except KeyError as e:
            return JsonResponse(status=400, data={'error': 'BadKey', 'key': e.args[0]})
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        try :
            id = kwargs.get('id')
            ChatGroup.objects.get(id=id).delete()
            logger.info("group %s, deleted", id)
            return HttpResponse(status=200)
        except (ValidationError, ObjectDoesNotExist):
            return HttpResponse(status=404)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)

    def list(request, opt=None):
        try :
            if opt == 'short':
                users = [i.json_short() for i in ChatGroup.objects.all()]
            else:
                users = [i.json() for i in ChatGroup.objects.all()]
            return JsonResponse(status=200, data={'n': len(users), 'groups': users}, safe=False)
        except BaseException as e:
            logger.error(f"Internal : {e.args[0]}")
            return HttpResponse(status=500)
