import enum

class Error(enum.StrEnum):
    DECODE = "error.decode"
    ENCODE = "error.encode"


class Game(enum.StrEnum):
    CREATE = "game.create"
    INVITE = "game.invite"
    JOIN = "game.join"
    QUIT = "game.quit"
    READY = "game.ready"
    START = "game.start"
    PAUSE = "game.pause"

class Tournament(enum.StrEnum):
    CREATE = "tournament.create"
    QUIT = "tournament.quit"

class Event(enum.StrEnum):
    PADDLE = "paddle.update"

class CStatus(enum.StrEnum):
    IDLE = "cs.idle"
    HOST = "cs.host"
    GUEST = "cs.guest"

    """
    idle

    no game
    host game
    joined game
    
    no trn
    host trn
    joined trn

{
    "type":"game.create"
}

{
    "type":"game.invite",
    "data":"target"
}

    wbs receive : 
        LOBBY CREATION
        - game.create -> put cs in host mode = create GameState, create lobby (group)
        - game.invite -> send game inviteation
        - game.join -> accept game inviteation = join lobby
        - game.quit -> quit actual lobby (if any)
        - game.ready -> player set status to ready
            -> if all ready -> start loop
        GAME RUNNING
        if host :
        - paddle.update -> player send update on paddle position
        - game.pause -> player ask for pause game -> pause loop
        - game.resume -> player ask for resume game -> resume loop
        else:
        - paddle.update -> 
        - game.pause -> 
        - game.resume -> transfert to cs host


        - tounament.create -> put cs in host mode (tournament) = create Tournament, create lobby
        - tournament.quit -> quit tournament lobby
    """
    async def receive2(self, data):
        await self.channel_layer.send('host', data)

    async def game_update(self, data):
        await self.send(json.dumps(self.game_state.to_dict('none')))

    async def game_invitee(self, data):
        pass