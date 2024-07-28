import { navigateTo } from "../index.js"
import { gameSocket, clearGame, clearInvList } from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
import { gameData } from './game.js';

// html element
// <!-- deplacement -->

const   start = document.getElementById('game-menu-start');
const   nextMatch = document.getElementById('game-menu-next');


// <!-- div buttons -->
const   menuM1 = document.getElementById('menu-m1-button');
const   menuM2a = document.getElementById('menu-m2a-button');
const   menuM2b = document.getElementById('menu-m2b-button');
const   menuM3 = document.getElementById('menu-m3-button');

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


// scene idx
let     idx = enu.sceneIdx.WELCOME;

// invitations received in remote mode
export let invitations = [];

// list of players invited
let     players = [];

// current match data
let     currentPlayers = [];
let     currentScore = [0, 0];
let     paused = false;
let     locked = false;

// scene
const   scene = [
    [menuM1, invitationBox], // accueil du jeu
    [menuM2a, locContainerList, locContainerSettings], // creation de partie/tournoi (host only)
    [menuM2b], // waiting room pour creation de tournoi (guest only)
    [menuM3, bannerPhase], // phases du tournoi : montre les prochain match de la phase et leur etat
    [bannerMatch, ready, circle], // afk check
    [bannerScore, pause], // in game
    [bannerEnd], // ecran de fin de match 
    [], // ecran de fin de tournoi (recap)
    [], // ecran erreur
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
 // 0 (C) acceuil du jeu -> containerMenu (Local+Match+Tournament+quit), containerInvitedBy
 // 1 (C/A)(host) creation de partie/tournoi -> containerSettings, containerInvitations (simple/status+ready), containerMenu (start+((C)home/(A)exit))
 // 2 (C)(guest) waiting room -> containerSettingsFrozen, containerInvitationsFrozen, containerMenuGuest (ready+quit)
 // 3 (C/A) tounoi phase -> containerPhase, containerMenu (nextmatch+quit)
 // 4 (C/A) pre match, ready check -> ready, 
 // 5 (C/A) match -> conatinerScores, containerMenu (pause+abandon)
 // 6 (C/A) fin match -> containerWinner (5s)
 // 7 (C/A) fin tournoi -> containerClassement, containerMenu (home+quit)
 // 8 (C) broken/quit containerError, containerMenu (home+quit)

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
    console.log("in intm")
    
    if (path === enu.backendPath.LOCAL) {
        status = enu.gameMode.LOCAL;
        anon = true;
        players = [];
        clearInvitationList();
        moveTo(enu.sceneIdx.CREATION);
        console.log("init : local");
    } else {
        status = enu.gameMode.IDLE;
        anon = false;
        clearInvitationList();
        console.log("init : remote");
        moveTo(enu.sceneIdx.WELCOME);
    }
}

export const clearInvitationList = () => {
    const local = document.getElementById('game-menu-list');
    while (local.firstChild) {local.removeChild(local.lastChild);}
    players = [];
}


/*** utils ***/
function isAlphaNumeric(str) {
    var code, i, len;

    for (i = 0, len = str.length; i < len; i++) {
      code = str.charCodeAt(i);
      if (!(code > 47 && code < 58) && 
          !(code > 64 && code < 91) && 
          !(code > 96 && code < 123) &&
          (code != 95) && (code != 45)) { 
        return false;
      }
    }
    return true;
  };

const validate_name = (name) => {
    console.log("test value : " + name)
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
    scene[idx].forEach(div => {console.log(div);div.style.display = "flex";});
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
    moveTo(enu.sceneIdx.CREATION);
})



ready.addEventListener('click', () => {
    if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.READY}));
    else if (status === enu.gameMode.MATCH) gameSocket.send(JSON.stringify({'type': enu.EventGame.READY}));
    else if (status === enu.gameMode.LOCAL) {
        moveTo(enu.sceneIdx.MATCH);
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



const quitFunc = () => {
    clearInvitationList();
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
        if (status === enu.gameMode.TOURNAMENT) gameSocket.send(JSON.stringify({'type': enu.EventTournament.QUIT}));
        else if (status === enu.gameMode.MATCH || status === enu.gameMode.LOCAL) gameSocket.send(JSON.stringify({'type': enu.EventGame.QUIT}));
        status = enu.gameMode.IDLE;
        if (idx === enu.sceneIdx.WELCOME) {
            fullClear()
            navigateTo("/");
        }
    moveTo(to);
};

document.querySelectorAll("button-menu-quit").forEach(div => {div.addEventListener('click', quitFunc)});

document.getElementById('game-menu-m1-quit').addEventListener('click', quitFunc);
document.getElementById('game-menu-m2a-quit').addEventListener('click', quitFunc);
document.getElementById('game-menu-m2b-quit').addEventListener('click', quitFunc);
document.getElementById('game-menu-m3-quit').addEventListener('click', quitFunc);


start.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) {
        gameSocket.send(JSON.stringify({
            'type': enu.EventLocal.PLAYERS,
            'message':players,
        }));
    } else if (status === enu.gameMode.MATCH) {
        gameSocket.send(JSON.stringify({'type': enu.EventGame.START}));
        moveTo(enu.sceneIdx.MATCH);
    } else if (status === enu.gameMode.TOURNAMENT) {
        gameSocket.send(JSON.stringify({'type': enu.EventTournament.START}));
    }
})

