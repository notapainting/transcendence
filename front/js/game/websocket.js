import * as game from './game.js';
import { gameData } from './game.js';
import { updateSettings, changeStatus, announcePhase, announceMatch, moveTo, invitations, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearInvitationList } from './menu.js';
import { fullClear } from './index.js';
import * as enu from './enums.js'
import * as utils from './utils.js';
import { composer } from './game.js';

function updateTimer() {
	gameData.elapsedTime += 1;
}

export let gameSocket = null;



export const initGameWebSocket = (path) => {
    _initWebsocket(path, (path === enu.backendPath.LOCAL) ? localHandler : remoteHandler)
}

const _initWebsocket = (path, handler) => {
    if (gameSocket !== null) return ; 
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + path
    );
    console.log("GWS connection open on : " + path)
    gameSocket.onmessage = handler;
    gameSocket.onclose = function(e) {
        console.log('GameWebSocket connection closed');
        setTimeout(_initWebsocket, 5000, path, handler)
        gameSocket = null;
    };
}

const localHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    switch (content.type) {
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
        case enu.EventLocal.UPDATE:
            game.gameRenderer(content.message);
            break;
        case enu.EventLocal.SCORE:
            updateScore(content.message);
            announceScore();
            break;
        case enu.EventLocal.END_GAME:
            clearGame();
            document.removeEventListener('keydown', bindKeyPress)
            document.removeEventListener('keyup', bindKeyRelease)
            announceWinner(content.message);
            moveTo(enu.sceneIdx.END_GAME)
            setTimeout(askNext, 3000);
            break;
        case enu.EventLocal.END_TRN:
            moveTo(enu.sceneIdx.END)
            break;
        default:
            console.log("unknow type");
            break;
    }
}


const remoteHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    switch(content.type) {
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
            moveTo(enu.sceneIdx.END_GAME)
            setTimeout(askNext, 3000);
            break;
        case enu.EventLocal.END_TRN:
            moveTo(enu.sceneIdx.END)
            break;
            
            
// match
        case enu.EventGame.INV_FOR:
            console.warn("USER BLOCKED: " + content.message)
            break;
        case enu.EventGame.INV_ABS:
            console.warn("USER NOT CONNECTED: " + content.message)
            break;
        case enu.EventGame.INV_404:
            console.warn("USER NOT FOUND/CONNECTED: " + content.message)
            break;
        case enu.EventGame.INV_ACC:
            createListRemote(content.message, enu.EventGame.KICK);
            break;
        case enu.EventGame.INVITE:
            console.log("invitation from: ", content.author);
            updateInvitationList(enu.EventGame.INVITE, content.author);
            break;
        case enu.EventGame.JOIN:
            // not used
            document.getElementById('invite-status' + content.author).innerHTML = 'accepted!';
            break;
        case enu.EventGame.SETTINGS_DEF:
            console.log("DEFAULTS SETTINGS : " + content.message);
            updateSettings(content.message);
            break;
        case enu.EventGame.SETTINGS:
            console.log("SETTINGS : " + content.message);
            break;
        case enu.EventGame.ACCEPTED:
            // when accepted for a match
            changeStatus(enu.gameMode.MATCH);
            game.gameRenderer(content.message);
            moveTo(enu.sceneIdx.PREMATCH);
            announceMatch(content.players);
            break;
        case enu.EventGame.KICK:
            moveTo(enu.sceneIdx.WELCOME);
            console.error("KICKED")
            break;
        case enu.EventGame.READY:
            document.getElementById('game-menu-ready-circle').style.background = '#0eee28';
            break;
        case enu.EventGame.START:
            moveTo(enu.sceneIdx.MATCH);
            document.addEventListener('keydown', bindKeyPress)
            document.addEventListener('keyup', bindKeyRelease)
            announceScore();
            if (gameData.start) {
                if (!gameData.timerInterval)
                    gameData.timerInterval = setInterval(updateTimer, 1000);
            } else {
                gameData.sceneHandler = 1;
                game.gameRenderer(null);
            }
            break;
        case enu.EventGame.UPDATE:
            game.gameRenderer(content.message);
            break;
        case enu.EventGame.SCORE:
            updateScore(content.message);
            announceScore();
            break;
        case enu.EventGame.PAUSE:
            togglePause();
            toggleLock();
            if (gameData.timerInterval) {
                clearInterval(gameData.timerInterval);
                gameData.timerInterval = null;
            }
            break;
        case enu.EventGame.RESUME:
            togglePause();
            toggleLock();
            break;
        case enu.EventGame.BROKE:
            // connection lost
        case enu.EventGame.DENY:
            // try to invite someone but get rejected
            if (content.message === 'invitation' ) {
                let target = 'invite-status' + content.author;
                document.getElementById(target).innerHTML = 'REFUSED!';
                setTimeout(() => {document.getElementById(target).parentElement.remove();}, 5000)
            }
            // try to join a match but refused
            break ;
        case enu.EventGame.QUIT:
            // a player has quit match
        case enu.EventGame.END:
            fullClear();
            moveTo(enu.sceneIdx.END);
            if (content.tournament) changeStatus(enu.gameMode.TOURNAMENT);
            break;
        case enu.EventError.TYPE:
            console.error(content.type)
            break;

// tournament
        case enu.EventTournament.SETTINGS:
            console.log("SETTINGS : " + content.message);
            break ;
        case enu.EventTournament.INVITE:
            console.log("invitation from: ", content.author);
            updateInvitationList(enu.EventTournament.INVITE, content.author);
            break;

        case enu.EventTournament.JOIN:
            // receive new player sjoining trn
            // do : update inviter list etc in WAITING
            break;

        case enu.EventTournament.ACCEPTED:
            // received whe naccepted in trn
            moveTo(enu.sceneIdx.WAITING)
            changeStatus(enu.gameMode.TOURNAMENT);
            break;
        case enu.EventTournament.READY:
            // players is ready 
            break;
        case enu.EventTournament.PHASE:
            moveTo(enu.sceneIdx.PHASE)
            announcePhase(content.message);
            // planning of match for that phase
            break;
        case enu.EventTournament.MATCH:
            // match you have to play
            changeStatus(enu.gameMode.MATCH);
            break;
        case enu.EventTournament.RESULT:
            // result of a match
            // update match tree in PHASE
            break;
        case enu.EventTournament.QUIT:
        case enu.EventTournament.DENY:
        case enu.EventTournament.KICK:
        case enu.EventTournament.BROKE:
        case enu.EventTournament.END:
            break;
        default:
            console.log("unknow type : ", content.type)
    }
};

