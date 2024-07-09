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
    PHASE: "tournament.phase",
    MATCH: "tournament.match",
    RESULT: "tournament.result",
    BROKE: "tournament.broke",
})

export const EventLocal = Object.freeze({
    PLAYERS: "local.players",
    PHASE: "local.phase",
    MATCH: "local.match",
    UPDATE: EventGame.UPDATE,
    NEXT: "local.next",
    END_GAME: "local.end.game",
    END_TRN: "local.end.tournament",
    QUIT: "local.quit",
})

export const EventError = Object.freeze({
    TYPE: "error.type",
    DATA: "error.data",
})

export const sceneIdx = Object.freeze({
    WELCOME: 0,
    TYPE: 1,
    CREATION:2,
    READY:3,
    MATCH:4,
    END:5,
    BROKE:6,
})

export const sceneLocIdx = Object.freeze({
    WELCOME: 0,
    PHASE: 1,
    PREMATCH:2,
    MATCH:3,
    END:4,
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