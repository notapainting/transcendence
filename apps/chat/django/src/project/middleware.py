# projet/middleware.py

from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import sync_only_middleware
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from channels.middleware import BaseMiddleware

import requests

class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        """
        ASGI application; can insert things into the scope and run asynchronous
        code.
        """
        # ask auth to auth user
        print(scope['headers'])
        print(scope['cookies'])
        # ret = await async_to_sync(
        ret=    requests.post('http://auth-service:8000/auth/validate_token/')
        # )

        print(ret)
        # Copy scope to stop changes going upstream
        scope = dict(scope)
        # Run the inner application along with the scope
        return await self.inner(scope, receive, send)

