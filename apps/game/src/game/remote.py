import json, asyncio, time



import game.enums as enu

from game.consumers import GameState, loop_remote_ultime
from game.lobby import Lobby
from game.match import Match, Match2
from game.tournament import Tournament

import channels.exceptions as exchan

from logging import getLogger
logger = getLogger(__name__)

import httpx

from game.base import BaseConsumer

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
        self.match_status = enu.CStatus.IDLE
        self.match = None
        self.host = None
        self.tournament_status = enu.CStatus.IDLE


    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers']))
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        await self.channel_layer.group_add(self.username, self.channel_name)
        lost = Match.is_lost(self.username)
        if lost is False:
            pass
        elif lost is True:
            self.match_status = enu.CStatus.HOST
            self.match = Match.current_match[self.username]
            # implemente reste
        else:
            self.match_status = enu.CStatus.GUEST
            self.host = Match.recover(self.username)
            await self.send_cs(self.host, {"type":enu.Game.RECOVER})
        print(f"hello {self.username} ({self.match_status})!")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.username, self.channel_name)
        print(f"bye {self.username} ({self.match_status})...")
        if self.match_status == enu.CStatus.HOST:
            self.match.end
            if self.match.task is not None:
                self.match.task.cancel()
            del self.match
        elif self.match_status == enu.CStatus.GUEST:
            Match.broke(host=self.host, guest=self.username)
            await self.send_cs(self.host, {"type":enu.Game.LOST})

    async def send_cs(self, target, data):
        data['author'] = self.username
        await self.channel_layer.group_send(target, data)

    async def receive_json(self, json_data):
        
        if json_data.get('type') == None: # enu.Errors.DECODE
            return await self.send_json({'type':enu.Errors.TYPE})
        print(f"{self.username} ({self.match_status}): type is {json_data['type']} ")
        
        if json_data['type'] == enu.Errors.DECODE:
            return await self.send_json({'type':enu.Errors.DECODE})
        
        if self.match_status == enu.CStatus.HOST:
            match json_data['type']:
                case enu.Game.QUIT:
                    self.match.end
                    del self.match
                case enu.Game.INVITE:
                    await self.match.lobby.invite(json_data['message'])
                case enu.Game.KICK:
                    await self.match.lobby.kick(json_data['message'])
                case enu.Game.READY:
                    if await self.match.lobby.set_ready(self.username) is True:
                        await self.gaming({"message":"startButton"})
                    else:
                        await self.send_cs(self.match.lobby._challenger, json_data)
                case enu.Game.UPDATE: 
                    await self.gaming(json_data)

        elif self.match_status == enu.CStatus.GUEST:
            match json_data['type']:
                case enu.Game.QUIT:
                    self.match_status = enu.CStatus.IDLE
                    await self.send_cs(self.host, json_data)
                    self.host = None
                case enu.Game.READY:
                    await self.send_cs(self.host, json_data)
                case enu.Game.UPDATE: 
                    await self.send_cs(self.host, json_data)

        else:
            match json_data['type']:
                case enu.Game.CREATE:
                    self.match_status = enu.CStatus.HOST
                    self.match = Match(self.username)
                case enu.Game.JOIN:
                    if json_data['message'] in self.invitations:
                        self.invitations.discard(json_data['message'])
                        await self.send_cs(json_data['message'], json_data)

    # BOTH
    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if self.match_status == enu.CStatus.HOST:
            if self.match.lobby.set_ready(data['message']) is True:
                await self.gaming({"message":"startButton"})
            else:
                await self.send_json(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    # async def game_unready(self, data):
    #     if self.match_status == enu.CStatus.HOST:
    #         if self.match.lobby.unready(data['message']):
    #             await self.send_json(data)
    #     elif self.match_status == enu.CStatus.GUEST:
    #         await self.send_json(data)

    async def game_update(self, data):
        if self.match_status == enu.CStatus.HOST:
            await self.gaming(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_lost(self, data):
        pass

    async def game_recover(self, data):
        pass

    async def game_quit(self, data):
        self.match.lobby.set_ready.discard(self.match.lobby._challenger)
        self.match.lobby._challenger = None
        await self.send_json(data)

    async def game_join(self, data):
        if self.match.lobby.invited(data['author']) and self.match.lobby.full() is False:
            self.match.lobby._challenger = data['author']
            data['message'] = self.match.game_state.to_dict('none')
            await self.send_json(data)
            await self.send_cs(self.match.lobby._challenger, {"type":enu.Game.ACCEPTED, "message":self.match.game_state.to_dict('none')})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

    # GUEST ONLY
    async def game_deny(self, data):
        await self.send_json(data)

    async def game_accepted(self, data):
        self.host = data['author']
        self.match_status = enu.CStatus.GUEST
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] == self.host:
            self.host = None
            self.match_status = enu.CStatus.IDLE
        else:
            self.invitations.discard(data['author'])
        await self.send_json(data)

    async def game_settings(self, data):
        await self.send_json(data)


    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.match.game_state.status['game_running'] == False :
                self.match.game_state.status['game_running'] = True
                self.match.task = asyncio.create_task(loop_remote_ultime(self))
        elif message == "bonus":
            self.match.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.match.game_state.update_player_position(message))


