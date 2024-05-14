# projet/middleware.py

from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import async_only_middleware
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from channels.middleware import BaseMiddleware
from channels.exceptions import DenyConnection
from django.core.exceptions import ObjectDoesNotExist
import chat.enums as enu
from channels.db import database_sync_to_async

from django.http import HttpResponseForbidden

import httpx
import chat.models as mod

@database_sync_to_async
def get_user(name):
    try:
        return mod.User.objects.exclude(name__in=enu.SpecialUser).get(name=name)
    except ObjectDoesNotExist:
        return None

class CustomAuthMiddleware(BaseMiddleware):
    async_capable = True
    sync_capable = False

    async def __call__(self, scope, receive, send):
        promise = await httpx.AsyncClient().post(url='http://auth-service:8000/auth/validate_token/', headers=dict(scope['headers']))

        print(promise.status_code)
        print(promise.json())
        if httpx.codes.is_error(promise.status_code) is True:
            scope['user'] = None
        else:
            scope['user'] = await get_user(name=promise.json()['name'])
        return await self.inner(scope, receive, send)

