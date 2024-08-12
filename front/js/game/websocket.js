import * as game from './game.js';
import { gameData } from './game.js';
import { updateSettings, changeGameStatus, getGameStatus, announcePhase, announceMatch, moveTo, invitations, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearInvitationList } from './menu.js';
import { fullClear } from './index.js';
import * as enu from './enums.js'
import * as utils from './utils.js';
import { composer } from './game.js';

function updateTimer() {
    gameData.elapsedTime += 1;
}

export let gameSocket = null;

function askNext() { gameSocket.send(JSON.stringify({ 'type': enu.Game.NEXT })) }

export const initGameWebSocket = (path) => {
    _initWebsocket(path)
}

const _initWebsocket = (path) => {
    if (gameSocket !== null) return;
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + path
    );
    console.log("GWS connection open on : " + path)
    gameSocket.onmessage = messageHandler;
    gameSocket.onclose = function (e) {
        console.log('GameWebSocket connection closed');
        moveTo((path === enu.backendPath.LOCAL) ? enu.sceneIdx.CREATION : enu.sceneIdx.WELCOME)
        setTimeout(_initWebsocket, 5000, path)
        gameSocket = null;
        clearListInvitation();
    };
    document.removeEventListener('keydown', bindKeyPress)
    document.removeEventListener('keyup', bindKeyRelease)
}

/*
        // LOCAL
                case enu.EventLocal.PHASE:
                    moveTo(enu.sceneIdx.PHASE);
                    announcePhase(content.message);
                    break;
                case enu.EventLocal.MATCH:
                    moveTo(enu.sceneIdx.PREMATCH);
                    announceMatch(content.message);
                    document.addEventListener('keydown', bindKeyPress)
                    document.addEventListener('keyup', bindKeyRelease)
                    game.gameRenderer(content.state);
                    if (gameData.start) {
                        if (!gameData.timerInterval)
                            gameData.timerInterval = setInterval(updateTimer, 1000);
                    } else {
                        gameData.sceneHandler = 1;
                        game.gameRenderer(null);
                    }
                    break;
                case enu.EventLocal.END_GAME:
                    clearGame();
                    document.removeEventListener('keydown', bindKeyPress)
                    document.removeEventListener('keyup', bindKeyRelease)
                    announceWinner(content.message);
                    moveTo(enu.sceneIdx.END)
                    setTimeout(askNext, 3000);
                    break;
                case enu.EventLocal.END_TRN:
                    moveTo(enu.sceneIdx.END)
                    break;
                    

const _remote = (content) => {
//     switch (content.type) {
//         // match
//         case enu.Game.ACCEPTED:
//             // when accepted for a match
//             changeGameStatus(enu.gameMode.MATCH);
//             game.gameRenderer(content.message);
//             moveTo(enu.sceneIdx.PREMATCH);
//             announceMatch(content.players);
//             break;

//         case enu.Game.READY:
//             document.getElementById('game-menu-ready-circle').style.background = '#0eee28';
//             break;


//         case enu.Game.END:
//             fullClear();
//             moveTo(enu.sceneIdx.END);
            
//             break;
//         case enu.EventError.TYPE:
//             console.error(content.type)
//             break;




//         default:
//             console.log("unknow type : ", content.type)
//     }
// }

*/

const startMatch = () => {
    if (gameData.start) {
        if (!gameData.timerInterval)
            gameData.timerInterval = setInterval(updateTimer, 1000);
    } else {
        gameData.sceneHandler = 1;
        game.gameRenderer(null);
    };
}

const _game = (content) => {
    switch (content.type) {
        case enu.Game.QUIT:
            // ?
            return true;
        case enu.Game.BROKE:
        case enu.Game.KICK:
            clearGame()
            moveTo(enu.sceneIdx.WELCOME);
            // warn kicked
            // clear 
            return true;
        case enu.Game.READY:
            // set users status to ready
            return true;
        case enu.Game.DEFAULT:
        case enu.Game.SETTING:
            updateSettings(content.message);
            return true;
    }
    return false;
}

const _invitations = (content) => {
    switch (content.type) {
        case enu.Game.INVITE:
            updateListInvitedBy(content.mode, content.author);
            return true;
        case enu.Invitation.VALID:
            updateListInvitation(content.user);
            return true;
        case enu.Invitation.ERROR:
            warnErrorInvitation(content.error);
            return true;
        case enu.Invitation.ACCEPT:
            console.log(content)
            if (content.mode === enu.Game.MATCH) {
                console.log("match")
                changeGameStatus(enu.gameMode.MATCH);
                moveTo(enu.sceneIdx.PREMATCH);
                announceMatch(content.players);
                // game.gameRenderer(content.message);
            } else if (getGameStatus() === enu.gameMode.TOURNAMENT) {
                updateStatusInvitation(content.author)
            } else {
                moveTo(enu.sceneIdx.WAITING)
                changeGameStatus(enu.gameMode.TOURNAMENT);
            }
            return true;
        case enu.Invitation.REJECT:
            warnErrorInvitation(enu.Invitation.REJECT)
            let target = 'invite-status' + content.author;
            document.getElementById(target).parentElement.remove();
            return true;
    };
    return false;
}

