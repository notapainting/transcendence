# game/match.py 

from game.lobby import Lobby, Lobby2
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

class Match2(Lobby2):

    def __init__(self, host, tournament=None):
        super().__init__(host)
        self._players.add(host)
        self.game_state = GameState()
        self.task = None
        self.host = host
        self.tournament = tournament

    async def invite(self, user):
        if self.tournament is None:
            super().invite(user)

    async def kick(self, user):
        if self.tournament is None:
            super().kick(user)

    def compute(self):
        guest = [x for x in list(self._players) if x != self.host][0]
        scores = {self.host:self.game_state.status['leftPlayerScore'], guest:self.game_state.status['rightPlayerScore']}
        winner = self.game_state.status['winner']
        loser = [x for x in list(self._players) if x != winner][0]
        if winner == 'leftWin':
            winner = self.host
        else:
            winner = guest
        self.result = {"scores":scores,"winner":winner, "loser":loser}
        return self.result

    async def end(self, cancelled=False):
        if cancelled == False:
            if hasattr(self, "result") is False:
                self.result = self.compute()
            # send match history data to usermgt
            # import httpx
            # await httpx.AsyncClient().post(url='http://auth-service:8000/user/match/', data=self.result)
            if self.tournament is True:
                await self._chlayer.send_group(self.tournament, {"type":enu.Tournament.RESULT, "message":self.result})
        if self.task is not None:
            self.task.cancel()