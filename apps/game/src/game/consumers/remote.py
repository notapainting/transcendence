import asyncio, random, httpx

import channels.exceptions as exchan
from rest_framework.renderers import JSONRenderer

from game.consumers.base import BaseConsumer
from game.consumers.local import LocalConsumer
from game.gamestate import GameState, remote_loop
import game.enums as enu


from game.lobby import Match, Tournament, LocalTournament, getDefault, LobbyException
from game.plaza import plaza, PlazaException

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


class ErrorDecode(Exception):
    pass

# add delay start match
# add delay after trn end

# idle -> game.host -> match.host

class RemoteGamer(LocalConsumer):
    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invited_by = {}
        self.status = enu.Game.IDLE
        self.mode = self.idle
        self.loopback = self.status
        # self.lobby = None
        # self.loopback_looby = None

    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers'])) 
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        plaza.join(self.username, self.channel_name)
        await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault()})
        print(f"hello {self.username} ({self.status})! ({self.channel_name})")

    async def disconnect(self, close_code):
        if self.username is not None:
            await self.channel_layer.group_discard(self.username, self.channel_name)
        await self.quit()
        plaza.leave(self.username)
        print(f"bye {self.username} ({self.status})...")

    async def send_cs(self, target_name, data):
        data['author'] = self.username
        target = plaza.translate(target_name, raise_exception=True)
        await self.channel_layer.send(target, data)

    """
           if hasattr(self, "loopback_lobby"):
                self.lobby = self.loopback_lobby
                del self.loopback_lobby
            
            if hasattr(self, "lobby"):
                self.loopback_lobby = self.lobby
    """

    def set_mode(self, status=None):
        if status == None:
            self.status = self.loopback
        else:
            if status != enu.Match.HOST and status != enu.Match.GUEST:
                self.loopback = self.status
            elif status == enu.Game.IDLE:
                self.loopback = senu.Game.IDLE
            self.status = status
        match self.status:
            case enu.Game.IDLE : self.mode = self.idle
            case enu.Game.LOCAL : self.mode = self.local
            case enu.Game.HOST : self.mode = self.mode_host
            case enu.Game.GUEST : self.mode = self.mode_guest
            case enu.Match.HOST : self.mode = self.mode_playing_match_host
            case enu.Match.GUEST : self.mode = self.mode_playing_match_guest

    async def receive_json(self, json_data):
        json_data['author'] = self.username
        try :
            if json_data['type'] == enu.Errors.DECODE:
                return await self.send_json({'type':enu.Errors.DECODE})
            match json_data['type']:
                case enu.Game.QUIT: await self.quit()
                case enu.Game.DEFAULT: await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault()})
                case _: await self.mode(json_data)
        except LobbyException as lob:
            await self.send_json({"type":enu.Errors.LOBBY})
        except PlazaException as e:
            print(f"plerror: {e}")
        # except BaseException as e:
        #     print(f"berror: {e}")


    async def quit(self, smooth=True):
        if self.status == enu.Game.LOCAL:
            await self.lobby.end()
        else:
            if self.status == enu.Match.HOST:
                await self.lobby.end(False)
            elif self.status == enu.Match.GUEST:
                await self.send_cs(self.host, {"type":enu.Game.QUIT})
            elif self.status == enu.Game.HOST:
                await self.lobby.end(smooth)
            elif self.status == enu.Game.GUEST:
                await self.send_cs(self.host, {"type":enu.Game.QUIT})
            self.set_mode()

            if self.status == enu.Game.HOST:
                await self.lobby.end()
            elif self.status == enu.Game.GUEST:
                await self.send_cs(self.host, {"type":enu.Game.QUIT})

        self.set_mode(enu.Game.IDLE)

    async def idle(self, data):
        match data['type']:
            case enu.Game.CREATE:
                if data['mode'] == enu.Game.MATCH:
                    self.lobby = Match(host=self.username, )
                    self.set_mode(enu.Game.HOST)
                elif data['mode'] == enu.Game.TRN:
                    self.lobby = Tournament(host=self.username)
                    self.set_mode(enu.Game.HOST)
                elif data['mode'] == enu.Game.LOCAL:
                    self.lobby = LocalTournament(host=self.username, host_channel_name=self.channel_name)
                    self.set_mode(enu.Game.LOCAL)
                await self.lobby._init()
            case enu.Invitation.ACCEPT | enu.Invitation.REJECT:
                if data['message'] in self.invited_by:
                    await self.send_cs(data['message'], data)

    async def mode_host(self, data):
        match data['type']:
            case enu.Game.NEXT:
                await self.lobby.next()
            case enu.Game.SETTING:
                settings = self.lobby.changeSettings(settings=data['message'])
                await self.lobby.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.SETTING, "message":settings}})
            case enu.Game.INVITE:
                to_user = data['user']
                response = await getInviteAuth(self.username, to_user)
                if response['type'] == enu.Invitation.VALID:
                    await self.lobby.invite(to_user)
                response['user'] = to_user
                response['mode'] = data['mode']
                await self.send_json(response) 
            case enu.Game.KICK:
                await self.lobby.kick(data['message'])
            case enu.Game.START:
                if self.lobby.checked():
                    await self.lobby.start()
            case enu.Game.READY:
                await self.lobby.check(self.username)
                if self.lobby.checked():
                    await self.lobby.start()
            case enu.Game.GO:
                await self.lobby.go()

    async def mode_guest(self, data):
        match data['type']:
            case enu.Game.READY:
                await self.send_cs(self.host, data)


    async def mode_playing_match_host(self, data):
        match data['type']:
            case enu.Game.READY :
                await self.lobby.match_start()
            case enu.Match.UPDATE :
                data['message'] = format_paddle_key(True, data['message'])
                await self.lobby.match_feed(data)
            case enu.Match.PAUSE :
                await self.lobby.match_pause(self.username)

    async def mode_playing_match_guest(self, data):
        match data['type']:
            case enu.Match.UPDATE | enu.Match.RESUME | enu.Match.PAUSE:
                await self.send_cs(self.host, data)

