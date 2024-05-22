# game/tournament.py

from typing import Any
from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


from channels.exceptions import  InvalidChannelLayerError

DEFAULT_CHANNEL_LAYER ='default'

TOURNAMENT_MAX_PLAYER = 16

class Lobby:
    def __init__(self, host, name="Simple Match") -> None:
        self.host = host
        self.name = name
        self.invitation_list = set()
        self.challenger = None
        self.full = False
        self.n_ready = 0

    def invite(self, user):
        self.invitation_list.add(user)
    
    def uninvite(self, user):
        self.invitation_list.discard(user)
    
    def invited(self, user):
        return user in self.invitation_list

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




class ChannelLayerManager:
    """
    Takes a settings dictionary of backends and initialises them on request.
    """

    def __init__(self):
        self.backends = {}
        setting_changed.connect(self._reset_backends)

    def _reset_backends(self, setting, **kwargs):
        """
        Removes cached channel layers when the CHANNEL_LAYERS setting changes.
        """
        if setting == "CHANNEL_LAYERS":
            self.backends = {}

    @property
    def configs(self):
        # Lazy load settings so we can be imported
        return getattr(settings, "CHANNEL_LAYERS", {})

    def _make_backend(self, name, config):
        # Check for old format config
        if "ROUTING" in self.configs[name]:
            raise InvalidChannelLayerError(
                "ROUTING key found for %s - this is no longer needed in Channels 2."
                % name
            )
        # Load the backend class
        try:
            backend_class = import_string(self.configs[name]["BACKEND"])
        except KeyError:
            raise InvalidChannelLayerError("No BACKEND specified for %s" % name)
        except ImportError:
            raise InvalidChannelLayerError(
                "Cannot import BACKEND %r specified for %s"
                % (self.configs[name]["BACKEND"], name)
            )
        # Initialise and pass config
        return backend_class(**config)
    


channel_layers = ChannelLayerManager()

def get_channel_layer(alias=DEFAULT_CHANNEL_LAYER):
    """
    Returns a channel layer by alias, or None if it is not configured.
    """
    try:
        return channel_layers[alias]
    except KeyError:
        return None