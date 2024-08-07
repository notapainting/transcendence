import asyncio, random, httpx

import game.enums as enu
import channels.exceptions as exchan

from game.consumers.base import BaseConsumer
from game.consumers.local import LocalConsumer
from game.gamestate import GameState, remote_loop, local_loop
from game.lobby import Match, Tournament, getDefault
from rest_framework.renderers import JSONRenderer

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

class RemoteGamer(LocalConsumer):
    connected = set()

    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invitations = set()
        self.status = enu.CStatus.IDLE
        self.mode = self.idle
        self.loopback = self.status

    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers'])) 
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        RemoteGamer.connected.add(self.username)
        await self.channel_layer.group_add(self.username, self.channel_name)
        await self.send_json({"type":enu.Game.SETTINGS_DEF, "message":getDefault()})
        print(f"hello {self.username} ({self.status})!")

    async def disconnect(self, close_code):
        if self.username is not None:
            await self.channel_layer.group_discard(self.username, self.channel_name)
        RemoteGamer.connected.discard(self.username)
        print(f"bye {self.username} ({self.status})...")
        # purge invitations

        if self.status == enu.Local.MODE:
            super().local_clear()
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
            case enu.Game.DENY:
                if data['message'] in self.invitations:
                    self.invitations.discard(data['message'])
                    target = data['message']
                    data['message'] = 'invitation'
                    await self.send_cs(target, data)
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
        await super().local(data)
        if data['type'] == enu.Local.QUIT:
            self.set_mode(enu.CStatus.IDLE)


