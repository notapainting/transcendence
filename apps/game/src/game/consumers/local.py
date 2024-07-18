# game/consumers/local.py

import random, asyncio
import game.enums as enu

from game.consumers.base import BaseConsumer
from game.gamestate import GameState, local_loop


class LocalConsumer(BaseConsumer):
    async def connect(self):
        await self.accept()
        self.local_players = []
        self.local_losers = []
        self.local_current = []
        self.local_matchIdx = -2
        self.local_task = None
        self.local_game_state = None

    async def disconnect(self, close_code):
        if self.local_task is not None:
            self.local_task.cancel()

    async def receive_json(self, json_data):
        match json_data['type']:
            case enu.Local.PLAYERS: 
                self.local_players = list(json_data['message'])
                if len(self.local_players) % 2 != 0 or len(self.local_players) == 0:
                    await self.send_json({'type':'error.players'})
                else:
                    await self.matchmake()
            case enu.Local.UPDATE:
                await self.gaming(json_data)
            case enu.Local.READY:
                await self.gaming({"message":"startButton"})
            case enu.Local.PAUSE:
                if self.local_game_state.status['game_running'] == True:
                    await self.gaming({"message":"stopButton"})
                else:
                    await self.gaming({"message":"startButton"})
            case enu.Local.NEXT:
                await self.announce_next()
            case enu.Local.QUIT:
                self.clear()
            case _:
                print(f"error in local: bad type")

    async def matchmake(self):
        random.shuffle(self.local_players)
        self.local_current = [(self.local_players[i],self.local_players[i + 1]) for i in range(0, len(self.local_players), 2)]
        self.local_matchIdx = -1
        await self.send_json({"type":enu.Local.PHASE, "message":self.local_current})

    async def announce_next(self):
        if self.local_matchIdx == -2:
            return
        if self.local_matchIdx == -3:
            return await self.send_json({'type':enu.Local.END_TRN})
        self.local_matchIdx += 1
        if self.local_matchIdx == len(self.local_current):
            if len(self.local_current) == 1:
                return
            await self.matchmake()
        else:
            match = self.local_current[self.local_matchIdx]
            self.local_game_state = GameState()
            await self.send_json({"type":enu.Local.MATCH, "message":match, "state":self.local_game_state.to_dict('none')})

    async def game_end(self, data):
        print("gameend here")
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
            self.clear()
            self.local_matchIdx =-3

    def clear(self):
        self.local_players = []
        self.local_losers = []
        self.local_current = []
        self.local_task = None
        del self.local_game_state
        self.local_matchIdx = -2

    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            self.local_game_state.status['game_running'] = True
            self.local_task = asyncio.create_task(local_loop(self))
        elif message == "stopButton":
            self.local_game_state.status['game_running'] = False
        elif message == "bonus":
            self.local_game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.local_game_state.update_player_position(message))


