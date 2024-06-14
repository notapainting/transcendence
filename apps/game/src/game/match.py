# game/match.py 

from game.lobby import Lobby
from game.consumers import GameState

from channels.layers import get_channel_layer


class Match:
    current_match = {}
    lost_guest = {}

    def __str__(self) -> str:
        return f"Match hosted by {self.lobby.host}"

    def __init__(self, host):
        self.lobby = Lobby(host=host)
        self.game_state = GameState()
        self.task = None
        self._store()

    def _store(self):
        Match.current_match[self.lobby.host] = self

    def _destroy(self):
        del Match.current_match[self.lobby.host]
        if self.lobby._challenger in Match.lost_guest is True:
            del Match.lost_guest[self.lobby._challenger]

    def end(self, host):
        self._destroy()
        print(f"send game data here and clean up action")
        pass

    def broke(host, guest):
        Match.lost_guest[guest] = host
        print(f"guest {guest} broke his match versus {host}")

    def is_lost(user):
        if user in Match.current_match:
            return True
        if user in Match.lost_guest:
            return Match.lost_guest[user]
        return False

    def recover(guest):
        host = Match.lost_guest[guest]
        print(f"guest {guest} recover his match versus {host}")
        return host

class Match2:
    current_match = {}
    lost_guest = {}

    def __init__(self, host, guest=None):
        self.host = host
        self.guest = guest
        self._invited = set()
        self._ready = set()
        self._chlayer = get_channel_layer()
        self.game_state = GameState()
        self.task = None
        Match.current_match[self.host] = self

    def __str__(self) -> str:
        return f"Match hosted by {self.host} vs {self.guest}"

    def destroy(self):
        del Match.current_match[self.host]
        if self.guest in Match.lost_guest is True:
            del Match.lost_guest[self.guest]
    
    def broke(self, host, guest):
        Match.lost_guest[guest] = host
        print(f"guest {guest} broke his match versus {host}")

    def recover(self, guest):
        host = Match.lost_guest[guest]
        del Match.lost_guest[guest]
        return host, Match.current_match[host]

    def is_lost(user):
        if user in Match.current_match:
            return True
        if user in Match.lost_guest:
            return Match.lost_guest[user]
        return False

    def recover(guest):
        host = Match.lost_guest[guest]
        print(f"guest {guest} recover his match versus {host}")
        return host
    
    
    async def clear(self):
        await self._chlayer.group_send(self._challenger, {"message":enu.Game.KICK, "author":self.host})
        for user in self._invited:
            await self._chlayer.group_send(user, {"message":enu.Game.KICK, "author":self.host})

    async def invite(self, user):
        self._invited.add(user)
        print(f"send invite to {user}")
        await self._chlayer.group_send(user, {"type":enu.Game.INVITE, "author":self.host})


    async def kick(self, user):
        if user == self._challenger:
            self._challenger = None
        else:
            self._invited.discard(user)
        await self._chlayer.group_send(user, {"type":enu.Game.KICK, "author":self.host})


    async def set_ready(self, user):
        self._ready.add(user)
        if len(self._ready) == 2:
            await self._chlayer.group_send(self.host, {"type":enu.Game.START, "author":self.host})
            await self._chlayer.group_send(self._challenger, {"type":enu.Game.START, "author":self.host})
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