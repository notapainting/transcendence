import { showHome } from "../home.js"
import { gameSocket, EventGame, EventTournament } from "./websocket.js"
export let invitations = [];

const gameMode = Object.freeze({
    MATCH: 0,
    TOURNAMENT: 1
})

const   fastGame = document.getElementById('fastGame');
const   tournament = document.getElementById('tournament');
const   exit = document.getElementById('exit');
const   back = document.getElementById('back');
const   create = document.getElementById('create');
const   join = document.getElementById('join');
const   userInput = document.getElementById('inviteInput');
const   inviteButton = document.getElementById('inviteButton');
const   invitationBox = document.getElementById('invitationBox');
const   ready = document.getElementById('ready');
const   pause = document.getElementById('game-pause');
const   circle = document.getElementById('ready-circle');

const   sceneGamode = [fastGame, tournament, invitationBox, exit];
const   sceneType = [create, invitationBox, back];
const   sceneCreate = [userInput, inviteButton, back];
const   sceneReady = [ready, circle, exit];
const   sceneMatch = [pause];
const   sceneEnd = [];
const   scene = [sceneGamode, sceneType, sceneCreate, sceneReady, sceneMatch, sceneEnd];
let     idx = -1;
let     status = gameMode.MATCH;


export const clearMenu = () => {
    document.querySelectorAll(".menu-element").forEach(div => {
        div.style.display = "none";
    });
    circle.style.background = '#ee0e0e';
    invitationBox.style.display = 'none';
}

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

export const moveTo = (i) => {
    if (i === scene.length || i < 0) 
        return ;
    idx = i;
    console.log('move to: ' + idx)
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

create.addEventListener('click', () => {
	if (status === gameMode.MATCH)
        var key = EventGame.CREATE
    else
        var key = EventTournament.CREATE
    gameSocket.send(JSON.stringify({
		'type': key
	}));
    move(1);

});

inviteButton.addEventListener('click', function() {
    var userInput = document.getElementById('inviteInput').value;
    console.log('Texte saisi : ' + userInput);

	gameSocket.send(JSON.stringify({
		'type': EventGame.INVITE,
		'message': userInput
	}));
});

ready.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({
		'type': EventGame.READY
	}));
});

pause.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({
		'type': EventGame.PAUSE
	}));
});

join.addEventListener('click', () => {
	gameSocket.send(JSON.stringify({
		'type': EventGame.JOIN
	}));

    updateInvitationList();
	invitationBox.style.display = 'block';
});

back.addEventListener('click', () => {
	move(-1);
});

exit.addEventListener('click', () => {
	gameSocket.close();
    idx = -1;
    console.log(idx)
    clearMenu()
    showHome()
});
