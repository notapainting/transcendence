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

    def __init__(self, host, guest):
        self.host = host
        self.guest = guest
        self._ready = set()
        self._chlayer = get_channel_layer()
        self.game_state = GameState()
        self._store()

    def __str__(self) -> str:
        return f"Match hosted by {self.lobby.host}"

    def __del__(self):
        del Match.current_match[self.lobby.host]
        if self.lobby._challenger in Match.lost_guest is True:
            del Match.lost_guest[self.lobby._challenger]

    def _store(self):
        Match.current_match[self.lobby.host] = self
        return Match.current_match[self.lobby.host]

    def end(self, host):
        print(f"send game data here and clean up action")
        pass


    def broke(self, host, guest):
        Match.lost_guest[guest] = host

    def recover(self, guest):
        host = Match.lost_guest[guest]
        del Match.lost_guest[guest]
        return host, Match.current_match[host]
