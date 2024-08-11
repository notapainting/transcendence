# game/consumers/local.py

import random, asyncio
import game.enums as enu

from game.consumers.base import BaseConsumer
from game.lobby import getDefault, LocalTournament, LobbyException



class LocalConsumer(BaseConsumer):

    async def connect(self):
        await self.accept()
        self.lobby = LocalTournament(host=self.channel_name)
        await self.lobby._init()
        await self.send_json({"type":enu.Game.SETTING, "message":getDefault()})
        print(f"Hey loyal !")

    async def disconnect(self, close_code):
        await self.lobby.end()
        print(f"bye loyal!")

    async def receive_json(self, json_data):
        try :
            await self.local(json_data)
        except LobbyException as lob:
            await self.send_json({"type":enu.Errors.LOBBY})
        except BaseException as e:
            print(f"error: {e}")


    async def local(self, data):
        match data['type']:
            case enu.Game.DEFAULT:
                await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault()})
            case enu.Game.SETTING:
                self.lobby.changeSettings(data['message'])
            case enu.Game.START:
                await self.lobby.start(data['players'])
            case enu.Game.READY :
                await self.lobby.match_start()
            case enu.Match.UPDATE :
                await self.lobby.match_feed(data)
            case enu.Match.PAUSE :
                await self.lobby.match_pause()
            case enu.Game.NEXT :
                await self.lobby.next()
            case enu.Game.QUIT :
                await self.lobby.end()
            case _:
                print(f"error: bad type")

    async def game_relay(self, data):
        await self.send_json(data["relay"])

    # async def game_start(self, data):
    #     await self.send_json(data)

    # async def tournament_phase(self, data):
    #     await self.send_json(data)

    # async def tournament_match(self, data):
    #     await self.send_json(data)

    # async def tournament_end(self, data):
    #     await self.send_json(data)

    # async def match_update(self, data):
    #     await self.send_json(data)

    async def match_score(self, data):
        print(f"score ")
        if self.lobby.matchCount > 0:
            data['score'] = {'players':self.lobby.current[self.lobby.matchCount]}
        await self.send_json(data)

    async def match_end(self, data):
        print(f"end...")
        data['message'] = self.lobby.match_result()
        await self.send_json(data)
        await self.lobby.tournament_result()