const createListRemote = (user, kick) => {
    const   item = document.createElement('li');
    const   itemPicture = document.createElement('img');
    const   itemName = document.createElement('div');
    const   button = document.createElement('button');
    const   itemStatus = document.createElement('span');

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
            'type': kick,
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

export const clearInvList = () => {
    const local = document.getElementById('game-menu-invitationList');
    while (local.firstChild) {local.removeChild(local.lastChild);}
}

function updateInvitationList(type, user) {
    if (type === enu.EventGame.INVITE) {
        var joinType = enu.EventGame.JOIN;
        var denyType = enu.EventGame.DENY;
        var typeGame = "invitationTypeMatch";
        var containerClass = "invitationTypeContainerMatch";
        var typeClass = "bi bi-controller";
    } else {
        var joinType = enu.EventTournament.JOIN;
        var denyType = enu.EventTournament.DENY;
        var typeGame = "invitationTypeTournament";
        var containerClass = "invitationTypeContainerTournament";
        var typeClass = "bi bi-people";
    }

    const   item = document.createElement('li');
    const   itemName = document.createElement('span');
    const   itemStatus = document.createElement('i');
    const   itemStatusContainer = document.createElement('div');
    const   acceptButton = document.createElement('button');
    const   refuseButton = document.createElement('button');

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
            'type': joinType,
            'message': user
        }));
    });

    refuseButton.addEventListener('click', (e) => {
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': denyType,
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


const bindKeyPress = (event) => {
    let data = {'type': 'game.update','message': ''};
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
            return ;
    }
    gameSocket.send(JSON.stringify(data));
}

const bindKeyRelease = (event) => {
    let data = {'type': 'game.update','message': ''};
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
            return ;
    }
    gameSocket.send(JSON.stringify(data));
}

export const clearGame = () => {
    document.removeEventListener('keydown', bindKeyPress)
    document.removeEventListener('keyup', bindKeyRelease)
    document.querySelectorAll(".game-element").forEach(div => {div.style.display = "none";});
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
