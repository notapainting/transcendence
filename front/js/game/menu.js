import { navigateTo } from "../index.js"
import { gameSocket, clearGame} from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
import { gameData } from './game.js';

// html element
// <!-- deplacement -->

const   start = document.getElementById('game-menu-start');
const   nextMatch = document.getElementById('game-menu-next');
const   settingsReInit = document.getElementById('settings-button-reinit');


// <!-- div buttons -->
const   menuM1 = document.getElementById('menu-m1-button');
const   menuM2a = document.getElementById('menu-m2a-button');
const   menuM2b = document.getElementById('menu-m2b');
const   menuM3 = document.getElementById('menu-m3');
const   menuM4 = document.getElementById('menu-m4');
const   menuM5 = document.getElementById('menu-m5');
const   menuM6 = document.getElementById('menu-m6-button');

// <!-- animated background -->
const   menuBgVid = document.getElementById('menu_bg_video');
const   menuBg = document.getElementById('menu-background');

// <!-- local  -->
const   locContainerList = document.getElementById('game-menu-list-tournament');
const   locContainerSettings = document.getElementById('game-menu-settings');
const   settingsSendBonus = document.getElementById('bonusToggle');
const   settingsSendScore = document.getElementById('scoreRange');
const   settingsSendPlayer = document.getElementById('playersRange');


// <!-- remote -->
// <!-- choose mode -->
const   createMatch = document.getElementById('game-menu-fastGame');
const   createTournament = document.getElementById('game-menu-tournament');
const   createLocal = document.getElementById('game-menu-local');

// <!-- invite player -->
const   invitationBox = document.getElementById('game-menu-invitationBox');

// <!-- set ready -->
const   ready = document.getElementById('game-menu-ready');
const   readyP = document.getElementById('game-menu-ready-prematch');
const   circle = document.getElementById('game-menu-ready-circle');

// <!-- in game banner -->
// const   bannerPhase = document.getElementById('game-menu-banner-phase');
// const   bannerMatch = document.getElementById('game-menu-banner-match');
// const   bannerScore = document.getElementById('game-menu-banner-score');
const   bannerEnd = document.getElementById('game-menu-banner-end');

// <!-- in game button -->
const   pause = document.getElementById('game-menu-pause');


/*** variable ****/

// client's status
let     status = enu.gameMode.IDLE;
let     anon = true;

export const changeGameStatus = (type) => {
    console.log("change from " + status + " to " + type)
    status = type;
}

export const getGameStatus = () => {
    return status;
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
    [menuBg, menuBgVid, menuM1, invitationBox], // accueil du jeu
    [menuBgVid, menuM2a, locContainerList, locContainerSettings], // creation de partie/tournoi (host only)
    [menuBgVid, menuM2b], // waiting room pour creation de tournoi (guest only)
    [menuBgVid, menuM3], // phases du tournoi : montre les prochain match de la phas eet leur etat
    [menuBgVid, menuM4], // afk check
    [menuM5], // in game
    [menuM6, bannerEnd], // ecran de fin de match 
    [menuM6], // ecran de fin de tournoi (recap)
    [menuM6], // ecran erreur
];



/*** initialisation ****/
export const initMenu = (path) => {
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
        moveTo(enu.sceneIdx.WELCOME);
        
    }
}

export const clearInvitationList = () => {
    const local = document.getElementById('game-menu-list');
    while (local.firstChild) {local.removeChild(local.lastChild);}
    players = [];
}

/*** menu deplacement ****/
export const clearMenu = () => {
    document.querySelectorAll(".menu-element").forEach(div => {div.style.display = "none";});
}

export const moveTo = (i) => {
    if (i === scene.length || i < 0) return ;
    idx = i;
    clearMenu();
    if (idx === enu.sceneIdx.CREATION) {
        clearGame();
    }
    scene[idx].forEach(div => {div.style.display = "flex";});
    if (idx === enu.sceneIdx.END && status !== enu.gameMode.MATCH) menuM6.style.display = "none";
}


/*** banner update ****/
export const updateScore = (data) => {
    currentScore = data.score;
    currentPlayers = data.players;
}

