import * as game from './game.js';
import { gameData } from './game.js';
import { updateSettings, changeGameStatus, getGameStatus, getSceneIdx, announcePhase, announceMatch, moveTo, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearInvitationList, clearScore } from './menu.js';
import { fullClear } from './index.js';
import { scene } from './game.js';
import * as enu from './enums.js'
import * as utils from './utils.js';
import { composer } from './game.js';
import { isUserAuthenticated } from '../index.js';
import { fetchUsers } from '../chat.js';
import { incrDecrNotifNumber } from '../chat.js';

function updateTimer() {
    gameData.elapsedTime += 1;
}

export let gameSocket = null;
export let gs_timeout = null;

let default_game_data = null;

function askNext() { gameSocket.send(JSON.stringify({ 'type': enu.Game.NEXT })) }

export const initGameWebSocket = async (path) => {
	console.log("initgws on:" + path);
    if (gameSocket !== null) {
        console.log("alreday open")
        return;
    };
	if (path === enu.backendPath.REMOTE) {
		if (await isUserAuthenticated() === false) return;
	}
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + path
    );
	gameSocket.onopen = function () {console.log("gws: open")};
	gameSocket.onerror = function () {console.log("gws: error")};
    gameSocket.onmessage = messageHandler;
    gameSocket.onclose = function (e) {
        moveTo((path === enu.backendPath.LOCAL) ? enu.sceneIdx.CREATION : enu.sceneIdx.WELCOME)
        gameSocket = null;
        clearListInvitation();
        if (path === enu.backendPath.REMOTE) gs_timeout = setTimeout(initGameWebSocket, 5000, path);
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
            if (getSceneIdx() === enu.sceneIdx.CREATION) {
                try {
                    const target = document.getElementById('invite-status-' + content.author);
                    target.parentElement.remove();
                }
                catch (error) {}
            }
            // if (getSceneIdx() === enu.sceneIdx.END || getSceneIdx() === enu.sceneIdx.END_TR || getSceneIdx() === enu.sceneIdx.CREATION) return true;
            // moveTo(enu.sceneIdx.WELCOME);
            return true;
        case enu.Game.START:
            
            return true;
        case enu.Game.BROKE:
        case enu.Game.KICK:
            if (getSceneIdx() === enu.sceneIdx.END || getSceneIdx() === enu.sceneIdx.END_TR) return true;
            moveTo(enu.sceneIdx.WELCOME);
            return true;
        case enu.Game.NEXT:
            moveTo(enu.sceneIdx.PREMATCH);
            return true;
        case enu.Game.READY:
            
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
    const inputField = document.getElementById('game-menu-input-player');
    const errorMessage = document.getElementById('input-error-message');

    inputField.value = '';
    errorMessage.style.display = 'none';

    switch (content.type) {
        case enu.Game.INVITE:
            updateListInvitedBy(content.mode, content.author);
            return true;
        case enu.Invitation.VALID:
            updateListInvitation(content.user);
            return true;
        case enu.Invitation.ERROR:
            warnErrorInvitation(content.error);
            inputField.classList.add('input-error');
            errorMessage.style.display = 'block';

            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 1500);

            setTimeout(() => {
                inputField.classList.remove('input-error');
            }, 500);

            return true;
        case enu.Invitation.ACCEPT:
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

                    document.getElementById(target).parentElement.remove();
                }
                changeGameStatus(enu.gameMode.MATCH);
                game.gameRenderer(content.message);
                moveTo(enu.sceneIdx.PREMATCH);
                announceMatch(content.players);
            } else if (getGameStatus() === enu.gameMode.TOURNAMENT) {
                updateStatusInvitation(content.author)
            } else if (content.mode === enu.Game.TRN) {
                moveTo(enu.sceneIdx.WAITING)
                changeGameStatus(enu.gameMode.TOURNAMENT);
            }
            return true;
        case enu.Invitation.REJECT:
            
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

let timeout_asknext = null;
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
            
            return true;
        case enu.Match.START:
            moveTo(enu.sceneIdx.MATCH);
            clearScore();
            announceScore();
            document.addEventListener('keydown', bindKeyPress)
            document.addEventListener('keyup', bindKeyRelease)
            
            gameData.start = false;
            game.gameRenderer(content.message);
            startMatch();
            return true;
        case enu.Match.UPDATE:
            game.gameRenderer(content.message);
            return true;
        case enu.Match.SCORE:
            updateScore(content);
            announceScore();
            return true;
        case enu.Match.END:
            gameData.start = false;
            moveTo(enu.sceneIdx.END)
            document.removeEventListener('keydown', bindKeyPress)
            document.removeEventListener('keyup', bindKeyRelease)
            announceWinner(content);
            if (getGameStatus() === enu.gameMode.LOCAL) {
				timeout_asknext = setTimeout(askNext, 3000);
				const   menuM6_button = document.getElementById('menu-m6-button');
				menuM6_button.style.display = "none";
			}
            return true;
    };
    return false;
}