const _match = (content) => {
    switch (content.type) {
        case enu.Match.PAUSE:
            if (gameData.timerInterval) {
                clearInterval(gameData.timerInterval);
                gameData.timerInterval = null;
            };
        case enu.Match.RESUME:
            togglePause();
            toggleLock();
            return true;
        case enu.Match.RESULT:
            // contain result for a match (used in trn)
            return true;
        case enu.Match.START:
            moveTo(enu.sceneIdx.MATCH);
            announceScore();
            document.addEventListener('keydown', bindKeyPress)
            document.addEventListener('keyup', bindKeyRelease)
            startMatch();
            return true;
        case enu.Match.UPDATE:
            game.gameRenderer(content.message);
            return true;
        case enu.Match.SCORE:
            console.log(content)
            updateScore(content.message);
            announceScore();
            return true;
        case enu.Match.END:
            moveTo(enu.sceneIdx.END)
            document.removeEventListener('keydown', bindKeyPress)
            document.removeEventListener('keyup', bindKeyRelease)
            announceWinner(content.message);
            if (getGameStatus() === enu.gameMode.LOCAL) setTimeout(askNext, 3000);
            else if (getGameStatus() === enu.gameMode.TOURNAMENT) setTimeout(moveTo, 3000, enu.sceneIdx.END);
            return true;
    };
    return false;
}

const _tournament = (content) => {
    switch (content.type) {
        case enu.Tournament.PHASE:
            moveTo(enu.sceneIdx.PHASE);
            announcePhase(content.message);
            return true;
        case enu.Tournament.MATCH:
            // if local -> go to prematck, if rem wait user to go to prematch
            //  changeGameStatus(enu.gameMode.MATCH);
            if (getGameStatus() === enu.gameMode.LOCAL) {
                moveTo(enu.sceneIdx.PREMATCH);
                announceMatch(content.message);
                document.addEventListener('keydown', bindKeyPress)
                document.addEventListener('keyup', bindKeyRelease)
                game.gameRenderer(content.state);
                startMatch()
            };
            return true;
        case enu.Tournament.END:
            moveTo(enu.sceneIdx.END_TR)
            return true;
        case enu.Tournament.RESULT:
            // not used now
            return true;
    };
    return false;
}


const messageHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    if (_match(content) === false)
        if (_invitations(content) === false)
            if (_game(content) === false)
                if (_tournament(content) === false)
                    console.error("unknow type");
};

const bindKeyPress = (event) => {
    let data = { 'type': enu.Match.UPDATE, 'message': '' };
    switch (event.key) {
        case 'w':
            data.message = 'wPressed'
            break;
        case 's':
            data.message = 'sPressed'
            break;
        case 'ArrowUp':
            data.message = 'upPressed'
            break;
        case 'ArrowDown':
            data.message = 'downPressed'
            break;
        default:
            return;
    }
    gameSocket.send(JSON.stringify(data));
}

const bindKeyRelease = (event) => {
    let data = { 'type': enu.Match.UPDATE, 'message': '' };
    switch (event.key) {
        case 'w':
            data.message = 'wRelease'
            break;
        case 's':
            data.message = 'sRelease'
            break;
        case 'ArrowUp':
            data.message = 'upRelease'
            break;
        case 'ArrowDown':
            data.message = 'downRelease'
            break;
        default:
            return;
    }
    gameSocket.send(JSON.stringify(data));
}