export const announcePhase = (data) => {
    document.getElementById('banner-phase-text').innerHTML = '';
    data.forEach((matchData) => {
        const   item = document.createElement('li');
        const   itemPlayer1 = document.createElement('div');
        const   itemPlayer2 = document.createElement('div');
        const   itemVS = document.createElement('div');
    
        item.className = 'list-banner-element';
        itemPlayer1.textContent = matchData[0];
        itemPlayer2.textContent = matchData[1];
        itemVS.textContent = 'vs';
        itemPlayer1.className = 'list-banner-user-name';
        itemPlayer2.className = 'list-banner-user-name';
        itemVS.className = 'list-banner-vs';
    
        item.appendChild(itemPlayer1);
        item.appendChild(itemVS);
        item.appendChild(itemPlayer2);
        document.getElementById('banner-phase-text').appendChild(item);
    })
}

export const announceMatch = (data) => {
    document.getElementById('game-announce-next-match').innerHTML = '';

    const   itemPlayer1 = document.createElement('div');
    const   itemPlayer2 = document.createElement('div');


    itemPlayer1.textContent = data[0];
    itemPlayer2.textContent = data[1];

    itemPlayer1.className = 'banner-user-name1';
    itemPlayer2.className = 'banner-user-name2';

    document.getElementById('game-announce-next-match').appendChild(itemPlayer1);
    document.getElementById('game-announce-next-match').innerHTML += '<img class="img-vs" src="img/vs.png" />';
    document.getElementById('game-announce-next-match').appendChild(itemPlayer2);
    
    currentPlayers = [data[0], data[1]];
    currentScore = [0, 0];
}

export const announceScore = () => {
    document.getElementById('score-container').innerHTML = '';
    document.getElementById('team-info-container1').innerHTML = '';
    document.getElementById('team-info-container2').innerHTML = '';
   
    const   score_home = document.createElement('span');
    const   score_away = document.createElement('span');
    const   player1 = document.createElement('span');
    const   player2 = document.createElement('span');

    score_home.textContent = currentScore[0] + ' ';
    score_away.textContent = ' ' + currentScore[1];
    player1.textContent = currentPlayers[0];
    player2.textContent = currentPlayers[1];

    score_home.className = 'score-home';
    score_away.className = 'score-away';
    player1.className = 'team-name-info';
    player2.className = 'team-name-info';

    document.getElementById('score-container').appendChild(score_home);
    document.getElementById('score-container').innerHTML += '<span class="custom-sep">-</span>';
    document.getElementById('score-container').appendChild(score_away);
    
    document.getElementById('team-info-container1').appendChild(player1);
    document.getElementById('team-info-container2').innerHTML += '<span class="team-icon-container"></span>';
    document.getElementById('team-info-container2').appendChild(player2);
}

export const announceWinner = (data) => {
    const   banner = document.getElementById('game-menu-banner-end')
    banner.innerHTML = "WINNER IS " + data;
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
        document.getElementById('game-menu-pause-text').innerHTML = "R E S U M E";
    } else {
        paused = false;
        document.getElementById('game-menu-pause-text').innerHTML = "P A U S E";
    }
    console.log('paused : ' + paused);
}

// game settings
let gameSettings = {
    bonused:"True",
    scoreToWin:"5",
    maxPlayer:"8",
}

export const updateSettings = (data) => {
    gameSettings.bonused = data.bonused;
    gameSettings.scoreToWin = data.scoreToWin;
    gameSettings.maxPlayer = data.maxPlayer;
    resetSettings();
}

const resetSettings = () => {
    setBonused();
    setScoreToWin();
    setMaxPlayer();
}

/*** event listener ****/
const sendCreate = (mode) => {
    console.log(status)
    gameSocket.send(JSON.stringify({'type': enu.Game.CREATE, 'mode':mode}));
    moveTo(enu.sceneIdx.CREATION);
    resetSettings();
} 

createMatch.addEventListener('click', () => {
    status = enu.gameMode.MATCH;
    sendCreate(enu.Game.MATCH)
});

createTournament.addEventListener('click', () => {
    status = enu.gameMode.TOURNAMENT;
    sendCreate(enu.Game.TRN)
});

createLocal.addEventListener('click', () => {
    status = enu.gameMode.LOCAL;
    sendCreate(enu.Game.LOCAL)
})

function getBonused() { return settingsSendBonus.checked; };
function getScoreToWin() { return settingsSendScore.value; };
function getMaxPlayer() { return settingsSendPlayer.value; };
function setBonused() {
    settingsSendBonus.checked = gameSettings.bonused;
};

