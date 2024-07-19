import { navigateTo } from "../index.js"
import { gameSocket, clearGame, clearInvList } from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
import { gameData } from './game.js';

// html element
// <!-- deplacement -->

const   start = document.getElementById('game-menu-start');
const   nextMatch = document.getElementById('game-menu-next');
const   quit = document.getElementById('game-menu-quit');

// <!-- local  -->
const   locContainerList = document.getElementById('game-menu-list-tournament');
const   locContainerSettings = document.getElementById('game-menu-settings');


// <!-- remote -->
// <!-- choose mode -->
const   createMatch = document.getElementById('game-menu-fastGame');
const   createTournament = document.getElementById('game-menu-tournament');
const   createLocal = document.getElementById('game-menu-local');

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


/*** variable ****/

// client's status
let     status = enu.gameMode.IDLE;
let     anon = true;

export const changeStatus = (type) => {
    console.log("change from " + status + " to " + type)
    status = type;

}

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
    [createLocal,createMatch, createTournament, invitationBox, quit], // accueil du jeu
    [userInput, inviteButton, invitationSent, start, quit], // creation de partie/tournoi (host only)
    [], // waiting room pour creation de tournoi (guest only)
    [bannerPhase, nextMatch, quit], // phases du tournoi : montre les prochain match de la phas eet leur etat
    [bannerMatch, ready, circle, quit], // afk check
    [bannerScore, pause, quit], // in game
    [bannerEnd, quit], // ecran de fin de match 
    [], // ecran de fin de tournoi (recap)
    [], // ecran erreur
];

const   sceneLoc = [
    [start, quit, locContainerList, locContainerSettings],
    [bannerPhase, nextMatch, quit],
    [bannerMatch, ready],
    [bannerScore, pause, quit],
    [bannerEnd],
    [quit],
];

/*
quit = home(C)/exit(A)

m1 : local match tournoi exit
m2 : start quit
m2a : ready quit
m3 : next quit
m4 : ready
m5 : pause quit (abandon)
m6 : quit 
m7 : quit 

*/


// status == idle/match/tournoi/local/anon
const   sceneWIP = [
    [], // 0 (C) acceuil du jeu -> containerMenu (Local+Match+Tournament+quit), containerInvitedBy
    [], // 1 (C/A)(host) creation de partie/tournoi -> containerSettings, containerInvitations (simple/status+ready), containerMenu (start+((C)home/(A)exit))
    [], // 2 (C)(guest) waiting room -> containerSettingsFrozen, containerInvitationsFrozen, containerMenuGuest (ready+quit)
    [], // 3 (C/A) tounoi phase -> containerPhase, containerMenu (nextmatch+quit)
    [], // 4 (C/A) pre match, ready check -> ready, 
    [], // 5 (C/A) match -> conatinerScores, containerMenu (pause+abandon)
    [], // 6 (C/A) fin match -> containerWinner (5s)
    [], // 7 (C/A) fin tournoi -> containerClassement, containerMenu (home+quit)
    [], // 8 (C) broken/quit containerError, containerMenu (home+quit)
]
// ANON : 1 -> 3 -> 4 -> 5 -> 6
//             ^         |
//             |<---  <---

// CONNECTED : TOURNOI
// (HOST)
//  : 0 -> 1 -> 3 -> 4 -> 5 -> 6
//              ^         |
//              |<---  <---
// (GUEST)
//  : 0 -> 2 -> ...same as host

// CONNECTED : MATCH
// (HOST)
//  : 0 -> 1 -> 4 -> 5 -> 6

// (GUEST)
//  : 0-> 4 -> 5 -> 6




