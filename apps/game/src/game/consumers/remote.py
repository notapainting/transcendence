import asyncio, random, httpx

import game.enums as enu
import channels.exceptions as exchan

from game.consumers.base import BaseConsumer
from game.gamestate import GameState, remote_loop, local_loop
from game.lobby import Match, Tournament

from logging import getLogger
logger = getLogger(__name__)


async def authenticate(headers):
    try :
        promise = await httpx.AsyncClient().post(url='http://auth:8000/auth/validate_token/', headers=headers)
        promise.raise_for_status()
        user = str(promise.json()['username'])
    except httpx.HTTPStatusError as error:
        logger.warning(error)
        user = None
    except (httpx.HTTPError) as error:
        logger.error(error)
        user = None
    except BaseException as error:
        logger.error(error)
    return user

class RemoteGamer(BaseConsumer):
    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invitations = set()
        self.status = enu.CStatus.IDLE
        self.mode = self.idle
        self.loopback = self.status

        self.local_players = []
        self.local_losers = []
        self.local_current = []
        self.local_matchIdx = -2
        self.local_task = None
        self.local_game_state = None

    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers'])) #str(self.scope.get('user', 'Anon'))
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        await self.channel_layer.group_add(self.username, self.channel_name)
        print(f"hello {self.username} ({self.status})!")

    async def disconnect(self, close_code):
        if self.username is not None:
            await self.channel_layer.group_discard(self.username, self.channel_name)
        print(f"bye {self.username} ({self.status})...")

        if self.status == enu.Local.MODE:
            self.local_clear()
        elif self.status == enu.Game.HOST:
            await self.match.end(True)
            await self.match.broadcast({"type":enu.Game.BROKE, "author":self.username})
            self.set_mode()
        elif self.status == enu.Game.GUEST:
            await self.send_cs(self.host, {"type":enu.Game.BROKE, "author":self.username})
            self.set_mode()

        elif self.status == enu.Tournament.HOST:
            self.tournament.end(True)
            await self.tournament.broadcast({"type":enu.Tournament.BROKE, "author":self.username})
        elif self.status == enu.Tournament.GUEST:
            await self.send_cs(self.thost, {"type":enu.Tournament.BROKE, "author":self.username})

    async def send_cs(self, target, data):
        data['author'] = self.username
        await self.channel_layer.group_send(target, data)

    def set_mode(self, status=None):
        if status == None:
            self.status = self.loopback
        else:
            self.loopback = self.status
            self.status = status
        match self.status:
            case enu.CStatus.IDLE : self.mode = self.idle
            case enu.Local.MODE : self.mode = self.local
            case enu.Game.HOST : self.mode = self.game_host
            case enu.Game.GUEST : self.mode = self.game_guest
            case enu.Tournament.HOST : self.mode = self.tournament_host
            case enu.Tournament.GUEST : self.mode = self.tournament_guest

    async def receive_json(self, json_data):
        if json_data.get('type') == None: # enu.Errors.DECODE
            return await self.send_json({'type':enu.Errors.TYPE})
        if json_data['type'] == enu.Errors.DECODE:
            return await self.send_json({'type':enu.Errors.DECODE})
        json_data['author'] = self.username
        print(f"{self.username} ({self.status}): type is {json_data['type']} ")
        await self.mode(json_data)


    async def idle(self, data):
        match data['type']:
            case enu.Game.CREATE:
                self.set_mode(enu.Game.HOST)
                self.match = Match(self.username)
            case enu.Game.JOIN:
                if data['message'] in self.invitations:
                    self.invitations.discard(data['message'])
                    await self.send_cs(data['message'], data)
            case enu.Tournament.CREATE:
                self.set_mode(enu.Tournament.HOST)
                self.tournament = Tournament(self.username)
            case enu.Tournament.JOIN:
                if data['message'] in self.invitations:
                    self.invitations.discard(data['message'])
                    await self.send_cs(data['message'], data)
            case enu.Local.MODE:
                self.set_mode(enu.Local.MODE)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})

