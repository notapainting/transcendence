import enum

class Errors(enum.StrEnum):
    HANDLER = 'error.handler'
    ENCODE  = "error.encode"

    TYPE    = "error.type"
    DATA    = "error.data"
    DECODE  = "error.decode"

    LOBBY   = "error.lobby"
    ABSENT  = "error.absent"
    FBD_403 = "error.forbidden"
    NTF_404 = "error.not_found"

class Invitation(enum.StrEnum):
    VALID   = "invitation.valid"
    ERROR   = "invitation.error"
    ACCEPT  = "invitation.accept"
    REJECT  = "invitation.reject"
    MATCH   = "invitation.match"
    TRN     = "invitation.tournament"

"""
class Game(enum.StrEnum):








"""

class Game(enum.StrEnum):
    CREATE  = "game.create"
    SETTING = "game.settings"
    DEFAULT = "game.defaults"
    KICK    = "game.kick"
    QUIT    = "game.quit"
    INVITE  = "game.invite"
    READY   = "game.ready"
    UNREADY = "game.unready"
    START   = "game.start"
    BROKE   = "game.broke"
    NEXT    = "game.next"
    RELAY   = "game.relay"
    IDLE    = "game.idle"
    LOCAL   = "game.local"
    MATCH   = "game.match"
    TRN     = "game.tournament"

# will be deprecated
    HOST = "game.host"
    GUEST = "game.guest"
    SETTINGS = "game.settings"
    SETTINGS_DEF = "game.settings.default"
    INV_ACC = "invite.valid"
    INV_404 = "invite.404"
    INV_FOR = "invite.forbidden"
    INV_ABS = "invite.absent"
    JOIN = "game.join"
    ACCEPTED = "game.accepted"
    DENY = "game.deny"
    UPDATE = "game.update"
    SCORE = "game.score"
    PAUSE = "game.pause" 
    RESUME = "game.resume"
    END = "game.end"

class Match(enum.StrEnum):
    ID      = "match.match"
    HOST    = "match.host"
    GUEST   = "match.guest"
    UPDATE  = "match.update"
    SCORE   = "match.score"
    PAUSE   = "match.pause" 
    RESUME  = "match.resume"
    END     = "match.end"
    RESULT  = "match.result"

class Tournament(enum.StrEnum):
    ID      = "tournament.tournament"
    HOST    = "tournament.host"
    GUEST   = "tournament.guest"
    PHASE   = "tournament.phase"
    MATCH   = "tournament.match"
    RESULT  = "tournament.result"
    END  = "tournament.end"

# will be deprecated
    SETTINGS = Game.SETTINGS
    CREATE = "tournament.create"
    INVITE = "tournament.invite"
    DENY = "tournament.deny"
    JOIN = "tournament.join"
    QUIT = "tournament.quit"
    KICK = "tournament.kick"
    ACCEPTED = "tournament.accepted"
    READY = "tournament.ready"
    START = "tournament.start"
    BROKE = "tournament.broke"

# will be deprecated
class Local(enum.StrEnum):
    MODE = "local.mode"
    SETTINGS = Tournament.SETTINGS
    PLAYERS = "local.players"
    PHASE = "local.phase"
    MATCH = "local.match"
    READY = Game.READY
    # UPDATE = Game.UPDATE
    # SCORE = Game.SCORE
    # PAUSE = Game.PAUSE
    NEXT = "local.next"
    END_GAME = "local.end.game"
    END_TRN = "local.end.tournament"
    QUIT = Game.QUIT

    UPDATE  = "match.update"
    SCORE   = "match.score"
    PAUSE   = "match.pause" 
    RESUME  = "match.resume"
    END     = "match.end"
    RESULT  = "match.result"


class CStatus(enum.StrEnum):
    IDLE = "status.idle"