import httpx

import channels.exceptions as exchan
from rest_framework.renderers import JSONRenderer

from game.consumers.local import LocalConsumer
import game.enums as enu

from game.lobby import Match, Tournament, LocalTournament, getDefault, LobbyException
from game.plaza import plaza, PlazaNotFound
from game.gamestate import getDefaultState

from logging import getLogger
logger = getLogger('base')

CHAN_EXCEPT = (exchan.AcceptConnection, exchan.DenyConnection,exchan.StopConsumer)

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
    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invited_by = {}
        self.status = enu.Game.IDLE
        self.mode = self.idle
        self.host = None
        self.host_tr = None

    async def connect(self):
        self.username = await authenticate(dict(self.scope['headers'])) 
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        plaza.join(self.username, self.channel_name)
        await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault(), "state":getDefaultState()})
        logger.info(f"JOIN: {self.username} ({self.status})")

    async def disconnect(self, close_code):
        if self.username is not None:
            await self.channel_layer.group_discard(self.username, self.channel_name)
        await self.quit(smooth=False)
        for invitor in self.invited_by:
            await self.send_cs(invitor, {'type':enu.Invitation.REJECT})
        plaza.leave(self.username)
        logger.info(f"QUIT: {self.username} ({self.status})")

    async def send_cs(self, target_name, data):
        data['author'] = self.username
        target = plaza.translate(target_name, raise_exception=True)
        await self.channel_layer.send(target, data)

    async def quit(self, smooth=True, cancelled=False):
        if hasattr(self, "lobby"):
            await self.lobby.end(smooth=smooth, cancelled=cancelled)
        if self.host is not None:
            await self.send_cs(self.host, {"type":enu.Game.QUIT})
        if self.host_tr is not None:
            await self.send_cs(self.host_tr, {"type":enu.Game.QUIT})
        self.set_mode(new_status=enu.Game.IDLE)

    def set_mode(self, new_status=None, new_host=None):
        logger.debug(f"{self.username} ({self.status}): setmode({new_status}, {new_host})")
        logger.debug(f"{self.username} ({self.status}): host({self.host}, {self.host_tr})")
        if new_status == None: 
            if self.host_tr is not None:
                if self.host_tr == self.username:
                    self.status = enu.Game.HOST
                else:
                    self.host = self.host_tr
                    self.status = enu.Game.GUEST
            else:
                self.host = None
                self.status = enu.Game.IDLE
        else:
            self.status = new_status
            if new_host is not None:
                self.host = new_host

        match self.status:
            case enu.Game.IDLE : 
                self.mode = self.idle
                self.host = None
                self.host_tr = None
            case enu.Game.LOCAL : self.mode = self.local
            case enu.Game.HOST : self.mode = self.mode_host
            case enu.Game.GUEST : self.mode = self.mode_guest
            case enu.Match.HOST : self.mode = self.mode_playing_match_host
            case enu.Match.GUEST : self.mode = self.mode_playing_match_guest

    async def receive_json(self, json_data):
        json_data['author'] = self.username
        if json_data['type'] == enu.Errors.DECODE:
            await self.send_json({'type':enu.Errors.DECODE})
        elif json_data['type'] == enu.Game.QUIT: 
            await self.quit(smooth=False, cancelled=True)
        elif json_data['type'] == enu.Game.DEFAULT:
            await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault(), "state":getDefaultState()})
        else:
            await self.mode(json_data)

    #  MODE (5)
    async def idle(self, data):
        match data['type']:
            case enu.Game.CREATE:
                if data['mode'] == enu.Game.MATCH:
                    self.lobby = Match(host=self.username)
                    self.set_mode(new_status=enu.Game.HOST)
                elif data['mode'] == enu.Game.TRN:
                    self.host_tr = self.username
                    self.lobby = Tournament(host=self.username)
                    self.set_mode(new_status=enu.Game.HOST)
                elif data['mode'] == enu.Game.LOCAL:
                    self.host_tr = self.username
                    self.lobby = LocalTournament(host=self.username, host_channel_name=self.channel_name)
                    self.set_mode(new_status=enu.Game.LOCAL)
                await self.lobby._init()
            case enu.Invitation.ACCEPT | enu.Invitation.REJECT:
                if data['message'] in self.invited_by:
                    await self.send_cs(data['message'], data)

    async def mode_host(self, data):
        match data['type']:
            case enu.Game.NEXT: logger.debug(f"PING: {self.username} ({self.status})")
            case enu.Game.SETTING:
                settings = self.lobby.changeSettings(settings=data['message'])
                await self.lobby.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.SETTING, "message":settings, "state":getDefaultState()}})
            case enu.Game.INVITE:
                to_user = data['user']
                response = await getInviteAuth(self.username, to_user)
                response['user'] = to_user
                response['mode'] = data['mode']
                if response['type'] == enu.Invitation.VALID:
                    if await self.lobby.invite(to_user):
                        await self.send_json(response)
                else:
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

    async def mode_guest(self, data):
        if data['type'] == enu.Game.READY:
            await self.send_cs(self.host, data)
        elif data['type'] == enu.Game.NEXT:
            logger.info(f"PING: {self.username} ({self.status})")

    async def mode_playing_match_host(self, data):
        if data['type'] == enu.Match.UPDATE:
            data['message'] = format_paddle_key(True, data['message'])
            await self.lobby.match_feed(data)
        elif data['type'] == enu.Match.PAUSE:
            await self.lobby.match_pause(self.username)
        elif data['type'] == enu.Game.READY:
            await self.lobby.check(self.username)
            if self.lobby.checked():
                await self.lobby.start()
        elif data['type'] == enu.Game.NEXT:
            await self.send_json(data)

    async def mode_playing_match_guest(self, data):
        if data['type'] == enu.Match.UPDATE or data['type'] == enu.Match.RESUME or data['type'] == enu.Match.PAUSE or data['type'] == enu.Game.READY:
            await self.send_cs(self.host, data)
        elif data['type'] == enu.Game.NEXT:
            await self.send_json(data)

    # GENERAL (8)
    async def game_invite(self, data):
        self.invited_by[data['author']] = data['mode']
        await self.send_json(data)

    async def invitation_accept(self, data):
        logger.error(f"{self.username} ({self.status}): inv accp from: {data['author']}, full {data}")
        author = data['author']
        if author == self.username:
            return await self.send_json(data)
        if self.status == enu.Game.IDLE and author in self.invited_by:
            data['mode'] = self.invited_by[author]
            if data['mode'] == enu.Game.TRN:
                self.host_tr = author
            data['by'] = True
            await self.send_json(data)
            self.host = author
            self.set_mode(new_status=enu.Game.GUEST)
            del self.invited_by[author]
        elif hasattr(self, "lobby"):
            if self.lobby.invited(author) and await self.lobby.add(author):
                data['players'] = self.lobby.players
                data['by'] = False
                data['message'] = author
                if hasattr(self.lobby, "tournament"):
                    data['players'] = {'host':self.lobby.players[0], 'guest':self.lobby.players[1]}
                await self.send_cs(author, data)
                await self.send_json(data)
            else:
                await self.send_cs(author, {"type":enu.Invitation.REJECT})

    async def invitation_reject(self, data):
        author = data['author']
        if author in self.invited_by:
            del self.invited_by[author]
            data['by'] = True
        elif hasattr(self, "lobby"):
            self.lobby.uninvite(author)
            data['by'] = False
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] != self.username:
            if data['author'] == self.host_tr:
                if hasattr(self, "lobby"):
                    await self.lobby.end(cancelled=True)
                    del self.lobby
                self.set_mode(new_status=enu.Game.IDLE)
                await self.send_json(data)
            elif data['author'] == self.host:
                self.set_mode()
                if self.host_tr is None: 
                    await self.send_json(data)


    async def game_quit(self, data):
        if hasattr(self, "lobby"):
            if isinstance(self.lobby, Tournament):
                if hasattr(self.lobby, "current") and data['author'] in self.lobby.players:
                    logger.debug(f"{self.username} ({self.status}): should cheat and make {data['author']} loose")
                    await self.lobby.cheat(data['author'])
                else:
                    logger.debug(f"{self.username} ({self.status}): should quietly remove {data['author']}")
                    await self.lobby.remove(data['author'])
            elif isinstance(self.lobby, Match):
                await self.lobby.end(cancelled=True)
                del self.lobby
                self.set_mode()
                if self.status == enu.Game.IDLE:
                    await self.send_json({'type':enu.Game.KICK, 'author':self.username})
            await self.send_json(data)
        else:
            if self.host_tr == data['author']:
                self.set_mode(new_status=enu.Game.IDLE)
            else:
                self.set_mode()
            await self.send_json(data)

    async def game_ready(self, data):
        if data['author'] == self.username:
            return 
        if hasattr(self, "lobby"):
            if await self.lobby.check(data['author']):
                if self.lobby.checked():
                    await self.lobby.start()
        await self.send_json(data)

    async def game_next(self, data):
        await self.send_json(data)

    # MATCH (3)
    async def match_start(self, data):
        if self.status == enu.Game.HOST:
            self.set_mode(new_status=enu.Match.HOST)
        elif self.status == enu.Game.GUEST:
            self.set_mode(new_status=enu.Match.GUEST)
        await self.send_json(data)

    async def match_end(self, data):
        if self.status == enu.Game.LOCAL:
            await self.lobby.update_result(data)
        else:
            if hasattr(self, "lobby") and self.username != self.host_tr:
                await self.lobby.end()
                del self.lobby
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
        if self.host_tr == data['host_tr'] and self.host_tr == self.username:
            await self.send_json(data)
            await self.lobby.update_result(data['message'])

    async def tournament_phase(self, data):
        if self.host_tr == data['host_tr']:
            await self.send_json(data)

    async def tournament_match(self, data):
        if self.host_tr == data['host_tr']:
            match = data['match']
            if match['host'] == self.username:
                self.set_mode(new_status=enu.Match.HOST)
                self.lobby = Match(host=self.username, tournament=self.host, settings=data['settings'])
                await self.lobby._init()
                await self.lobby.add(match['guest'])
            else:
                self.set_mode(new_status=enu.Match.GUEST, new_host=match['host'])
            await self.send_json(data)

    async def tournament_end(self, data):
        if self.host_tr == data['host_tr']:
            await self.send_json(data)
            if self.username == self.host_tr:
                await self.lobby.end()
            self.set_mode(new_status=enu.Game.IDLE)
            self.host = None
            self.host_tr = None



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
        logger.warning(f"invitation error : {error}")
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

