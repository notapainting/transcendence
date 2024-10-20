# projet/middleware.py

from channels.middleware import BaseMiddleware
from django.core.exceptions import ObjectDoesNotExist
import chat.enums as enu
from channels.db import database_sync_to_async


from logging import getLogger
logger = getLogger('base')

import httpx
import chat.models as mod

@database_sync_to_async
def get_user(name):
        return mod.User.objects.exclude(name__in=enu.SpecialUser).get(name=name)

class CustomAuthMiddleware(BaseMiddleware):
    async_capable = True
    sync_capable = False
    async def __call__(self, scope, receive, send):
        try :
            promise = await httpx.AsyncClient().post(url='http://auth:8000/auth/validate_token/', headers=dict(scope['headers']))
            promise.raise_for_status()
            scope['user'] = await get_user(name=promise.json()['username'])

        except httpx.HTTPStatusError as error:
            logger.warning(error)
            scope['user'] = None
        except (httpx.HTTPError, ObjectDoesNotExist) as error:
            logger.error(error)
            scope['user'] = None
        return await self.inner(scope, receive, send)