# GENERAL (8)
    async def game_invite(self, data):
        self.invited_by[data['author']] = data['mode']
        await self.send_json(data)

    async def invitation_accept(self, data):
        author = data['author']
        if author == self.username:
            return await self.send_json(data)
        if self.status == enu.Game.IDLE:
            data['mode'] = self.invited_by[author]
            await self.send_json(data)
            self.host = author
            self.set_mode(enu.Game.GUEST)
            del self.invited_by[author]
        else :
            if self.lobby.invited(author) and await self.lobby.add(author):
                data['players'] = self.lobby.players
                if hasattr(self.lobby, "game_state"):
                    print("we got a gamestate")
                    data['message'] = self.lobby.game_state.to_dict()
                return await self.lobby.broadcast(data)
            await self.send_cs(author, {"type":enu.Invitation.REJECT})

    async def invitation_reject(self, data):
        author = data['author']
        if author in self.invited_by:
            del self.invited_by[author]
            data['by'] = True
        else :
            self.lobby.invitations.remove(author)
            data['by'] = False
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] != self.username:
            if data['author'] == self.host:
                self.host = None
                self.set_mode(enu.Game.IDLE)
            await self.send_json(data)

    async def game_quit(self, data):
        if hasattr(self, "lobby"):
            await self.lobby.remove(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if data['author'] == self.username:
            return 
        if hasattr(self, "lobby"):
            await self.lobby.check(data['author'])
            if self.lobby.checked():
                await self.lobby.start()
        await self.send_json(data)

    async def game_broke(self, data):
        # host : relay + broadcast + cleanup + set to idle
        # guest : relay + set to idle
        await self.send_json(data)

    async def game_next(self, data):
        # local : ask next match
        await self.send_json(data)

# MATCH (3)
    async def match_start(self, data):
        if self.status == enu.Game.HOST:
            self.set_mode(enu.Match.HOST)
        else:
            self.set_mode(enu.Match.GUEST)
        await self.send_json(data)

    async def match_go(self, data):
        if hasattr(self, "lobby"):
            await self.lobby.go()

    async def match_end(self, data):
        if hasattr(self, "lobby"):
            await self.lobby.end()
        self.set_mode()
        await self.send_json(data)

    async def match_update(self, data):
        data['message'] = format_paddle_key(False, data['message'])
        await self.lobby.match_feed(data)

    async def match_pause(self, data):
        if hasattr(self, "lobby") and data['author'] != "system":
            await self.lobby.match_pause(data['author'])
        await self.send_json(data)


# TOURNAMENT (4)
    async def match_result(self, data):
        # TRN -> #host: apply to trn
        await self.send_json(data)

    async def tournament_phase(self, data):
        # TRN -> #guest: relay
        await self.send_json(data)

    async def tournament_match(self, data):
        # TRN -> #guest: relay + prep for game
        await self.send_json(data)

    async def tournament_result(self, data):
        # TRN -> #guest: relay
        await self.send_json(data)

async def getInviteAuth(author, user):
    try :
        promise = await httpx.AsyncClient().post(
                    url='http://chat:8000/api/v1/relations/blocked/', 
                    data=JSONRenderer().render({
                    "target":user,
                    "author":author}))
        if promise.status_code == 200:
            if plaza.found(user):
                return {"type":enu.Invitation.VALID}
            else:
                return {"type":enu.Invitation.ERROR, "error":enu.Errors.ABSENT}
        elif promise.status_code == 403:
            return {"type":enu.Invitation.ERROR, "error":enu.Errors.FBD_403}
        elif promise.status_code == 404:
            return {"type":enu.Invitation.ERROR, "error":enu.Errors.NTF_404} 
        else:
            return {"type":enu.Invitation.ERROR, "error":enu.Errors.INTERN} 
    except httpx.HTTPError as error:
        print(f"er is : {error}")
        return {"type":enu.Invitation.ERROR, "error":enu.Errors.INTERN}

def format_paddle_key(host, key):
    if host is True:
        match key:
            case 'downPressed' | 'sPressed': return 'sPressed'
            case 'downRelease' | 'sRelease': return 'sRelease'
            case 'upPressed' | 'wPressed': return 'wPressed'
            case 'upRelease' | 'wRelease': return 'wRelease'
            case '_': return key
    else:
        match key:
            case 'downPressed' | 'sPressed': return 'downPressed'
            case 'downRelease' | 'sRelease': return 'downRelease'
            case 'upPressed' | 'wPressed': return 'upPressed'
            case 'upRelease' | 'wRelease': return 'upRelease'
            case '_': return key




"""
class DEADRemoteGamer(LocalConsumer):
    connected = {}

    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invitations = set()
        self.status = enu.Game.IDLE
        self.mode = self.idle
        self.loopback = self.status

    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers'])) 
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        plaza.join(self.username, self.channel_name)
        await self.channel_layer.group_add(self.username, self.channel_name)
        await self.send_json({"type":enu.Game.SETTINGS_DEF, "message":getDefault()})
        print(f"hello {self.username} ({self.status})!")

    async def disconnect(self, close_code):
        if self.username is not None:
            await self.channel_layer.group_discard(self.username, self.channel_name)
        plaza.leave(self.username)
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
            case enu.Game.IDLE : self.mode = self.idle
            case enu.Local.MODE : self.mode = self.local
            case enu.Game.HOST : self.mode = self.game_host
            case enu.Game.GUEST : self.mode = self.game_guest
            case enu.Tournament.HOST : self.mode = self.tournament_host
            case enu.Tournament.GUEST : self.mode = self.tournament_guest

    async def receive_json(self, json_data):
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
            self.set_mode(enu.Game.IDLE)


# MATCH
    async def game_host(self, data):
        match data['type']:
            case enu.Game.QUIT:
                await self.match.end(True)
                self.set_mode(enu.Game.IDLE)
                await self.match.broadcast(data)
            case enu.Game.INVITE:
                response = await self.getInviteAuth(data['message'])
                response['message'] = data['message']
                await self.send_json(response)
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
                self.set_mode(enu.Game.IDLE)
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
            data['message'] = self.match.game_state.to_dict()
            await self.send_json(data)
            plist = list(self.match._players)
            await self.match.broadcast({"type":enu.Game.ACCEPTED, "author":self.username, "message":self.match.game_state.to_dict(), "players":plist})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

    async def game_kick(self, data):
        if self.status == enu.Game.IDLE:
            self.invitations.discard(data['author'])
        elif data['author'] == self.host:
            self.host = None
            self.set_mode(enu.Game.IDLE)
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
                self.set_mode(enu.Game.IDLE)
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
                self.set_mode(enu.Game.IDLE)
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

 """