class RemoteGamer2(BaseConsumer):
    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invitations = set()
        self.status = enu.CStatus.IDLE
        self.mode = self.idle

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

        if self.status == enu.CStatus.GHOST:
            await self.match.end(True)
            await self.match.broadcast({"type":enu.Game.BROKE, "author":self.username})
            self.set_mode()
        if self.status == enu.CStatus.GGUEST:
            await self.send_cs(self.host, {"type":enu.Game.BROKE, "author":self.username})
            self.set_mode()

        if self.status == enu.CStatus.THOST:
            self.tounament.end(True)
            await self.match.broadcast({"type":enu.Tournament.BROKE, "author":self.username})
        if self.status == enu.CStatus.TGUEST:
            await self.send_cs(self.thost, {"type":enu.Tournament.BROKE, "author":self.username})


    async def send_cs(self, target, data):
        data['author'] = self.username
        await self.channel_layer.group_send(target, data)

    def set_mode(self, status=None):
        print(f"ouin")
        if status == None:
            self.status = self.loopback
        else:
            self.loopback = self.status
            self.status = status
        match self.status:
            case enu.CStatus.IDLE : self.mode = self.idle
            case enu.CStatus.GHOST : self.mode = self.game_host
            case enu.CStatus.GGUEST : self.mode = self.game_guest
            case enu.CStatus.THOST : self.mode = self.tournament_guest
            case enu.CStatus.TGUEST : self.mode = self.tournament_host

    async def receive_json(self, json_data):
        if json_data.get('type') == None: # enu.Errors.DECODE
            return await self.send_json({'type':enu.Errors.TYPE})
        if json_data['type'] == enu.Errors.DECODE:
            return await self.send_json({'type':enu.Errors.DECODE})

        print(f"{self.username} ({self.status}): type is {json_data['type']} ")
        await self.mode(json_data)


    async def idle(self, data):
        match data['type']:
            case enu.Game.CREATE:
                self.set_mode(enu.CStatus.GHOST)
                self.match = Match2(self.username)
            case enu.Game.JOIN:
                if data['message'] in self.invitations:
                    self.invitations.discard(data['message'])
                    await self.send_cs(data['message'], data)
            case enu.Tournament.CREATE:
                self.tournament = Tournament(self.username)
                self.set_mode(enu.CStatus.THOST)
            case enu.Tournament.JOIN:
                self.thost = data['message']
                self.set_mode(enu.CStatus.TGUEST)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})


    async def game_host(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.match.end(True)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Game.INVITE:
                await self.match.invite(data['message'])
            case enu.Game.KICK:
                await self.match.kick(data['message'])
            case enu.Game.READY:
                await self.match.set_ready(self.username)
                if self.match.ready() is True:
                    self.match.start()
                    await self.gaming({"message":"startButton"})
            case enu.Game.UPDATE: 
                await self.gaming(data)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})

    async def game_guest(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.send_cs(self.host, data)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Game.READY:
                await self.send_cs(self.host, data)
            case enu.Game.UPDATE: 
                await self.send_cs(self.host, data)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})

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
                await self.tournament.set_ready(self.username)
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

    # BOTH
    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if self.match_status == enu.CStatus.HOST:
            if self.match.set_ready(data['message']) is True:
                await self.gaming({"message":"startButton"})
            else:
                await self.send_json(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    async def game_broke(self, data):
        if self.status == enu.CStatus.GHOST:
            await self.match.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

    async def game_end(self, data):
        if self.status == enu.CStatus.GHOST:
            await self.match.end()
        self.set_mode()
        await self.send_json(data)


    async def game_update(self, data):
        if self.status == enu.CStatus.GHOST:
            await self.gaming(data)
        elif self.status == enu.CStatus.GGUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_quit(self, data):
        self.match.set_ready.discard(self.match._challenger)
        self.match._challenger = None
        await self.send_json(data)

    async def game_join(self, data):
        if self.match.invited(data['author']) and self.match.full() is False:
            self.match._players.add(data['author'])
            data['message'] = self.match.game_state.to_dict('none')
            # await self.send_json(data)
            await self.match.broadcast({"type":enu.Game.ACCEPTED, "author":self.username, "message":self.match.game_state.to_dict('none')})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

    # GUEST ONLY
    async def game_deny(self, data):
        await self.send_json(data)

    async def game_accepted(self, data):
        if self.status != enu.CStatus.GHOST:
            self.host = data['author']
            self.set_mode(enu.CStatus.GGUEST)
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] == self.host:
            self.host = None
            self.set_mode(enu.CStatus.IDLE)
        else:
            self.invitations.discard(data['author'])
        await self.send_json(data)

    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.match.game_state.status['game_running'] == False :
                self.match.game_state.status['game_running'] = True
                self.match.task = asyncio.create_task(loop_remote_ultime(self))
        elif message == "bonus":
            self.match.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.match.game_state.update_player_position(message))


    async def tournament_result(self, data):
        if hasattr(self, "tournament") is False:
            return
        await self.tournament.update_result(data)


    async def tournament_match(self, data):
        await self.send_json(data)
        if self.username == data['message']['host']:
            self.set_mode(enu.CStatus.GHOST)
            self.match = Match2(self.username, data['author'])
        else:
            self.set_mode(enu.CStatus.GGUEST)
        

    async def tournament_broke(self, data):
        if self.status == enu.CStatus.THOST:
            await self.tournament.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

    async def tournament_quit(self, data):
        await self.tournament.kick(data['message'])

    async def tournament_kick(self, data):
        await self.send_json(data)

    async def tournament_start(self, data):
        await self.send_json(data)