const _tournament = (content) => {
    switch (content.type) {
        case enu.Tournament.PHASE:
            if (timeout_asknext !== null) {
                clearTimeout(timeout_asknext);
                timeout_asknext = null;
            }
            game.gameRenderer(default_game_data)
            moveTo(enu.sceneIdx.PHASE);
            if (content.new === true) announcePhase(content.phase);
            return true;
        case enu.Tournament.MATCH:
            if (getGameStatus() === enu.gameMode.LOCAL) {
                moveTo(enu.sceneIdx.PREMATCH);
                document.addEventListener('keydown', bindKeyPress)
                document.addEventListener('keyup', bindKeyRelease)
                game.gameRenderer(content.state);
            }
            announceMatch(content.match);
            return true;
        case enu.Tournament.END:
            announceWinner(content)
            moveTo(enu.sceneIdx.END_TR)
            return true;
        case enu.Tournament.RESULT:
            return true;
    };
    return false;
}


const messageHandler = (e) => {
    const content = JSON.parse(e.data);
    if (content.type !== enu.Match.UPDATE) console.log("recv: " + content.type);
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



const updateListInvitation = async (user) => {
    const item = document.createElement('li');
    const itemPicture = document.createElement('img');
    const itemName = document.createElement('div');
    const button = document.createElement('button');
    const itemStatus = document.createElement('span');
    const itemPic = await fetchUsers(user);
    item.className = 'list-tournoi-element';
    itemPicture.className = 'list-tournoi-user-pic';
    
    itemPicture.src = itemPic.profile_picture;
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
    item.appendChild(itemPicture);
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
    const notificationContainer = document.querySelector(".notification-container");

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
    acceptButton.textContent = 'Accept';
    acceptButton.className = 'accept-button';
    refuseButton.className = 'remove-button';

    const notifDiv = document.createElement('div');
    const notifText = document.createElement('p');
    const notifDelete = document.createElement('i');

    notifDiv.className = 'notif';
    notifText.textContent = user + " invited you to play";
    notifDelete.className = "fa-solid fa-xmark";

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

    notifDelete.addEventListener('click', (e) => {
        e.target.parentElement.remove();
        incrDecrNotifNumber("decrement", -1);
    });

    itemStatusContainer.appendChild(itemStatus);
    item.appendChild(itemStatusContainer);
    item.appendChild(itemName);
    item.appendChild(acceptButton);
    refuseButton.appendChild(svg);
    item.appendChild(refuseButton);

    notifDiv.appendChild(notifText);
    notifDiv.appendChild(notifDelete);
    notificationContainer.appendChild(notifDiv);
    incrDecrNotifNumber("increment", 1);

    document.getElementById('game-menu-invitationList').appendChild(item);

}

export const clearListInvitedBy = () => {
    const local = document.getElementById('game-menu-invitationList');
    while (local.firstChild) { local.removeChild(local.lastChild); }
}

const updateStatusInvitation = (user) => {

}

const warnErrorInvitation = (error) => {
    const errorMessage = document.getElementById('input-error-message');
    if (error === enu.Error.FBD_403) {
        console.warn("FORBIDDEN");
        errorMessage.textContent = 'Stop being a creep. You are blocked.';
    }
    else if (error === enu.Error.NTF_404) {
        console.warn("USER NOT FOUND");
        errorMessage.textContent = 'User not found';
    }
    else if (error === enu.Error.ABSENT) {
        console.warn("USER ABSENT");
        errorMessage.textContent = 'User not connected';
    }
    else if (error === enu.Invitation.REJECT) {
        console.warn("REJECTED");
    }
}


export const clearGame = () => {
    document.removeEventListener('keydown', bindKeyPress)
    document.removeEventListener('keyup', bindKeyRelease)
    document.querySelectorAll(".game-element").forEach(div => { div.style.display = "none"; });
    game.clearScene();
    composer.render();
    game.scene.children
        .filter(obj => obj.userData.isTrailSphere)
        .forEach(obj => game.scene.remove(obj));
}