# MATCH
    async def game_host(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.match.end(True)
                self.set_mode(enu.CStatus.IDLE)
                await self.match.broadcast(data)
            case enu.Game.INVITE:
                try :
                    promise = await httpx.AsyncClient().post(
                        url='http://chat:8000/api/v1/relations/blocked/', 
                        data=JSONRenderer().render({
                        "target":data['message'],
                        "author":self.username,
                    }))
                    if promise.status_code == 404:
                        data['type'] = enu.Game.INV_404
                    elif promise.status_code == 403:
                        data['type'] = enu.Game.INV_FOR
                    elif data['message'] in RemoteGamer.connected:
                        await self.match.invite(data['message'])
                        data['type'] = enu.Game.INV_ACC
                    else:
                        data['type'] = enu.Game.INV_ABS
                except httpx.HTTPError as error:
                    print(f"er is : {error}")
                await self.send_json(data)
            case enu.Game.KICK:
                await self.match.kick(data['message'])
            case enu.Game.SETTINGS:
                newSettings = self.match.changeSettings(data['message'])
                await self.match.broadcast({"type":enu.Game.SETTINGS, "author":self.username, "message":newSettings})
            case enu.Game.START:
                if self.match.ready() is True:
                    await self.match.start()
                    await self.gaming({"message":"startButton"})
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


    async def game_accepted(self, data):
        if self.status != enu.Game.HOST:
            self.host = data['author']
            self.set_mode(enu.Game.GUEST)
        await self.send_json(data)

    async def game_broke(self, data):
        if self.status == enu.Game.HOST:
            await self.match.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

    async def game_deny(self, data):
        await self.send_json(data)

    async def game_end(self, data):
        if self.status == enu.Local.MODE:
            return await self.local_game_end(data)
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.match.end()
        self.set_mode()
        if self.status == enu.Tournament.GUEST or self.status == enu.Tournament.HOST:
            data['tournament'] = True
        else:
            data['tournament'] = False
        await self.send_json(data)

    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_join(self, data):
        if self.match.invited(data['author']) and self.match.full() is False and self.status == enu.Game.HOST:
            self.match.add(data['author'])
            data['message'] = self.match.game_state.to_dict('none')
            await self.send_json(data)
            plist = list(self.match._players)
            await self.match.broadcast({"type":enu.Game.ACCEPTED, "author":self.username, "message":self.match.game_state.to_dict('none'), "players":plist})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

    async def game_kick(self, data):
        if self.status == enu.CStatus.IDLE:
            self.invitations.discard(data['author'])
        elif data['author'] == self.host:
            self.host = None
            self.set_mode(enu.CStatus.IDLE)
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

    async def game_quit(self, data):
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.match.end(True)
        if data['author'] != self.username:
            await self.send_json(data)
            self.set_mode()

    async def game_update(self, data):
        if self.status == enu.Game.HOST and data['author'] != self.username:
            await self.gaming(data)
        else:
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

    async def game_resume(self, data):
        if data['author'] == self.username:
            return ;
        await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    async def game_settings(self, data):
        await self.send_json(data)

    async def game_score(self, data):
        await self.send_json(data)



# TOURNAMENT
    async def tournament_host(self, data):
        match data['type']:
            case enu.Tournament.QUIT:
                self.tournament.end(True)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Tournament.INVITE:
                await self.tournament.invite(data['message'])
            case enu.Tournament.SETTINGS:
                newSettings = self.tournament.changeSettings(data['message'])
                await self.tournament.broadcast({"type":enu.Game.SETTINGS, "author":self.username, "message":newSettings})
            case enu.Tournament.KICK:
                await self.tournament.kick(data['message'])
            case enu.Tournament.READY:
                await self.tournament.add_ready(self.username)
                if self.tournament.ready() is True:
                    await self.tournament.start()
                    await self.tournament.make_phase()
                    await self.tournament.order_match()
            case enu.Tournament.START:
                await self.tournament.start()
                await self.tournament.make_phase()
                await self.tournament.order_match()

    async def tournament_guest(self, data):
        match data['type']:
            case enu.Tournament.QUIT:
                await self.send_cs(self.thost, data)
                self.set_mode(enu.CStatus.IDLE)
            case enu.Tournament.READY:
                await self.send_cs(self.thost, data)
            case _: 
                await self.send_json({'type':enu.Errors.TYPE})

    async def tournament_accepted(self, data):
        self.thost = data['author']
        self.set_mode(enu.Tournament.GUEST)
        await self.send_json(data)

    async def tournament_broke(self, data):
        if self.status == enu.Tournament.HOST:
            await self.tournament.end(cancelled=True)
        self.set_mode()
        await self.send_json(data)

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

    async def tournament_kick(self, data):
        await self.send_json(data)
        self.set_mode()

    async def tournament_match(self, data):
        await self.send_json(data)
        if self.username == data['message']['host']:
            self.set_mode(enu.Game.HOST)
            self.match = Match(self.username, data['author'])
            self.match.add(data['message']['guest'])
        else: 
            self.set_mode(enu.Game.GUEST)
            self.host = data['message']['host']

    async def tournament_phase(self, data):
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

    async def tournament_result(self, data):
        if hasattr(self, "tournament") is False:
            return
        await self.tournament.update_result(data)

    async def tournament_start(self, data):
        await self.send_json(data)

    async def ournament_settings(self, data):
        await self.send_json(data)

    async def tournament_quit(self, data):
        await self.tournament.kick(data['message'])



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
"""
# when game/trn start -> send cancel to all invite
    async def mode_base(self, data):
        pass
        enu.Game2.QUIT: + cleanup/kick -> if lobby -> stop + clean, else send quit + set idle

    async def mode_idle(self, data):
        pass
        enu.Game2.CREATE        : + match/trn/local -> set mode
        enu.Invitation.ACCEPT   : -> relay to host -> wait for same
        enu.Invitation.REJECT   : -> relay to host

    async def mode_host(self, data):
        pass
        enu.Game2.NEXT      : -> only on local

        enu.Game2.DEFAULT : -> get lobby.default
        enu.Game2.SETTING   : lobby.changesettings + broadcast
        enu.Game2.INVITE    : + target -> lobby.invite 
        enu.Game2.KICK      : + target -> lobby.kick
        enu.Game2.START     : lobby.start -> change to start task

    async def mode_host_match(self, data):
        pass

        enu.Game2.READY     : lobby.ready
        enu.Game2.UNREADY   : lobby.unready
        enu.Game2.UPDATE    : gaemstate.game
        enu.Game2.PAUSE     : gaemstate.game -> change to cnacel task
        enu.Game2.RESUME    : gaemstate.game -> change to start task

    async def mode_guest_match(self, data):
        pass
        enu.Game2.READY     : send to host
        enu.Game2.UNREADY   : send to host
        enu.Game2.UPDATE    : send to host + format paddle
        enu.Game2.PAUSE     : send to host
        enu.Game2.RESUME    : send to host




# GENERAL (13)
    async def invitation_accept(self, data):
        # host : check if ok -> accept + relay or deny 
        # guest : relay + set mode to guest/trn
        pass

    async def invitation_reject(self, data):
        # host : relay + remove inv
        # guest : relay + remove inv
        pass

    async def game_settings(self, data):
        # host : change settings + broadcast
        # guest : relay
        pass


    async def game_kick(self, data):
        # guest : relay + kick (set to idle)
        pass

    async def game_quit(self, data):
        # guest : relay 
        # host : remove user from lobby + relay
        pass

    async def game_invite(self, data):
        # idle/all : add to invitation + relay
        pass

    async def game_ready(self, data):
        # guest : relay
        pass

    async def game_unready(self, data):
        # host : apply to lobby
        # guest : relay
        pass

    async def game_start(self, data):
        # guest : relay
        pass

    async def game_broke(self, data):
        # host : relay + broadcast + cleanup + set to idle
        # guest : relay + set to idle
        pass

    async def game_next(self, data):
        # local : ask next match
        pass


# MATCH (5)
    async def match_update(self, data):
        # guest: relay
        pass

    async def match_score(self, data):
        #guest: relay
        pass

    async def match_pause(self, data):
        #guest: relay
        #host: apply to match
        pass 

    async def match_resume(self, data):
        #guest: relay
        #host: apply to match
        pass

    async def match_end(self, data):
        #guest: relay
        pass

# TOURNAMENT (4)
    async def match_result(self, data):
        TRN -> #host: apply to trn
        pass

    async def tournament_phase(self, data):
        TRN -> #guest: relay
        pass

    async def tournament_match(self, data):
        TRN -> #guest: relay + prep for game
        pass

    async def tournament_result(self, data):
        TRN -> #guest: relay
        pass

"""
