import * as game from './game.js';
import { gameData } from './game.js';
import { changeStatus, announcePhase, announceMatch, moveTo, invitations, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearInvitationList } from './menu.js';
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
        case enu.EventGame.INVITE:
            console.log("invitation from: ", content.author);
            updateInvitationList(enu.EventGame.INVITE, content.author);
            break;
        case enu.EventGame.JOIN:
            // not used
            document.getElementById(content.author).innerHTML = 'accepted!';
            break;
        case enu.EventGame.ACCEPTED:
            // when accepted for a match
            game.gameRenderer(content.message);
            moveTo(enu.sceneIdx.PREMATCH);
            announceMatch(content.players);
            break;
        case enu.EventGame.KICK:
            document.getElementById('game-menu-ready-circle').style.background = '#0eee28';
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
            // try to join a match but refused
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


export const clearInvList = () => {
    const local = document.getElementById('game-menu-invitationList');
    while (local.firstChild) {local.removeChild(local.lastChild);}
}

function updateInvitationList(type, user) {
    if (type === enu.EventGame.INVITE) {
        var joinType = enu.EventGame.JOIN;
        var denyType = enu.EventGame.DENY;
        var typeGame = "match";
    } else {
        var joinType = enu.EventTournament.JOIN;
        var denyType = enu.EventTournament.DENY;
        var typeGame = "tournoi";
    }

    const   item = document.createElement('li');
    const   itemName = document.createElement('span');
    const   itemStatus = document.createElement('span');
    const   acceptButton = document.createElement('button');
    const   refuseButton = document.createElement('button');

    item.className = 'list-tournoi-element';
    item.id = "invited-by-" + user;
    itemStatus.textContent = typeGame;
    itemName.textContent = user;
    acceptButton.textContent = 'Accepter';
    acceptButton.className = 'accept-button';
    refuseButton.textContent = 'Refuse';
    refuseButton.className = 'remove-button';

    acceptButton.addEventListener('click', () => {
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

    item.appendChild(itemStatus);
    item.appendChild(itemName);
    item.appendChild(acceptButton);
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
