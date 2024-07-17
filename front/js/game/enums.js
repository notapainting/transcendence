export const EventGame = Object.freeze({
    CREATE: "game.create",
    INVITE: "game.invite",
    JOIN: "game.join",
    QUIT: "game.quit",
    READY: "game.ready",
    UNREADY: "game.unready",
    KICK: "game.kick",
    ACCEPTED: "game.accepted",
    DENY: "game.deny",
    UPDATE: "game.update",
    SCORE: "game.score",
    START: "game.start",
    PAUSE: "game.pause",
    RESUME: "game.resume",
    END: "game.end",
    BROKE: "game.broke",
})

export const EventTournament = Object.freeze({
    CREATE: "tournament.create",
    INVITE: "tournament.invite",
    JOIN: "tournament.join",
    QUIT: "tournament.quit",
    KICK: "tournament.kick",
    ACCEPTED: "tournament.accepted",
    READY: "tournament.ready",
    PHASE: "tournament.phase",
    MATCH: "tournament.match",
    RESULT: "tournament.result",
    BROKE: "tournament.broke",
    END: "tournament.end",
})

export const EventLocal = Object.freeze({
    PLAYERS: "local.players",
    PHASE: "local.phase",
    MATCH: "local.match",
    UPDATE: EventGame.UPDATE,
    SCORE: EventGame.SCORE,
    NEXT: "local.next",
    END_GAME: "local.end.game",
    END_TRN: "local.end.tournament",
    QUIT: EventGame.QUIT,
})

export const EventError = Object.freeze({
    TYPE: "error.type",
    DATA: "error.data",
})

export const sceneIdx = Object.freeze({
    WELCOME: 0,
    CREATION:1,
    WAITING:2,
    PHASES:3,
    PREMATCH:4,
    MATCH:5,
    END:6,
    END_TR:7,
    BROKE:8,
})

export const sceneLocIdx = Object.freeze({
    WELCOME: 0,
    PHASE: 1,
    PREMATCH:2,
    MATCH:3,
    END_GAME:4,
    END:5,
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
