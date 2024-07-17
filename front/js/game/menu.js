import { navigateTo } from "../index.js"
import { gameSocket, clearGame, clearInvList } from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
import { gameData } from './game.js';

// html element
// <!-- deplacement -->
const   exit = document.getElementById('game-menu-exit');
const   back = document.getElementById('game-menu-back');
const   home = document.getElementById('game-menu-home');
const   start = document.getElementById('game-menu-start');
const   nextMatch = document.getElementById('game-menu-next');

// <!-- local  -->
const   locInput = document.getElementById('game-menu-local-input');
const   locInputBut = document.getElementById('game-menu-local-input-button');
const   locList = document.getElementById('game-menu-list');

// <!-- remote -->
// <!-- choose mode -->
const   createMatch = document.getElementById('game-menu-fastGame');
const   createTournament = document.getElementById('game-menu-tournament');

// <!-- invite player -->
const   userInput = document.getElementById('game-menu-inviteInput');
const   inviteButton = document.getElementById('game-menu-inviteButton');
const   invitationBox = document.getElementById('game-menu-invitationBox');
const   invitationSent = document.getElementById('game-menu-invite-sent-list');

// <!-- set ready -->
const   ready = document.getElementById('game-menu-ready');
const   circle = document.getElementById('game-menu-ready-circle');

// <!-- in game banner -->
const   bannerPhase = document.getElementById('game-menu-banner-phase');
const   bannerMatch = document.getElementById('game-menu-banner-match');
const   bannerScore = document.getElementById('game-menu-banner-score');
const   bannerEnd = document.getElementById('game-menu-banner-end');

// <!-- in game button -->
const   pause = document.getElementById('game-pause');
const   abandon = document.getElementById('game-abandon');


/*** variable ****/

// client's status
let     status = enu.gameMode.MATCH;

// is sceneRem or sceneLoc depending on status
let     scene = null;

// scene idx
let     idx = enu.sceneIdx.WELCOME;

// invitations received in remote mode
export let invitations = [];

// list of players in local mode and invited players in remote
let     players = [];
let     invited = []

// current match data
let     currentPlayers = [];
let     currentScore = [0, 0];
let     paused = false;
let     locked = false;

// scene
const   sceneRem = [
    [createMatch, createTournament, invitationBox, exit], // acceuil du jeu
    [userInput, inviteButton, invitationSent, home], // creation de partie/tournoi (host only)
    [], // waiting room pour creation de tournoi (guest only)
    [bannerPhase], // phases du tournoi : montre les prochain match de la phas eet leur etat
    [bannerMatch, ready, circle, exit], // afk check
    [bannerScore, pause, abandon], // in game
    [bannerEnd, home, exit], // ecran de fin de match 
    [], // ecran de fin de tournoi (recap)
    [], // ecran erreur
];

const   sceneLoc = [
    [locInput, locInputBut, locList, start, exit],
    [bannerPhase, nextMatch, exit],
    [bannerMatch, ready],
    [bannerScore, pause, exit],
    [bannerEnd],
    [home, exit],
];


/*** initialisation ****/
export const initMenu = (path) => {
    if (path === enu.backendPath.LOCAL) {
        status = enu.gameMode.LOCAL;
        scene = sceneLoc;
        players = [];
        clearLocList();
        console.log("init : local");
    } else {
        status = enu.gameMode.MATCH;
        scene = sceneRem;
        clearSentList();
        console.log("init : remote");
    }
    moveTo(enu.sceneIdx.WELCOME);
}

const clearLocList = () => {
    const local = document.getElementById('game-menu-list');
    while (local.firstChild) {local.removeChild(local.lastChild);}
}

export const clearSentList = () => {
    const local = document.getElementById('game-menu-invite-sent-list');
    while (local.firstChild) {local.removeChild(local.lastChild);}
    invited = []
}


/*** utils ***/
function isAlphaNumeric(str) {
    var code, i, len;

    for (i = 0, len = str.length; i < len; i++) {
      code = str.charCodeAt(i);
      if (!(code > 47 && code < 58) && 
          !(code > 64 && code < 91) && 
          !(code > 96 && code < 123)) { 
        return false;
      }
    }
    return true;
  };

const validate_name = (name) => {
    if (name.length > 20) return false;
    if (name === "") return false;
    if (isAlphaNumeric(name) === false) return false;
    return true;
}

// allow to lock pause in remote game if oponent has paused the game
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

/*** banner update ****/
export const updateScore = (data) => {
    currentScore = data.score;
    currentPlayers = data.players;
}

export const announcePhase = (data) => {
    const   banner = document.getElementById('game-menu-banner-phase')
    banner.innerHTML = '';
    data.forEach((matchData) => {banner.innerHTML += matchData[0] + " VS " + matchData[1] + "<br>";})
}

export const announceMatch = (data) => {
    const   banner = document.getElementById('game-menu-banner-match')
    banner.innerHTML = data[0] + " VS " + data[1];
    currentPlayers = [data[0], data[1]];
    currentScore = [0, 0];
}

export const announceScore = () => {
    const   banner = document.getElementById('game-menu-banner-score')
    banner.innerHTML = currentPlayers[0] + " : " + currentScore[0] + "                " + currentPlayers[1] + " : " + currentScore[1];
}

