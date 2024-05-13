import * as game from './game.js';
import { gameData } from './game.js';

const gameSocket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/ws-game/'
);

let lastPingTime = performance.now();

gameSocket.onmessage = function(e) {
    const message = JSON.parse(e.data);
    // explosion(message);
	game.gameRenderer(message);
    
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

document.querySelector('#backButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'back button click !'
	}));
};

document.querySelector('#startButton').onclick = function(e) {
    if (gameData.start)
    {
        gameSocket.send(JSON.stringify({
            'message': 'startButton'
        }));
    }
};

document.querySelector('#stopButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'stopButton'
	}));
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