import * as game from './game.js';
import { gameData } from './game.js';
import { clearView } from "../index.js";



const invitations = [];



let lastPingTime = performance.now();

function updateTimer() {
	gameData.elapsedTime += 1;
}

let gameSocket;

// socket event
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

    gameSocket.onmessage = function(e) {
        const content = JSON.parse(e.data);
        var contentType = content.type;
        console.log("message received: ", content);
        updateInvitationList();
        if (contentType === 'game.accepted'){
            const message = content.message;
            game.gameRenderer(message);
            invitationBox.style.display = 'none';
            // #startbutton/stopbutton
            clearMenu()

        }
        if (contentType === 'game.join'){
            const message = content.message;
            game.gameRenderer(message);
            userInput.style.display = 'none';
            inviteButton.style.display = 'none';
        }
        if (contentType === 'game.invite'){
            const joinData = content.author;
            console.log("invitation from: ", joinData);
            invitations.push(joinData);
            updateInvitationList();
        }
        else if (contentType === 'game.update') {
            const message = content.message;
            console.log('update')
            game.gameRenderer(message);
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
    
    
    gameSocket.onclose = function(e) {
        // console.error('Game socket closed unexpectedly');
        console.log('Game socket closed');
    };
    console.log(idx)

    move(1);
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


// bouton game

document.querySelector('#startButton').onclick = function(e) {
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
};

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

// navigation bouton

// export const clearView = () => {
//     console.log("Appel ClearView")
//         document.querySelectorAll(".view").forEach(div => {
//             div.style.display = "none";
//         });
//     }

import { showHome } from "../home.js"

const   fastGame = document.getElementById('fastGame');
const   tournament = document.getElementById('tournament');
const   exit = document.getElementById('exit');
const   back = document.getElementById('back');
const   create = document.getElementById('create');
const   join = document.getElementById('join');
const   userInput = document.getElementById('inviteInput');
const   inviteButton = document.getElementById('inviteButton');
const   invitationBox = document.getElementById('invitationBox');


const gameMode = Object.freeze({
    MATCH: 0,
    TOURNAMENT: 1
})

const   sceneGamode = [fastGame, tournament, exit];
const   sceneType = [create, join, back];
const   sceneCreate = [userInput, inviteButton, back];
const   scene = [sceneGamode, sceneType, sceneCreate];
let     idx = -1;
let     status = gameMode.MATCH;


const clearMenu = () => {
    document.querySelectorAll(".menu-element").forEach(div => {
        div.style.display = "none";
    });
}

exit.addEventListener('click', () => {
	gameSocket.close();
    idx = -1;
    console.log(idx)
    clearMenu()
    showHome()
});

const move = (pas) => {
    if (idx + pas === scene.length || idx + pas < 0) 
        return ;
    idx += pas;
    console.log('move at: ' + idx)
    clearMenu()
    scene[idx].forEach( div => {
        div.style.display = "block";
    })
}

fastGame.addEventListener('click', () => {
	move(1);
});

tournament.addEventListener('click', () => {
    status = gameMode.TOURNAMENT;
    move(1);
});

back.addEventListener('click', () => {
	move(-1);
});

create.addEventListener('click', () => {
	if (status === gameMode.MATCH)
        var key = 'game.create'
    else
        var key = 'tournament.create'
    gameSocket.send(JSON.stringify({
		'type': key
	}));
    move(1);

});

inviteButton.addEventListener('click', function() {
    var userInput = document.getElementById('inviteInput').value;
    console.log('Texte saisi : ' + userInput);

	gameSocket.send(JSON.stringify({
		'type': 'game.invite',
		'message': userInput
	}));
});

join.addEventListener('click', () => {
	gameSocket.send(JSON.stringify({
		'type': 'game.join'
	}));

	// create.style.display = 'none';
	// join.style.display = 'none';

    updateInvitationList();
	invitationBox.style.display = 'block';
});




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