import json
from django.shortcuts import render
from django.http import JsonResponse
from apiauth.models import getFormInformation
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = getFormInformation.objects.create(name=data['name'], email=data['email'])
        return JsonResponse({"id": user.id, "name": user.name, "email": user.email})
# Create your views here.
