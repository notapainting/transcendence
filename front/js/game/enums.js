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

export const Game = Object.freeze({
    CREATE  : "game.create",
    SETTING : "game.settings",
    QUIT    : "game.quit",
    INVITE  : "game.invite",
    KICK    : "game.kick",
    READY   : "game.ready",
    START   : "game.start",
    BROKE   : "game.broke",
    DEFAULT : "game.default",
    NEXT    : "game.next",
    IDLE    : "game.idle",
    LOCAL   : "game.local",
    MATCH   : "game.match",
    TRN     : "game.tournament",
})

export const Match = Object.freeze({
    UPDATE  :   "match.update",
    SCORE   :   "match.score",
    PAUSE   :   "match.pause",
    RESUME  :   "match.resume",
    END     :   "match.end",
    RESULT  :   "match.result",
    START   :   "match.start",
})

export const Tournament = Object.freeze({
    PHASE   : "tournament.phase",
    MATCH   : "tournament.match",
    RESULT  : "tournament.result",
    END     : "tournament.end",
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
