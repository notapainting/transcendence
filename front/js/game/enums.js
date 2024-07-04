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

export const sceneIdx = Object.freeze({
    WELCOME: 0,
    TYPE: 1,
    CREATION:2,
    READY:3,
    MATCH:4,
    END:5,
    BROKE:6,
})

export const gameMode = Object.freeze({
    MATCH: 0,
    TOURNAMENT: 1
})
