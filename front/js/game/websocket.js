import * as game from './game.js';
import { gameData } from './game.js';
import { moveTo, invitations, toggleLock, togglePause } from './menu.js';
import { fullClear } from './index.js';
import * as enu from './enums.js'



function updateTimer() {
	gameData.elapsedTime += 1;
}

export let gameSocket = null;

const messageHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    updateInvitationList();
    switch(content.type){
        case enu.EventGame.INVITE:
            console.log("invitation from: ", content.author);
            invitations.push(content.author);
            updateInvitationList();
            break;
        case enu.EventGame.JOIN:
            game.gameRenderer(content.message);
            break;
        case enu.EventGame.ACCEPTED:
            document.addEventListener('keydown', bindKeyPress)
            document.addEventListener('keyup', bindKeyRelease)
            game.gameRenderer(content.message);
            moveTo(enu.sceneIdx.READY);
            break;
        case enu.EventGame.READY:
            document.getElementById('game-menu-ready-circle').style.background = '#0eee28';
            break;
        case enu.EventGame.START:
            moveTo(enu.sceneIdx.MATCH);
            if (gameData.start)
                {
                    if (!gameData.timerInterval)
                        gameData.timerInterval = setInterval(updateTimer, 1000);
                }
                else {
                    gameData.sceneHandler = 1;
                    game.gameRenderer(null);
                }
            break;
        case enu.EventGame.UPDATE:
            game.gameRenderer(content.message);
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
            moveTo(enu.sceneIdx.END);
            break;
        case enu.EventGame.END:
            moveTo(enu.sceneIdx.END);
            break;
        case enu.EventGame.QUIT:
            moveTo(enu.sceneIdx.END);
            break;
        case enu.EventError.TYPE:
            console.error(content.type)
            break;
        default:
            console.log("unknow type : ", content.type)
    }


};

export const initWebSocket = (path) => {
    if (gameSocket !== null) return ; 
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + path
    );
    gameSocket.onmessage = messageHandler;
    gameSocket.onclose = function(e) {
        fullClear();
        console.log('Game socket closed');
        gameSocket = null;
    };
}


function updateInvitationList() {
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
    
    // const canvas = document.getElementById('game-canvas')
    // const context = canvas.getContext('2d');
    // context.clearRect(0, 0, canvas.width, canvas.height);
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