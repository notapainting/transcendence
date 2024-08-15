import enum

class Errors(enum.StrEnum):
    HANDLER = 'error.handler'
    INTERN  = 'error.internal'
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


class Game(enum.StrEnum):
    CREATE  = "game.create"
    SETTING = "game.settings"
    DEFAULT = "game.default"
    KICK    = "game.kick"
    QUIT    = "game.quit"
    INVITE  = "game.invite"
    READY   = "game.ready"
    START   = "game.start"
    NEXT    = "game.next"
    RELAY   = "game.relay"
    IDLE    = "game.idle"
    HOST    = "game.host"
    GUEST   = "game.guest"
    LOCAL   = "game.local"
    MATCH   = "game.match"
    TRN     = "game.tournament"


class Match(enum.StrEnum):
    HOST    = "match.host"
    GUEST   = "match.guest"
    UPDATE  = "match.update"
    SCORE   = "match.score"
    PAUSE   = "match.pause" 
    RESUME  = "match.resume"
    END     = "match.end"
    RESULT  = "match.result"
    START   = "match.start"
    GO      = "match.go"

class Tournament(enum.StrEnum):
    PHASE   = "tournament.phase"
    MATCH   = "tournament.match"
    RESULT  = "tournament.result"
    END  = "tournament.end"



class CStatus(enum.StrEnum):
    IDLE    = "status.idle"
    HOST    = "status.host"
    GUEST   = "status.guest"