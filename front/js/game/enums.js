export const Error = Object.freeze({ 
    DECODE  : "error.decode",
    ENCODE  : "error.encode",
    TYPE    : "error.type",
    DATA    : "error.data",
    HANDLER : "error.handler",
    ABSENT  : "error.absent",
    FBD_403 : "error.forbidden",
    NTF_404 : "error.not_found",
})

export const Invitation = Object.freeze({ 
    VALID   : "invitation.valid",
    ERROR   : "invitation.error",
    ACCEPT  : "invitation.accept",
    REJECT  : "invitation.reject",
    MATCH   : "invitation.match",
    TRN     : "invitation.tournament",
})

export const EventGame = Object.freeze({
    CREATE  : "game.create",
    SETTING : "game.settings",
    QUIT    : "game.quit",
    INVITE  : "game.invite",
    KICK    : "game.kick",
    READY   : "game.ready",
    UNREADY : "game.unready",
    START   : "game.start",
    BROKE   : "game.broke",
    DEFAULT : "game.defaults",
    NEXT    : "game.next",
    IDLE    : "game.idle",
    LOCAL   : "game.local",
    MATCH   : "game.match",
    TRN     : "game.tournament",

    // will be deprecated
    INV_ACC     :   "invite.valid",
    INV_404     :   "invite.404",
    INV_FOR     :   "invite.forbidden",
    INV_ABS     :   "invite.absent",
    JOIN        :   "game.join",
    ACCEPTED    :   "game.accepted",
    DENY        :   "game.deny",
    UPDATE      :   "game.update",
    SCORE       :   "game.score",
    PAUSE       :   "game.pause",
    RESUME      :   "game.resume",
    END         :   "game.end",
    SETTINGS    :   "game.settings",
    SETTINGS_DEF:   "game.settings.default",
})

export const EventMatch = Object.freeze({
    ID      :   "match.match",
    UPDATE  :   "match.update",
    SCORE   :   "match.score",
    PAUSE   :   "match.pause",
    RESUME  :   "match.resume",
    END     :   "match.end",
    RESULT  :   "match.result"
})

export const EventTournament = Object.freeze({
    ID      : "tournament.tournament",
    PHASE   : "tournament.phase",
    MATCH   : "tournament.match",
    RESULT  : "tournament.result",
    END     : "tournament.end",

    // will be deprecated
    CREATE: "tournament.create",
    INVITE: "tournament.invite",
    DENY: "tournament.deny",
    JOIN: "tournament.join",
    QUIT: "tournament.quit",
    KICK: "tournament.kick",
    ACCEPTED: "tournament.accepted",
    READY: "tournament.ready",
    START: "tournament.start",
    BROKE: "tournament.broke",
    SETTINGS: "tournament.settings",
})

// will be deprecated
export const EventLocal = Object.freeze({
    MODE: "local.mode",
    SETTINGS : EventTournament.SETTINGS,
    PLAYERS: "local.players",
    PHASE: EventTournament.PHASE,
    MATCH: EventTournament.MATCH,
    READY: EventGame.READY,
    UPDATE: EventGame.UPDATE,
    SCORE: EventGame.SCORE,
    NEXT: EventGame.NEXT,
    END_GAME: "local.end.game",
    END_TRN: "local.end.tournament",
    QUIT: EventGame.QUIT,
})

// will be deprecated
export const EventError = Object.freeze({
    TYPE: "error.type",
    DATA: "error.data",
})

export const sceneIdx = Object.freeze({
    WELCOME: 0,
    CREATION:1,
    WAITING:2,
    PHASE:3,
    PREMATCH:4,
    MATCH:5,
    END:6,
    END_TR:7,
    BROKE:8,
})

export const gameMode = Object.freeze({
    LOCAL: 0,
    MATCH: 1,
    TOURNAMENT: 2,
})

export const backendPath = Object.freeze({
    LOCAL: "/game/local/",
    REMOTE: "/game/",
});
