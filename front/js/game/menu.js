import { navigateTo } from "../index.js"
import { gameSocket, clearGame } from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
export let invitations = [];


const   fastGame = document.getElementById('game-menu-fastGame');
const   tournament = document.getElementById('game-menu-tournament');
const   exit = document.getElementById('game-menu-exit');
const   back = document.getElementById('game-menu-back');
const   create = document.getElementById('game-menu-create');
const   userInput = document.getElementById('game-menu-inviteInput');
const   inviteButton = document.getElementById('game-menu-inviteButton');
const   invitationBox = document.getElementById('game-menu-invitationBox');
const   ready = document.getElementById('game-menu-ready');
const   circle = document.getElementById('game-menu-ready-circle');
const   home = document.getElementById('game-menu-home');
const   pause = document.getElementById('game-pause');
const   abandon = document.getElementById('game-abandon');

/*** scene list ****/
const   sceneGamode = [fastGame, tournament, invitationBox, exit];
const   sceneType = [create, invitationBox, back];
const   sceneCreate = [userInput, inviteButton, back];
const   sceneReady = [ready, circle, exit];
const   sceneMatch = [pause, abandon];
const   sceneEnd = [home, exit];
const   scene = [sceneGamode, sceneType, sceneCreate, sceneReady, sceneMatch, sceneEnd];
let     idx = enu.sceneIdx.WELCOME;
let     status = enu.gameMode.MATCH;


/*** menu deplacement ****/
export const clearMenu = () => {
    document.querySelectorAll(".menu-element").forEach(div => {div.style.display = "none";});
    circle.style.background = '#ee0e0e';
}

const goBack = () => {
    if (idx == enu.sceneIdx.WELCOME) return ;
    idx--;
    console.log('go back to: ' + idx)
    clearMenu()
    scene[idx].forEach(div => {div.style.display = "block";});
}

export const moveTo = (i) => {
    if (i === scene.length || i < 0) return ;
    idx = i;
    console.log('move to: ' + i)
    if (idx === enu.sceneIdx.END) clearGame();
    clearMenu();
    scene[idx].forEach(div => {div.style.display = "block";});
}

/*** event listener ****/
fastGame.addEventListener('click', () => {
    moveTo(enu.sceneIdx.TYPE);
});

tournament.addEventListener('click', () => {
    status = gameMode.TOURNAMENT;
    moveTo(enu.sceneIdx.TYPE);
});

create.addEventListener('click', () => {
    if (status === enu.gameMode.MATCH) gameSocket.send(JSON.stringify({'type': enu.EventGame.CREATE}));
    else gameSocket.send(JSON.stringify({'type': enu.EventTournament.CREATE}));
    moveTo(enu.sceneIdx.CREATION);
});

inviteButton.addEventListener('click', function() {
    var userInput = document.getElementById('game-menu-inviteInput').value;
    console.log('Texte saisi : ' + userInput);
    gameSocket.send(JSON.stringify({
        'type': enu.EventGame.INVITE,
        'message': userInput
    }));
});

ready.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({'type': enu.EventGame.READY}));
});

let paused = false;
pause.addEventListener('click', () => {
    if (locked === true) return ;
    gameSocket.send(JSON.stringify({'type': enu.EventGame.PAUSE}));
    togglePause();
});

let locked = false;
export const toggleLock = () => {
    if (locked == false) locked = true;
    else if (locked == true) locked = false;
    console.log('locked : ' + locked);
}

export const togglePause = () => {
    if (paused === false) {
        paused = true;
        pause.innerHTML = "Resume";
    } else {
        paused = false;
        pause.innerHTML = "Pause";
    }
    console.log('paused : ' + paused);
}

back.addEventListener('click', () => {
    goBack();
});

exit.addEventListener('click', () => {
    gameSocket.close();
    idx = enu.sceneIdx.WELCOME;
    console.log(idx)
    fullClear();
    navigateTo("/")
});

abandon.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({'type': enu.EventGame.QUIT}));
    fullClear();
    moveTo(enu.sceneIdx.END);
});

home.addEventListener('click', () => {
    moveTo(enu.sceneIdx.WELCOME);
});