nextMatch.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) gameSocket.send(JSON.stringify({'type': enu.EventLocal.NEXT}));
    else moveTo(enu.sceneIdx.PREMATCH)
})

document.getElementById('game-menu-local-input-button').addEventListener('click', () => {
    const   user = document.getElementById('game-menu-input-player').value;
    document.getElementById('game-menu-input-player').value = '';
    if (validate_name(user) === false) return ;
    players.push(user);

    if (status === enu.gameMode.LOCAL) {
        createListLocal(user)
    } else if (status === enu.gameMode.MATCH) {
        createListRemote(user, enu.EventGame.INVITE, enu.EventGame.KICK)
    } else if (status === enu.gameMode.TOURNAMENT) {
        createListRemote(user, enu.EventTournament.INVITE, enu.EventTournament.KICK)
    }
})

const createListLocal = (user) => {
    const   item = document.createElement('li');
    const   itemName = document.createElement('div');
    const   button = document.createElement('button');
    
    item.className = 'list-tournoi-element';
    itemName.textContent = user;
    itemName.className = 'list-tournoi-user-name';
    // button.textContent = 'Remove';
    button.className = 'remove-button';
    button.addEventListener('click', (e) => {
        const pos = players.indexOf(user);
        players.splice(pos, 1);
        e.target.parentElement.remove();
    });

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 448 512');
    svg.setAttribute('class', 'svgIcon'); 

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z');
    path.setAttribute('fill', 'white'); 

    svg.appendChild(path);
    button.appendChild(svg);
    item.appendChild(itemName);
    item.appendChild(button);
    document.getElementById('game-menu-list').appendChild(item);
}

const createListRemote = (user, invite, kick) => {
    const   item = document.createElement('li');
    const   itemPicture = document.createElement('img');
    const   itemName = document.createElement('div');
    const   button = document.createElement('button');
    const   itemStatus = document.createElement('span');

    item.className = 'list-tournoi-element';
    itemPicture.className = 'list-tournoi-user-pic';
    itemPicture.src = '../../img/anon.jpg'; // a remplacer !!!! (par la vrai foto)
    itemName.textContent = user;
    itemName.className = 'list-tournoi-user-name';
    itemStatus.id = 'invite-status' + user;
    itemStatus.className = 'remote-list-element';
    // itemStatus.textContent = '...waiting...';

    button.className = 'remove-button';
    button.addEventListener('click', (e) => {
        const pos = players.indexOf(user);
        players.splice(pos, 1);
        e.target.parentElement.remove();
        gameSocket.send(JSON.stringify({
            'type': kick,
            'message': user
        }));
    });

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 448 512');
    svg.setAttribute('class', 'svgIcon'); 

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z');
    path.setAttribute('fill', 'white'); 

    svg.appendChild(path);
    item.appendChild(itemPicture);
    item.appendChild(itemName);
    item.appendChild(itemStatus);

    item.innerHTML += `
        <div class="typing-indicator">
            <div class="typing-circle"></div>
            <div class="typing-circle"></div>
            <div class="typing-circle"></div>
            <div class="typing-shadow"></div>
            <div class="typing-shadow"></div>
            <div class="typing-shadow"></div>
        </div>
    `;

    button.appendChild(svg);
    item.appendChild(button);

    document.getElementById('game-menu-list').appendChild(item);

    gameSocket.send(JSON.stringify({
        'type': invite,
        'message': user,
    }));
}



/*
function createInviteListElement () {
    if (status === enu.gameMode.ANON || status === enu.gameMode.LOCAL) createInviteListElementLocal();
    else if (status === enu.gameMode.MATCH) createInviteListElementRemote();
}
*/