/*** initialisation ****/
export const initMenu = (path) => {
    if (path === enu.backendPath.LOCAL) {
        status = enu.gameMode.LOCAL;
        scene = sceneLoc;
        players = [];
        clearLocList();
        console.log("init : local");
    } else {
        status = enu.gameMode.IDLE;
        anon = false;
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


createLocal.addEventListener('click', () => {
    status = enu.gameMode.LOCAL;
    gameSocket.send(JSON.stringify({'type': enu.EventLocal.MODE}));
    scene = sceneLoc;
    moveTo(enu.sceneIdx.WELCOME);
})



ready.addEventListener('click', () => {
    if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.READY}));
    else if (status === enu.gameMode.MATCH) gameSocket.send(JSON.stringify({'type': enu.EventGame.READY}));
    else if (status === enu.gameMode.LOCAL) {
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



quit.addEventListener('click', () => {
    if (anon === true) {
        if (idx == enu.sceneIdx.CREATION) {
            console.log("ANON exit")
            if (gameSocket !== null) gameSocket.close();
            fullClear()
            navigateTo("/");
            return ;
        }
        var to = enu.sceneIdx.CREATION;
    } else var to = enu.sceneIdx.WELCOME;
        scene = sceneRem
        status = enu.gameMode.IDLE;
        if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.QUIT}));
        else if (status === enu.gameMode.MATCH || status === enu.gameMode.LOCAL) gameSocket.send(JSON.stringify({'type': enu.EventGame.QUIT}));
        if (idx === enu.sceneIdx.WELCOME) {
            fullClear()
            navigateTo("/");
        }
    moveTo(to);
});



start.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) {
        gameSocket.send(JSON.stringify({
            'type': enu.EventLocal.PLAYERS,
            'message':players,
        }));
    } else if (status === enu.gameMode.MATCH) {
        gameSocket.send(JSON.stringify({'type': enu.EventGame.START}));
        moveTo(enu.sceneLocIdx.MATCH);
    } else if (status === enu.gameMode.TOURNAMENT) {
        gameSocket.send(JSON.stringify({'type': enu.EventTournament.START}));

    }
})

nextMatch.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) gameSocket.send(JSON.stringify({'type': enu.EventLocal.NEXT}));
    else moveTo(enu.sceneIdx.PREMATCH)
})

// invitation list for remote
document.getElementById('game-menu-inviteButton').addEventListener('click', function() {
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

// invitation list for local
/*** list of players in local mode ****/
document.getElementById('game-menu-local-input-button').addEventListener('click', () => {
    const   user = document.getElementById('game-menu-local-input').value;
    document.getElementById('game-menu-local-input').value = '';
    if (validate_name(user) === false) return ;
    players.push(user);

    const   listItem = document.createElement('li');
    const   listItemName = document.createElement('span');
    const   removeButton = document.createElement('button');

    listItem.className = 'list-tournoi-element';
    listItemName.textContent = user;
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

/*
function createInviteListElement () {
    if (status === enu.gameMode.ANON || status === enu.gameMode.LOCAL) createInviteListElementLocal();
    else if (status === enu.gameMode.MATCH) createInviteListElementRemote();
}

function createInviteListElementLocal () {
    const   input = document.getElementById('game-menu-local-input').value;
    if (validate_name(user) === false) return ;

    players.push(user);

    const   item = document.createElement('li');
    const   itemName = document.createElement('span');
    const   itemButton = document.createElement('button');

    item.className = 'list-tournoi-element';
    item.id = `invite-${input}`
    itemName.textContent = input;
    itemButton.textContent = "remove";
    removeButton.className = "remove-button";
    
    removeButton.addEventListener('click', (e) => {
        let pos = players.indexOf(input);
        players.splice(pos, 1);
        e.target.parentElement.remove();
    });

    item.appendChild(itemName);
    item.appendChild(itemButton);
    document.getElementById('game-menu-list').appendChild(item);
}

function createInviteListElementRemote () {
    const   input = document.getElementById('game-menu-local-input').value;
    if (validate_name(user) === false) return ;

    const   item = document.createElement('li');
    const   itemName = document.createElement('span');
    const   itemStatus = document.createElement('span');
    const   itemButton = document.createElement('button');

    item.className = 'list-tournoi-element';
    itemName.textContent = input;
    itemStatus.id = `invite-status-${input}`;
    itemStatus.textContent = "..pending..";
    itemButton.textContent = "remove";
    removeButton.className = 'remove-button';
    
    removeButton.addEventListener('click', (e) => {
        let pos = players.indexOf(input);
        players.splice(pos, 1);
        e.target.parentElement.remove();
    });

    item.appendChild(itemName);
    item.appendChild(itemStatus);
    item.appendChild(itemButton);
    document.getElementById('game-menu-list').appendChild(item);
}
*/