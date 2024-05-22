import enum

class Errors(enum.StrEnum):
    DECODE = "error.decode"
    ENCODE = "error.encode"
    TYPE = "error.type"
    DATA = "error.data"


class Game(enum.StrEnum):
    CREATE = "game.create"
    INVITE = "game.invite"
    JOIN = "game.join"
    QUIT = "game.quit"
    READY = "game.ready"
    KICK = "game.kick"

    CANCEL = "game.cancel"
    ACCEPTED = "game.accepted"
    DENY = "game.deny"
    START = "game.start"
    PAUSE = "game.pause"

class Tournament(enum.StrEnum):
    CREATE = "tournament.create"
    QUIT = "tournament.quit"


class CStatus(enum.StrEnum):
    IDLE = "cs.idle"
    HOST = "cs.host"
    GUEST = "cs.guest"

