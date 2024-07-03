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


    START = "game.start"
    PAUSE = "game.pause"
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
    PHASE = "tournament.phase"
    MATCH = "tournament.match"
    RESULT = "tournament.result"
    BROKE = "tournament.broke"


class CStatus(enum.StrEnum):
    IDLE = "status.idle"
    LOCAL = "status.local"
    HOST = "status.host"
    GUEST = "status.guest"

    GHOST = "status.game.host"
    GGUEST = "status.game.guest"
    THOST = "status.game.host"
    TGUEST = "status.game.guest"

