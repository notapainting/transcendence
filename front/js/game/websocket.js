import * as game from './game.js';
import { gameData } from './game.js';
import { moveTo, clearMenu, invitations } from './menu.js';
import { clearView } from "../index.js";

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


function updateTimer() {
	gameData.elapsedTime += 1;
}

export let gameSocket;

const messageHandler = (e) => {
    const content = JSON.parse(e.data);
    console.log("message: ", content.type);
    updateInvitationList();

    switch(content.type){
        case EventGame.INVITE:
            console.log("invitation from: ", content.author);
            invitations.push(content.author);
            updateInvitationList();
            break;
        case EventGame.JOIN:
            game.gameRenderer(content.message);
            break;
        case EventGame.ACCEPTED:
            game.gameRenderer(content.message);
            moveTo(3);
            break;
        case EventGame.READY:
            document.getElementById('ready-circle').style.background = '#0eee28';
            break;
        case EventGame.START:
            moveTo(4);
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
        case EventGame.UPDATE:
            game.gameRenderer(content.message);
            break;
        case EventGame.PAUSE:
            if (gameData.timerInterval) {
                clearInterval(gameData.timerInterval);
                gameData.timerInterval = null;
            }
            break;
        case EventGame.BROKE:
            moveTo(0);
            break;
        default:
            console.log("unknow type : ", content.type)
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
};

// refaire en supprimant la partei transition (utilsier funciton islem + naviguate To)
export const initGame = (path) => {
    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });

    document.querySelector("#home").style.display = "none"
    document.querySelector("#game").style.display = "block"
    console.log(path)
    gameSocket = new WebSocket(
        'wss://'
        + window.location.host
        + path
    );
    gameSocket.onmessage = messageHandler;
    gameSocket.onclose = function(e) {
        console.log('Game socket closed');
    };
    moveTo(0);
}


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