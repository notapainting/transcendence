# projet/middleware.py

from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import async_only_middleware
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from channels.middleware import BaseMiddleware

from django.http import HttpResponseForbidden

import game.enums as enu

from logging import getLogger
logger = getLogger('django')

import httpx



class CustomAuthMiddleware(BaseMiddleware):
    async_capable = True
    sync_capable = False

    async def __call__(self, scope, receive, send):

        try :
            promise = await httpx.AsyncClient().post(url='http://auth-service:8000/auth/validate_token/', headers=dict(scope['headers']))
            promise.raise_for_status()
            scope['user'] = promise.json()['name']

        except httpx.HTTPStatusError as error:
            logger.warning(error)
            scope['user'] = None
        except (httpx.HTTPError) as error:
            logger.error(error)
            scope['user'] = None

        scope['user'] = scope['cookies']['user']

        return await self.inner(scope, receive, send)