function setScoreToWin() {
    settingsSendScore.value = gameSettings.scoreToWin;
    document.getElementById('scoreRangeOut').value = gameSettings.scoreToWin;
};

function setMaxPlayer() { 
    settingsSendPlayer.value = gameSettings.maxPlayer;
    document.getElementById('playersRangeOut').value = gameSettings.maxPlayer;
};

let updateRequested = [
    ["bonused", null, getBonused], 
    ["scoreToWin", null, getScoreToWin], 
    ["maxPlayer", null, getMaxPlayer]
];

settingsSendBonus.addEventListener('input', () => {
    prepRequest(0);
});

settingsSendScore.addEventListener('input', () => {
    prepRequest(1);
});

settingsSendPlayer.addEventListener('input', () => {
    prepRequest(2);
})

const prepRequest = (type) => {
    if (updateRequested[type][1] === null) {
        updateRequested[type][1] = setTimeout(requestUpdateSettings, 700, type);
    }
}

const requestUpdateSettings = (type) => {
    gameSocket.send(JSON.stringify({
        'type': enu.Game.SETTING,
         'message':{
            'param':updateRequested[type][0],
            'value':updateRequested[type][2](),
        }}));

    updateRequested[type][1] = null;
    console.log("settings: " + updateRequested[type][0] + ", update to: " + updateRequested[type][2]());
}

settingsReInit.addEventListener('click', () => {
    resetSettings();
    prepRequest(0);
    prepRequest(1);
    prepRequest(2);
})

start.addEventListener('click', () => {
    updateRequested.forEach((req, index) => {
        if (req[1] !== null) {
            clearTimeout(updateRequested)
            requestUpdateSettings(index)
            req[1] = null;
        }
    } )
    var message = {'type': enu.Game.START}
    if (status === enu.gameMode.LOCAL) message['players'] = players; 
    // if (status === enu.gameMode.MATCH) moveTo(enu.sceneIdx.MATCH);
    gameSocket.send(JSON.stringify(message));

})

const readyFunc = () => {
    if (status === enu.gameMode.LOCAL) {
        moveTo(enu.sceneIdx.MATCH);
        announceScore();
    };
    gameSocket.send(JSON.stringify({'type': enu.Game.READY}));
};

readyP.addEventListener('click', readyFunc);
ready.addEventListener('click', readyFunc);

pause.addEventListener('click', () => {
    if (locked === true) return ;
    gameSocket.send(JSON.stringify({'type': enu.Match.PAUSE}));
    togglePause();
    if (status === enu.gameMode.LOCAL) {
        if (gameData.timerInterval) {
            clearInterval(gameData.timerInterval);
            gameData.timerInterval = null;
        }
    }
});



const quitFunc = () => {
    updateRequested.forEach(req => {clearTimeout(req[1]);});
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
    gameSocket.send(JSON.stringify({'type': enu.Game.QUIT}));
    status = enu.gameMode.IDLE;
    if (idx === enu.sceneIdx.WELCOME) {
        fullClear()
        navigateTo("/");
    }
    moveTo(to);
};

document.querySelectorAll(".button-menu-quit").forEach(div => {div.addEventListener('click', quitFunc)});


nextMatch.addEventListener('click', () => {
    if (status === enu.gameMode.LOCAL) gameSocket.send(JSON.stringify({'type': enu.Game.NEXT}));
    else moveTo(enu.sceneIdx.PREMATCH)
})

document.getElementById('game-menu-local-input-button').addEventListener('click', () => {
    const   user = document.getElementById('game-menu-input-player').value;
    if (validate_name(user) === false) {
        console.warn("bad input: " + user);
        return ;
    }
    document.getElementById('game-menu-input-player').value = '';

    players.push(user);
    console.log(status)
    if (status === enu.gameMode.LOCAL) {
        createListLocal(user)
    } else {
        gameSocket.send(JSON.stringify({
            'type': enu.Game.INVITE,
            'user': user,
            'mode': (status === enu.gameMode.MATCH ? enu.Game.MATCH: enu.Game.TOURNAMENT),
        }));
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

document.addEventListener('DOMContentLoaded', function() {
    const video = document.querySelector('.video-background video');
    if (video) {
        video.src = 'img/menu_bg_vid.mp4'; 
        video.load();
    } else {
        console.error('Video element not found');
    }
});