export const announceWinner = (data) => {
    const   banner = document.getElementById('game-menu-banner-end')
    banner.innerHTML = "WINNER IS " + data;
}

/*** menu deplacement ****/
export const clearMenu = () => {
    document.querySelectorAll(".menu-element").forEach(div => {div.style.display = "none";});
    circle.style.background = '#ee0e0e';
}

export const goBack = () => {
    if (idx == enu.sceneIdx.WELCOME) return ;
    idx--;
    console.log('go back to: ' + idx)
    clearMenu()
    scene[idx].forEach(div => {div.style.display = "block";});
}

export const goNext = () => {
    if (idx == length(scene)) return ;
    idx++;
    console.log('go next to: ' + idx)
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
createMatch.addEventListener('click', () => {
    status = enu.gameMode.MATCH;
    gameSocket.send(JSON.stringify({'type': enu.EventGame.CREATE}));
    moveTo(enu.sceneIdx.CREATION);
});

createTournament.addEventListener('click', () => {
    status = enu.gameMode.TOURNAMENT;
    gameSocket.send(JSON.stringify({'type': enu.EventTournament.CREATE}));
    moveTo(enu.sceneIdx.CREATION);
});


inviteButton.addEventListener('click', function() {
    var userInput = document.getElementById('game-menu-inviteInput').value;
    if (userInput === "") return ;
    document.getElementById('game-menu-inviteInput').value = '';

    console.log('Texte saisi : ' + userInput);

    if (status === enu.gameMode.MATCH) {
        var inviteType = enu.EventGame.INVITE
        var kickType = enu.EventGame.KICK
    } else {
        var inviteType = enu.EventTournament.INVITE;
        var kickType = enu.EventTournament.KICK
    }
    
    gameSocket.send(JSON.stringify({
        'type': inviteType,
        'message': userInput
    }));
    invited.push(userInput);

    const   listItem = document.createElement('li');
    listItem.className = 'remote-list-element';
    
    const   listItemName = document.createElement('span');
    listItemName.textContent = userInput;

    const   removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.className = 'remove-button';
    removeButton.addEventListener('click', (e) => {
        let pos = players.indexOf(e.target.parentNode.firstChild.innerHTML);
        players.splice(pos, 1);
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': kickType,
            'message': userInput
        }));
    });
    
    const   listItemStatus = document.createElement('span');
    listItemStatus.id = userInput;
    listItemStatus.className = 'remote-list-element';
    listItemStatus.textContent = '...waiting...';

    listItem.appendChild(listItemName);
    listItem.appendChild(removeButton);
    listItem.appendChild(listItemStatus);

    document.getElementById('game-menu-invite-sent-list').appendChild(listItem);

});

ready.addEventListener('click', () => {
    if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.READY}));
    else gameSocket.send(JSON.stringify({'type': enu.EventGame.READY}));
    if (status === enu.gameMode.LOCAL) {
        moveTo(enu.sceneLocIdx.MATCH);
        announceScore();
    }
});

pause.addEventListener('click', () => {
    if (locked === true) return ;
    gameSocket.send(JSON.stringify({'type': enu.EventGame.PAUSE}));
    togglePause();
    if (status === enu.gameMode.LOCAL) {
        if (gameData.timerInterval) {
            clearInterval(gameData.timerInterval);
            gameData.timerInterval = null;
        }
    }
});

back.addEventListener('click', () => {
    goBack();
});

exit.addEventListener('click', () => {
    if (gameSocket !== null) gameSocket.close();
    idx = enu.sceneIdx.WELCOME;
    console.log("quit")
    clearInvList();
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
    if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.QUIT}));
    else gameSocket.send(JSON.stringify({'type': enu.EventGame.QUIT}));
    clearSentList();
});

nextMatch.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({'type': enu.EventLocal.NEXT}));
})

start.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) {
        gameSocket.send(JSON.stringify({
            'type': enu.EventLocal.PLAYERS,
            'message':players,
        }));
    } else {
        gameSocket.send(JSON.stringify({'type': enu.EventGame.START}));
        moveTo(enu.sceneLocIdx.MATCH);
    }
})


/*** list of players in local mode ****/
document.getElementById('game-menu-local-input-button').addEventListener('click', () => {
    const   user = document.getElementById('game-menu-local-input').value;
    document.getElementById('game-menu-local-input').value = '';
    if (validate_name(user) === false) return ;
    players.push(user);

    const   listItem = document.createElement('li');
    const   listItemName = document.createElement('span');
    const   removeButton = document.createElement('button');

    listItemName.textContent = user;
    listItem.className = 'list-tournoi-element';
    removeButton.textContent = 'Remove';
    removeButton.className = 'accept-button';
    removeButton.addEventListener('click', (e) => {
        let pos = players.indexOf(e.target.parentNode.firstChild.innerHTML);
        players.splice(pos, 1);
        e.target.parentElement.remove();
    });
    listItem.appendChild(listItemName);
    listItem.appendChild(removeButton);
    document.getElementById('game-menu-list').appendChild(listItem);
})

