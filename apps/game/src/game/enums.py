import enum

class Errors(enum.StrEnum):
    DECODE = "error.decode"
    ENCODE = "error.encode"
    TYPE = "error.type"
    DATA = "error.data"




class Game(enum.StrEnum):
    HOST = "game.host"
    GUEST = "game.guest"

    CREATE = "game.create"
    INVITE = "game.invite"
    JOIN = "game.join"
    QUIT = "game.quit"
    READY = "game.ready"
    UNREADY = "game.unready"
    KICK = "game.kick"
    ACCEPTED = "game.accepted"
    DENY = "game.deny"
    BROKE = "game.broke"
    UPDATE = "game.update"
    SCORE = "game.score"

    START = "game.start"
    PAUSE = "game.pause"
    RESUME = "game.resume"
    END = "game.end"

class Tournament(enum.StrEnum):
    HOST = "tournament.host"
    GUEST = "tournament.guest"

    CREATE = "tournament.create"
    INVITE = "tournament.invite"
    JOIN = "tournament.join"
    QUIT = "tournament.quit"
    KICK = "tournament.kick"
    ACCEPTED = "tournament.accepted"
    READY = "tournament.ready"
    PHASE = "tournament.phase"
    MATCH = "tournament.match"
    RESULT = "tournament.result"
    BROKE = "tournament.broke"


class Local(enum.StrEnum):
    PLAYERS = "local.players"
    PHASE = "local.phase"
    MATCH = "local.match"
    READY = Game.READY
    UPDATE = Game.UPDATE
    SCORE = Game.SCORE
    PAUSE = Game.PAUSE
    NEXT = "local.next"
    END_GAME = "local.end.game"
    END_TRN = "local.end.tournament"
    QUIT = Game.QUIT

class CStatus(enum.StrEnum):
    IDLE = "status.idle"
