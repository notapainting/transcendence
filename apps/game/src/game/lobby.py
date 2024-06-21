# game/lobby.py

from channels.layers import get_channel_layer
import game.enums as enu

class Lobby:
    def __init__(self, host, name="Simple Match") -> None:
        self.host = host
        self.name = name
        self._invited = set()
        self._ready = set()
        self._challenger = None
        self.guest = None
        self.n_ready = 0
        self._chlayer = get_channel_layer()

    def __str__(self) -> str:
        return self.name

    async def clear(self):
        await self._chlayer.group_send(self._challenger, {"type":enu.Game.KICK, "author":self.host})
        for user in self._invited:
            await self._chlayer.group_send(user, {"type":enu.Game.KICK, "author":self.host})

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


class Lobby2:
    def __init__(self, host, n_player=2, types=enu.Game) -> None:
        self.host = host
        self._invited = set()
        self._ready = set()
        self._players = set()
        self._players.add(host)
        self.n_player = n_player
        self._chlayer = get_channel_layer()

    async def clear(self):
        for user in self._invited:
            await self._chlayer.group_send(user, {"type":types.KICK, "author":self.host})
        self.broadcast({"type":types.KICK, "author":self.host})


    async def invite(self, user):
        self._invited.add(user)
        await self._chlayer.group_send(user, {"type":types.INVITE, "author":self.host})

    async def kick(self, user):
        self._players.discard(user)
        self._invited.discard(user)
        await self._chlayer.group_send(user, {"type":types.KICK, "author":self.host})

    async def add_ready(self, user):
        self._ready.add(user)
        self.broadcast({"type":types.READY, "author":user})


    def ready(self):
        if len(self._ready) == self.n_players:
            return True
        return False

    async def start(self):
        self.broadcast({"type":types.START, "author":self.host})

    def invited(self, user):
        return user in self._invited

    async def broadcast(self, message):
        for player in self._players:
            await self._chlayer.group_send(player, message)


