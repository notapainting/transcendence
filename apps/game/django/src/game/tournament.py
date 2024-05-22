# game/tournament.py

from typing import Any
from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


from channels.exceptions import  InvalidChannelLayerError
from channels.layers import get_channel_layer

import game.enums as enu
from game.consumers import GameState


def get_game_manager():
    pass

"""
match = lobby + gamestate 

matchManager -> look if lobby with host/guest already exist
            -> create new lobby
            
store match data 

"""

class Match:
    def __init__(self, host):
        self.lobby = Lobby(host=host)
        self.game_state = GameState()
        
    def __getitem__(self, key):
        pass
    
    def create(self):
        pass


class MatchManager:
    current_game = {}
    broken_guest= {}


TOURNAMENT_MAX_PLAYER = 16

class Lobby:
    def __init__(self, host, name="Simple Match") -> None:
        self.host = host
        self.name = name
        self._invited = set()
        self._ready = set()
        self._challenger = None
        self.n_ready = 0
        self._chlayer = get_channel_layer()

    async def clear(self):
        await self._chlayer.send(self._challenger, {"message":enu.Game.KICK})
        for user in self._invited:
            await self._chlayer.send(user, {"message":enu.Game.KICK})

    async def invite(self, user):
        if self.invited(user) is False:
            self._invited.add(user)
            await self._chlayer.send(user, {"type":enu.Game.INVITE, "author":self.host})
        else:
            raise RuntimeError("Player already invited")

    async def kick(self, user):
        if self.invited(user) is True:
            self._invited.discard(user)
            await self._chlayer.send(user, {"type":enu.Game.KICK, "author":self.host})
        elif user == self._challenger:
            self._challenger = None
            await self._chlayer.send(user, {"type":enu.Game.KICK, "author":self.host})
        else:
            raise RuntimeError("Player not found")

    async def set_ready(self, user):
        self._ready.add(user)
        if len(self._ready) == 2:
            await self._chlayer.send(self.host, {"type":enu.Game.START, "author":self.host})
            await self._chlayer.send(self._challenger, {"type":enu.Game.START, "author":self.host})
            return True
        else:
            return False

    def full(self):
        if self._challenger is not None:
            return True
        else:
            return False

    def ready(self, user):
        return user in self._ready

    def invited(self, user):
        return user in self._invited


class Tournament:
    
    def __str__(self) -> str:
        return self.name

    def __init__(self, creator, app=None, **kwargs) -> None:
        self.name = 'SuperDuper'
        self.max_player = TOURNAMENT_MAX_PLAYER
        self.creator = creator
        self.params = kwargs.get('params')
        self.app = app
        self.participants= set()

    async def __call__(self, *args, **kwds) -> Any:
        return await self.app(self.params)




# class ChannelLayerManager:
#     """
#     Takes a settings dictionary of backends and initialises them on request.
#     """

#     def __init__(self):
#         self.backends = {}
#         setting_changed.connect(self._reset_backends)

#     def _reset_backends(self, setting, **kwargs):
#         """
#         Removes cached channel layers when the CHANNEL_LAYERS setting changes.
#         """
#         if setting == "CHANNEL_LAYERS":
#             self.backends = {}

#     @property
#     def configs(self):
#         # Lazy load settings so we can be imported
#         return getattr(settings, "CHANNEL_LAYERS", {})

#     def _make_backend(self, name, config):
#         # Check for old format config
#         if "ROUTING" in self.configs[name]:
#             raise InvalidChannelLayerError(
#                 "ROUTING key found for %s - this is no longer needed in Channels 2."
#                 % name
#             )
#         # Load the backend class
#         try:
#             backend_class = import_string(self.configs[name]["BACKEND"])
#         except KeyError:
#             raise InvalidChannelLayerError("No BACKEND specified for %s" % name)
#         except ImportError:
#             raise InvalidChannelLayerError(
#                 "Cannot import BACKEND %r specified for %s"
#                 % (self.configs[name]["BACKEND"], name)
#             )
#         # Initialise and pass config
#         return backend_class(**config)
    

# DEFAULT_CHANNEL_LAYER2 ='default'
# channel_layers = ChannelLayerManager()

# def get_channel_layer2(alias=DEFAULT_CHANNEL_LAYER):
#     """
#     Returns a channel layer by alias, or None if it is not configured.
#     """
#     try:
#         return channel_layers[alias]
#     except KeyError:
#         return None