// invitations 
const updateListInvitation = (user) => {
    const item = document.createElement('li');
    const itemPicture = document.createElement('img');
    const itemName = document.createElement('div');
    const button = document.createElement('button');
    const itemStatus = document.createElement('span');

    item.className = 'list-tournoi-element';
    itemPicture.className = 'list-tournoi-user-pic';
    itemPicture.src = '../../img/anon.jpg'; // a remplacer !!!! (par la vrai foto)
    itemName.textContent = user;
    itemName.className = 'list-tournoi-user-name';
    itemStatus.id = 'invite-status' + user;
    itemStatus.className = 'remote-list-element';
    // itemStatus.textContent = '...waiting...';

    button.className = 'remove-button';
    button.addEventListener('click', (e) => {
        const pos = players.indexOf(user);
        players.splice(pos, 1);
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': enu.Game.KICK,
            'message': user
        }));
    });

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 448 512');
    svg.setAttribute('class', 'svgIcon');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z');
    path.setAttribute('fill', 'white');

    svg.appendChild(path);
    item.appendChild(itemPicture);// Initial shooting star
    item.appendChild(itemName);
    item.appendChild(itemStatus);

    item.innerHTML += `
        <div class="typing-indicator">
            <div class="typing-circle"></div>
            <div class="typing-circle"></div>
            <div class="typing-circle"></div>
            <div class="typing-shadow"></div>
            <div class="typing-shadow"></div>
            <div class="typing-shadow"></div>
        </div>
    `;

    button.appendChild(svg);
    item.appendChild(button);

    document.getElementById('game-menu-list').appendChild(item);
}

export const clearListInvitation = () => {
    const local = document.getElementById('game-menu-list');
    while (local.firstChild) { local.removeChild(local.lastChild); }
}

function updateListInvitedBy(mode, user) {
    if (mode === enu.Game.MATCH) {
        var typeGame = "invitationTypeMatch";
        var containerClass = "invitationTypeContainerMatch";
        var typeClass = "bi bi-controller";
    } else {
        var typeGame = "invitationTypeTournament";
        var containerClass = "invitationTypeContainerTournament";
        var typeClass = "bi bi-people";
    }

    const item = document.createElement('li');
    const itemName = document.createElement('span');
    const itemStatus = document.createElement('i');
    const itemStatusContainer = document.createElement('div');
    const acceptButton = document.createElement('button');
    const refuseButton = document.createElement('button');

    item.className = 'list-tournoi-element';
    item.id = "invited-by-" + user;
    itemStatusContainer.className = "invitationTypeContainer " + containerClass + " " + typeGame;
    itemStatus.className = typeClass;
    itemName.textContent = user;
    acceptButton.textContent = 'Accepter';
    acceptButton.className = 'accept-button';
    refuseButton.className = 'remove-button';

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 448 512');
    svg.setAttribute('class', 'svgIcon');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z');
    path.setAttribute('fill', 'white');

    svg.appendChild(path);

    acceptButton.addEventListener('click', (e) => {
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': enu.Invitation.ACCEPT,
            'message': user
        }));
    });

    refuseButton.addEventListener('click', (e) => {
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': enu.Invitation.REJECT,
            'message': user
        }));

    });
    itemStatusContainer.appendChild(itemStatus);
    item.appendChild(itemStatusContainer);
    item.appendChild(itemName);
    item.appendChild(acceptButton);
    refuseButton.appendChild(svg);
    item.appendChild(refuseButton);

    document.getElementById('game-menu-invitationList').appendChild(item);

}

export const clearListInvitedBy = () => {
    const local = document.getElementById('game-menu-invitationList');
    while (local.firstChild) { local.removeChild(local.lastChild); }
}

const updateStatusInvitation = (user) => {

}

const warnErrorInvitation = (error) => {
    if (error === enu.Error.FBD_403) console.warn("FORBIDDEN")
    else if (error === enu.Error.NTF_404) console.warn("USER NOT FOUND")
    else if (error === enu.Error.ABSENT) console.warn("USER ABSENT")
        else if (error === enu.Invitation.REJECT) console.warn("REJECTED")
}


export const clearGame = () => {
    document.removeEventListener('keydown', bindKeyPress)
    document.removeEventListener('keyup', bindKeyRelease)
    document.querySelectorAll(".game-element").forEach(div => { div.style.display = "none"; });
    utils.clearScene();
    composer.render();
    game.scene.children
        .filter(obj => obj.userData.isTrailSphere)
        .forEach(obj => game.scene.remove(obj));
}


// bouton game
/*

// document.querySelector('#startButton').onclick = function(e) {
    if (gameData.start)
    {
        gameSocket.send(JSON.stringify({
            'type': 'game.update',
            'message': 'startButton'
        }));
        if (!gameData.timerInterval)
            gameData.timerInterval = setInterval(updateTimer, 1000);
    }
    else {
        gameData.sceneHandler = 1;
        game.gameRenderer(null);
    }
// };

document.querySelector('#stopButton').onclick = function(e) {
    gameSocket.send(JSON.stringify({
        'type': 'game.update',
        'message': 'stopButton'
    }));
	
    if (gameData.timerInterval) {
        clearInterval(gameData.timerInterval);
        gameData.timerInterval = null;
    }
};
*/