# LOCAL
    async def local(self, data):
        match data['type']:
            case enu.Local.PLAYERS: 
                self.local_players = list(data['message'])
                if len(self.local_players) % 2 != 0 or len(self.local_players) == 0:
                    await self.send_json({'type':'error.players'})
                else:
                    await self.local_matchmake()
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
            self.local_game_state = GameState()
            await self.send_json({"type":enu.Local.MATCH, "message":match, "state":self.local_game_state.to_dict('none')})

    async def local_game_end(self, data):
        print("local game end here")
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
            self.local_matchIdx =-3

    async def local_gaming(self, data):
        print(f"here")
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

    def local_clear(self):
        self.local_players = []
        self.local_losers = []
        self.local_current = []
        if self.local_task is not None:
            self.local_task.cancel()
        self.local_task = None
        del self.local_game_state
        self.local_matchIdx = -2


# MATCH
    async def game_host(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.match.end(True)
                self.set_mode(enu.CStatus.IDLE)
                await self.match.broadcast(data)
            case enu.Game.INVITE:
                await self.match.invite(data['message'])
            case enu.Game.KICK:
                await self.match.kick(data['message'])
            case enu.Game.READY:
                await self.match.add_ready(self.username)
                if self.match.ready() is True:
                    await self.match.start()
                    await self.gaming({"message":"startButton"})
            case enu.Game.UPDATE: 
                data['message'] = format_paddle_key(self.status, data['message'])
                await self.gaming(data)
            case enu.Game.PAUSE: 
                data['author'] = self.username
                if self.match.game_state.status['game_running'] == True:
                    await self.gaming({"message":"stopButton"})
                    self.match.game_state.status['game_running'] = False
                    await self.match.broadcast(data)
                else:
                    data['type'] = enu.Game.RESUME
                    await self.match.broadcast(data)
                    await self.gaming({"message":"startButton"})
            case _: 
                print(f"unknow : {data['type']}")
                await self.send_json({'type':enu.Errors.TYPE})

    async def game_guest(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.send_cs(self.host, data)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Game.READY:
                await self.send_cs(self.host, data)
            case enu.Game.UPDATE: 
                data['message'] = format_paddle_key(self.status, data['message'])
                await self.send_cs(self.host, data)
            case enu.Game.PAUSE: 
                await self.send_cs(self.host, data)
            case _:
                print(f"unknow : {data['type']}")
                await self.send_json({'type':enu.Errors.TYPE})

    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.match.game_state.status['game_running'] == False :
                self.match.game_state.status['game_running'] = True
                self.match.task = asyncio.create_task(remote_loop(self))
        elif message == "bonus":
            self.match.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.match.game_state.update_player_position(message))

    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if data['author'] == self.username:
            return 
        if self.status == enu.Game.HOST and 'r' not in data:
            await self.match.add_ready(data['author'])
            if self.match.ready() is True:
                await self.match.start()
                await self.gaming({"message":"startButton"})
        await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    async def game_score(self, data):
        await self.send_json(data)

    async def game_broke(self, data):
        if self.status == enu.Game.HOST:
            await self.match.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

    async def game_end(self, data):
        if self.status == enu.Local.MODE:
            return await self.local_game_end(data)
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.match.end()
        self.set_mode()
        await self.send_json(data)

    async def game_pause(self, data):
        if self.status == enu.Game.HOST:
            if data['author'] == self.username:
                return
            if self.match.game_state.status['game_running'] == True:
                await self.gaming({"message":"stopButton"})
                self.match.game_state.status['game_running'] = False
            else:
                await self.gaming({"message":"startButton"})
                self.match.game_state.status['game_running'] = True
                data['type'] = enu.Game.RESUME
        await self.send_json(data)

    async def game_resume(self, data):
        if data['author'] == self.username:
            return ;
        await self.send_json(data)

    async def game_update(self, data):
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.gaming(data)
        else:
            await self.send_json(data)

    async def game_quit(self, data):
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.match.end(True)
        if data['author'] != self.username:
            await self.send_json(data)
            self.set_mode()

    async def game_join(self, data):
        if self.match.invited(data['author']) and self.match.full() is False and self.status == enu.Game.HOST:
            self.match.add(data['author'])
            data['message'] = self.match.game_state.to_dict('none')
            await self.send_json(data)
            plist = list(self.match._players)
            await self.match.broadcast({"type":enu.Game.ACCEPTED, "author":self.username, "message":self.match.game_state.to_dict('none'), "players":plist})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

    async def game_deny(self, data):
        await self.send_json(data)

    async def game_accepted(self, data):
        if self.status != enu.Game.HOST:
            self.host = data['author']
            self.set_mode(enu.Game.GUEST)
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] == self.host:
            self.host = None
            self.set_mode(enu.CStatus.IDLE)
        else:
            self.invitations.discard(data['author'])
        await self.send_json(data)

