import * as game from './game.js';
import { gameData } from './game.js';

const fastGame = document.getElementById('fastGame');
const tournament = document.getElementById('tournament');
const exit = document.getElementById('exit');
const create = document.getElementById('create');
const join = document.getElementById('join');
const userInput = document.getElementById('userInput');
const inviteButton = document.getElementById('inviteButton');
const invitationBox = document.getElementById('invitationBox');

const invitations = [];

function updateTimer() {
	gameData.elapsedTime += 1;
}

export const gameSocket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/ws-game/'
);

let lastPingTime = performance.now();

function updateInvitationList() {
    const invitationList = document.getElementById('invitationList');
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

gameSocket.onmessage = function(e) {
    const message = JSON.parse(e.data);
	var messageType = message.type;
	updateInvitationList();
	if (messageType === 'game.invite'){
		const joinData = message.message;
		updateInvitationList();
		invitations.push(joinData);
	}
	else {
		game.gameRenderer(message);
	}

    
    const currentTime = performance.now();
    const pingDelay = currentTime - lastPingTime;
    // console.log("Ping delay:", pingDelay, "ms");

	if (message.winner == 'leftWin')
		playerWin('left')
	else if (message.winner == 'rightWin')
		playerWin('right')

    lastPingTime = currentTime;
	// console.log("ping = ", lastPingTime);
};


gameSocket.onclose = function(e) {
	console.error('Game socket closed unexpectedly');
};

document.querySelector('#startButton').onclick = function(e) {
	if (gameData.start)
    {
		gameSocket.send(JSON.stringify({
			'message': 'startButton'
        }));
		if (!gameData.timerInterval)
			gameData.timerInterval = setInterval(updateTimer, 1000);
    }
	else {
		gameData.sceneHandler = 1;
		game.gameRenderer(null);
	}
};

document.querySelector('#stopButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'stopButton'
	}));
	
	if (gameData.timerInterval) {
		clearInterval(gameData.timerInterval);
		gameData.timerInterval = null;
	}
};

document.addEventListener('keydown', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
            'message': 'wPressed'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'message': 'sPressed'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'message': 'upPressed'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'message': 'downPressed'
		}));
	}
});


document.addEventListener('keyup', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
            'message': 'wRelease'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'message': 'sRelease'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'message': 'upRelease'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'message': 'downRelease'
		}));
	}
});

fastGame.addEventListener('click', () => {
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

create.addEventListener('click', () => {
	gameSocket.send(JSON.stringify({
		'type': 'game.create'
	}));

	create.style.display = 'none';
	join.style.display = 'none';

	userInput.style.display = 'block';
	inviteButton.style.display = 'block';
});

join.addEventListener('click', () => {
	// gameSocket.send(JSON.stringify({
	// 	'type': 'game.join'
	// }));

	create.style.display = 'none';
	join.style.display = 'none';

	invitationBox.style.display = 'block';
});

inviteButton.addEventListener('click', function() {
    var userInput = document.getElementById('userInput').value;
    console.log('Texte saisi : ' + userInput);

	gameSocket.send(JSON.stringify({
		'type': 'game.invite',
		'message': userInput
	}));
});
