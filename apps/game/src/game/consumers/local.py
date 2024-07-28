# game/consumers/local.py

import random, asyncio
import game.enums as enu

from game.consumers.base import BaseConsumer
from game.gamestate import GameState, local_loop, MAX_SCORE, DEFAULT_SCORE
from game.lobby import LOBBY_MAXIMUM_PLAYERS, LOBBY_MINIMUM_PLAYERS, LOBBY_DEFAULT_PLAYERS


class LocalConsumer(BaseConsumer):

    def __init__(self):
        super().__init__()
        self.local_players = []
        self.local_losers = []
        self.local_current = []
        self.local_matchIdx = -2
        self.local_task = None
        self.local_game_state = None
        self.nPlayers = LOBBY_DEFAULT_PLAYERS
        self.bonused = True
        self.scoreToWin = DEFAULT_SCORE

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        self.local_clear()

    async def receive_json(self, json_data):
        await self.local(json_data)

    async def local(self, data):
        match data['type']:
            case enu.Local.PLAYERS: 
                self.local_players = list(data['message'])
                if len(self.local_players) % 2 != 0 or len(self.local_players) == 0:
                    await self.send_json({'type':'error.players'})
                else:
                    await self.local_matchmake()
            case enu.Local.SETTINGS:
                self.changeSettings(data['message'])
            case enu.Local.UPDATE:
                await self.local_gaming(data)
            case enu.Local.READY:
                await self.local_gaming({"message":"startButton"})
            case enu.Local.PAUSE:
                if self.local_game_state.status['game_running'] == True:
                    await self.local_gaming({"message":"stopButton"})
                else:
                    await self.local_gaming({"message":"startButton"})
            case enu.Local.NEXT:
                await self.local_announce_next()
            case enu.Local.QUIT:
                self.local_clear()
            case _:
                print(f"error in local: bad type")

    def changeSettings(self, data):
        setattr(self, data['param'], data['value'])

    async def local_matchmake(self):
        random.shuffle(self.local_players)
        self.local_current = [(self.local_players[i],self.local_players[i + 1]) for i in range(0, len(self.local_players), 2)]
        self.local_matchIdx = -1
        await self.send_json({"type":enu.Local.PHASE, "message":self.local_current})

    async def local_announce_next(self):
        if self.local_matchIdx == -2:
            return
        if self.local_matchIdx == -3:
            return await self.send_json({'type':enu.Local.END_TRN})
        self.local_matchIdx += 1
        if self.local_matchIdx == len(self.local_current):
            if len(self.local_current) == 1:
                return
            await self.local_matchmake()
        else:
            match = self.local_current[self.local_matchIdx]
            self.local_game_state = GameState(self.bonused, self.scoreToWin)
            await self.send_json({"type":enu.Local.MATCH, "message":match, "state":self.local_game_state.to_dict('none')})

    async def local_game_end(self, data):
        winner = self.local_game_state.status['winner']
        if winner == 'leftWin':
            winner = self.local_current[self.local_matchIdx][0]
            loser = self.local_current[self.local_matchIdx][1]
        else:
            winner = self.local_current[self.local_matchIdx][1]
            loser = self.local_current[self.local_matchIdx][0]
        self.local_losers.append(loser)
        self.local_players.remove(loser)
        await self.send_json({'type':enu.Local.END_GAME, "message":winner})
        if len(self.local_current) == 1:
            self.local_clear()
            self.local_matchIdx = -3

    def local_clear(self):
        self.local_players = []
        self.local_losers = []
        self.local_current = []
        if self.local_task is not None:
            self.local_task.cancel()
        if hasattr(self, "local_game_state"):
            del self.local_game_state
        self.local_matchIdx = -2

    async def local_gaming(self, data):
        message = data["message"]
        if message == "startButton":
            self.local_game_state.status['game_running'] = True
            self.task = asyncio.create_task(local_loop(self))
        elif message == "stopButton":
            self.local_game_state.status['game_running'] = False
        elif message == "bonus":
            self.local_game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.local_game_state.update_player_position(message))