# TOURNAMENT
    async def tournament_host(self, data):
        match data['type']:
            case enu.Tournament.QUIT:
                self.tournament.end(True)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Tournament.INVITE:
                await self.tournament.invite(data['message'])
            case enu.Tournament.KICK:
                await self.tournament.kick(data['message'])
            case enu.Tournament.READY:
                await self.tournament.add_ready(self.username)
                if self.tournament.ready() is True:
                    self.tournament.start()
                    self.tournament.make_phase()
                    self.tournament.order_match()

    async def tournament_guest(self, data):
        match data['type']:
            case enu.Tournament.QUIT:
                await self.send_cs(self.thost, data)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Tournament.READY:
                await self.send_cs(self.thost, data)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})

    async def tournament_result(self, data):
        if hasattr(self, "tournament") is False:
            return
        await self.tournament.update_result(data)

    async def tournament_match(self, data):
        await self.send_json(data)
        if self.username == data['message']['host']:
            self.set_mode(enu.Game.HOST)
            self.match = Match(self.username, data['author'])
        else:
            self.set_mode(enu.Game.GUEST)

    async def tournament_broke(self, data):
        if self.status == enu.Tournament.HOST:
            await self.tournament.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

    async def tournament_quit(self, data):
        await self.tournament.kick(data['message'])

    async def tournament_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def tournament_join(self, data):
        if self.status != enu.Tournament.HOST or data['author'] == self.username:
            return await self.send_json(data)
        if self.tournament.invited(data['author']) and self.tournament.full() is False:
            self.tournament.add(data['author'])
            await self.send_cs(data['author'], {"type":enu.Tournament.ACCEPTED, "author":self.username, "message":self.tournament.players_state()})
            data['message'] = data['author']
            data['author'] = self.username
            await self.tournament.broadcast(data)
        else:
            await self.send_cs(data['author'], {"type":enu.Tournament.DENY})

    async def tournament_accepted(self, data):
        self.thost = data['author']
        self.set_mode(enu.Tournament.GUEST)
        await self.send_json(data)

    async def tournament_kick(self, data):
        await self.send_json(data)
        self.set_mode()

    async def tournament_start(self, data):
        await self.send_json(data)

    async def tournament_ready(self, data):
        if self.status == enu.Tournament.HOST and data['author'] != self.username:
            await self.tournament.add_ready(self.username)
            if self.tournament.ready() is True:
                await self.tournament.start()
                await self.tournament.make_phase()
                await self.tournament.order_match()
        if data['author'] != self.username:
            await self.send_json(data)


def format_paddle_key(status, key):
    if status == enu.Game.HOST:
        match key:
            case 'downPressed' | 'sPressed':
                return 'sPressed'
            case 'downRelease' | 'sRelease':
                return 'sRelease'
            case 'upPressed' | 'wPressed':
                return 'wPressed'
            case 'upRelease' | 'wRelease':
                return 'wRelease'
            case '_':
                return key
    else:
        match key:
            case 'downPressed' | 'sPressed':
                return 'downPressed'
            case 'downRelease' | 'sRelease':
                return 'downRelease'
            case 'upPressed' | 'wPressed':
                return 'upPressed'
            case 'upRelease' | 'wRelease':
                return 'upRelease'
            case '_':
                return key
