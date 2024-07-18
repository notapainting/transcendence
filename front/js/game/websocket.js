import * as game from './game.js';
import { gameData } from './game.js';
import { announcePhase, announceMatch, moveTo, invitations, toggleLock, togglePause, announceWinner, updateScore, announceScore, clearSentList } from './menu.js';
import { fullClear } from './index.js';
import * as enu from './enums.js'
import * as utils from './utils.js';
import { composer } from './game.js';

function updateTimer() {
	gameData.elapsedTime += 1;
}

export let gameSocket = null;
export let localGameSocket = null;

async function sleep (ms) { new Promise(r => setTimeout(r, ms));}

function askNext() {gameSocket.send(JSON.stringify({'type': enu.EventLocal.NEXT}))}

const localHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    switch (content.type) {
        case enu.EventLocal.PHASE:
            moveTo(enu.sceneLocIdx.PHASE);
            announcePhase(content.message);
            break;
        case enu.EventLocal.MATCH:
            moveTo(enu.sceneLocIdx.PREMATCH);
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
            moveTo(enu.sceneLocIdx.END_GAME)
            setTimeout(askNext, 3000);
            break;
        case enu.EventLocal.END_TRN:
            moveTo(enu.sceneLocIdx.END)
            break;
        default:
            console.log("unknow type");
            break;
    }
}


/*
enu.Local.PLAYERS
enu.Local.UPDATE
enu.Local.NEXT
enu.Local.QUIT
*/

export const initLocalGameWebSocket = () => {
    if (localGameSocket !== null) return ; 
    localGameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + enu.backendPath.LOCAL
    );
    localGameSocket.onmessage = localHandler;
    localGameSocket.onclose = function(e) {
        console.log('GameWebSocket connection closed');
        setTimeout(initLocalGameWebSocket, 5000)
        localGameSocket = null;
    };
}

export const initGameWebSocket = () => {
    if (gameSocket !== null) return ; 
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + enu.backendPath.REMOTE
    );
    gameSocket.onmessage = remoteHandler;
    gameSocket.onclose = function(e) {
        console.log('GameWebSocket connection closed');
        setTimeout(initGameWebSocket, 5000)
        gameSocket = null;
    };
}

const remoteHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    switch(content.type) {
// LOCAL
        case enu.EventLocal.PHASE:
            moveTo(enu.sceneLocIdx.PHASE);
            announcePhase(content.message);
            break;
        case enu.EventLocal.MATCH:
            moveTo(enu.sceneLocIdx.PREMATCH);
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
            moveTo(enu.sceneLocIdx.END_GAME)
            setTimeout(askNext, 3000);
            break;
        case enu.EventLocal.END_TRN:
            moveTo(enu.sceneLocIdx.END)
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
            clearSentList();
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
            break;

        case enu.EventTournament.ACCEPTED:
            // received whe naccepted in trn
            break;
        case enu.EventTournament.READY:
            // players is ready 
            break;
        case enu.EventTournament.PHASE:
            // planning of match for that phase
            break;
        case enu.EventTournament.MATCH:
            // match you have to play
            break;
        case enu.EventTournament.RESULT:
            // result of a match
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
        var typeGame = "match";
    } else {
        var joinType = enu.EventTournament.JOIN;
        var typeGame = "tournoi";
    }

    const listItem = document.createElement('li');
    listItem.className = 'remote-list-element';

    const   listItemName = document.createElement('span');
    listItemName.textContent = `(${typeGame}) ${user}`;
    
    const acceptButton = document.createElement('button');
    acceptButton.textContent = 'Accepter';
    acceptButton.className = 'accept-button';

    acceptButton.addEventListener('click', function() {
        acceptButton.disabled = true;
        gameSocket.send(JSON.stringify({
            'type': joinType,
            'message': user
        }));
    });

    listItem.appendChild(listItemName);
    listItem.appendChild(acceptButton);

    document.getElementById('game-menu-invitationList').appendChild(listItem);

}

function updateInvitationList2() {
    const invitationList = document.getElementById('game-menu-invitationList');
    invitationList.innerHTML = '';

    invitations.forEach((invitation, index) => {
        const listItem = document.createElement('li');
        const invitationText = document.createElement('span');
        invitationText.textContent = `${index + 1}. ${invitation}`;

        const acceptButton = document.createElement('button');
        acceptButton.textContent = 'Accepter';
        acceptButton.className = 'accept-button';

        acceptButton.addEventListener('click', function() {
            invitationText.textContent = `${index + 1}. ${invitation} - Ok`;
            acceptButton.disabled = true;
            gameSocket.send(JSON.stringify({
                'type': 'game.join',
                'message': invitation
            }));
        });

        listItem.appendChild(invitationText);
        listItem.appendChild(acceptButton);
        invitationList.appendChild(listItem);
    });
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


    // const currentTime = performance.now();
    // const pingDelay = currentTime - lastPingTime;
    // console.log("Ping delay:", pingDelay, "ms");

    // if (message.winner == 'leftWin')
    // 	playerWin('left')
    // else if (message.winner == 'rightWin')
    // 	playerWin('right')

    // lastPingTime = currentTime;
    // console.log("ping = ", lastPingTime);



/*

document.addEventListener('keydown', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
			'type': 'game.update',
            'message': 'wPressed'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'sPressed'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'upPressed'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'downPressed'
		}));
	}
});


document.addEventListener('keyup', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
			'type': 'game.update',
            'message': 'wRelease'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'sRelease'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'upRelease'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'type': 'game.update',
			'message': 'downRelease'
		}));
	}
});



// let lastPingTime = performance.now();

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


/*
	fastGame.style.display = 'none';
	tournament.style.display = 'none';
	exit.style.display = 'none';

	create.style.display = 'block';
	join.style.display = 'block';
});

tournament.addEventListener('click', () => {
	fastGame.style.display = 'none';
	tournament.style.display = 'none';
	exit.style.display = 'none';

	create.style.display = 'block';
	join.style.display = 'block';
});

*/