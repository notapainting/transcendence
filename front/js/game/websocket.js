import * as game from './game.js';
import { gameData } from './game.js';
import { updateSettings, changeGameStatus, getGameStatus, getSceneIdx, announcePhase, announceMatch, moveTo, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearInvitationList, clearScore } from './menu.js';
import { fullClear } from './index.js';
import { scene } from './game.js';
import * as enu from './enums.js'
import * as utils from './utils.js';
import { composer } from './game.js';

function updateTimer() {
    gameData.elapsedTime += 1;
}

export let gameSocket = null;

let default_game_data = null;

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
        if (path === enu.backendPath.REMOTE) setTimeout(_initWebsocket, 5000, path);
        gameSocket = null;
        clearListInvitation();
    };
    document.removeEventListener('keydown', bindKeyPress)
    document.removeEventListener('keyup', bindKeyRelease)
}


export const startMatch = () => {
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
            // if (getSceneIdx() === enu.sceneIdx.PREMATCH) moveTo(enu.WELCOME);
            return true;
        case enu.Game.START:
            // ?
            return true;
        case enu.Game.BROKE:
        case enu.Game.KICK:
            if (getSceneIdx() === enu.sceneIdx.END || getSceneIdx() === enu.sceneIdx.END_TR) return;
            moveTo(enu.sceneIdx.WELCOME);
            // warn kicked
            return true;
        case enu.Game.NEXT:
            moveTo(enu.sceneIdx.PREMATCH);
            return true;
        case enu.Game.READY:
            // set users status to ready
            return true;
        case enu.Game.DEFAULT:
            default_game_data = content.state
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
            console.log(content);
            const message = content.message;  
            const listItems = document.querySelectorAll('.list-tournoi-element');
        
            listItems.forEach(li => {
                const userNameDiv = li.querySelector('.list-tournoi-user-name');
                
                if (userNameDiv && userNameDiv.textContent.trim() === message) {
                    const typingIndicator = li.querySelector('.typing-indicator');
                    if (typingIndicator) {
                        typingIndicator.innerHTML = '';
                        typingIndicator.innerHTML = '<div class="check-mark-accept-game"></div>';
                    }
                }
            });
            if (content.mode === enu.Game.MATCH) {
                if (content.by === false) {
                    let target = 'invite-status-' + content.message;
                    console.log(target)
                    document.getElementById(target).parentElement.remove();
                } 
                changeGameStatus(enu.gameMode.MATCH);
                moveTo(enu.sceneIdx.PREMATCH);
                announceMatch(content.players);
            } else if (getGameStatus() === enu.gameMode.TOURNAMENT) {
                updateStatusInvitation(content.author)
                console.log("bad: " + getGameStatus())
            } else if (content.mode === enu.Game.TRN){
                console.log("good")
                moveTo(enu.sceneIdx.WAITING)
                changeGameStatus(enu.gameMode.TOURNAMENT);
            }
            return true;
        case enu.Invitation.REJECT:
            warnErrorInvitation(enu.Invitation.REJECT)
            if (content.by === false) {
                let target = 'invite-status-' + content.author;
                document.getElementById(target).parentElement.remove();
            } else {
                var target = 'invited-by-' + content.author;
                document.getElementById(target).remove();
            }
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
            togglePause(true);
            return true;
        case enu.Match.RESUME:
            togglePause(false);
            return true;
        case enu.Match.RESULT:
            // contain result for a match (used in trn)
            return true;
        case enu.Match.START:
            moveTo(enu.sceneIdx.MATCH);
            clearScore();
            announceScore();
            document.addEventListener('keydown', bindKeyPress)
            document.addEventListener('keyup', bindKeyRelease)
            game.gameRenderer(content.message);
            startMatch();
            return true;
        case enu.Match.UPDATE:
            game.gameRenderer(content.message);
            return true;
        case enu.Match.SCORE:
            console.log(content)
            updateScore(content);
            announceScore();
            return true;
        case enu.Match.END:
            console.log(content)
            moveTo(enu.sceneIdx.END)
            document.removeEventListener('keydown', bindKeyPress)
            document.removeEventListener('keyup', bindKeyRelease)
            announceWinner(content);
            if (getGameStatus() === enu.gameMode.LOCAL) setTimeout(askNext, 3000);
            return true;
    };
    return false;
}

const _tournament = (content) => {
    switch (content.type) {
        case enu.Tournament.PHASE:
            console.log(content);
            game.gameRenderer(default_game_data)
            moveTo(enu.sceneIdx.PHASE);
            if (content.new === true) announcePhase(content.phase);
            return true;
        case enu.Tournament.MATCH:
            console.log(content)
            if (getGameStatus() === enu.gameMode.LOCAL) {
                moveTo(enu.sceneIdx.PREMATCH);
                document.addEventListener('keydown', bindKeyPress)
                document.addEventListener('keyup', bindKeyRelease)
                game.gameRenderer(content.state);
            }
            announceMatch(content.match);
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
    console.log("message type: ", content.type);
    console.log("message: ", content);
    if (_match(content) === false)
        if (_invitations(content) === false)
            if (_game(content) === false)
                if (_tournament(content) === false)
                    console.error("unknow type: " + content.type);
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
    itemStatus.id = 'invite-status-' + user;
    itemStatus.className = 'remote-list-element';

    button.className = 'remove-button';
    button.addEventListener('click', (e) => {
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
    };

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
            'message': user,
            'mode': mode,
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
