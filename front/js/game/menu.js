import { navigateTo } from "../index.js"
import { gameSocket, clearGame, startMatch} from "./websocket.js"
import { fullClear } from './index.js';
import * as enu from './enums.js'
import { gameData } from './game.js';




const   start = document.getElementById('game-menu-start');
const   nextMatch = document.getElementById('game-menu-next');
const   settingsReInit = document.getElementById('settings-button-reinit');


const   menuM1 = document.getElementById('menu-m1-button');
const   menuM2a = document.getElementById('menu-m2a-button');
const   menuM2b = document.getElementById('menu-m2b');
const   menuM3 = document.getElementById('menu-m3');
const   menuM4 = document.getElementById('menu-m4');
const   menuM5 = document.getElementById('menu-m5');
const   menuM6 = document.getElementById('menu-m6');
const   menuM7 = document.getElementById('menu-m7');
const   menuM6_button = document.getElementById('menu-m6-button');


const   menuBgVid = document.getElementById('menu_bg_video');
const   menuBg = document.getElementById('menu-background');
const   menuBlurry = document.getElementById('blurry-background');


const   locContainerList = document.getElementById('game-menu-list-tournament');
const   locContainerSettings = document.getElementById('game-menu-settings');
const   settingsSendBonus = document.getElementById('bonusToggle');
const   settingsSendScore = document.getElementById('scoreRange');
const   settingsSendPlayer = document.getElementById('playersRange');




const   createMatch = document.getElementById('game-menu-fastGame');
const   createTournament = document.getElementById('game-menu-tournament');
const   createLocal = document.getElementById('game-menu-local');


const   invitationBox = document.getElementById('game-menu-invitationBox');


const   readyP = document.getElementById('game-menu-ready-prematch');


const   pause = document.getElementById('game-menu-pause');


/*** variable ****/


let     status = enu.gameMode.LOCAL;
let     anon = true;

export const changeGameStatus = (type) => {
    status = type;
}

export const getGameStatus = () => {
    return status;
}


let     idx = enu.sceneIdx.WELCOME;

export const getSceneIdx = () => {
    return idx;
}



let     players = [];


let     currentPlayers = [];
let     currentScore = [0, 0];
let     locked = false;
let     is_match = false;



const   scene = [
    [menuBg, menuBgVid, menuM1, invitationBox], 
    [menuBgVid, menuM2a, locContainerList, locContainerSettings], 
    [menuBgVid, menuM2b], 
    [menuBlurry, menuM3], 
    [menuBlurry, menuM4], 
    [menuM5], 
    [menuM6, menuM6_button], 
    [menuM7], 
    [], 
];





/*** initialisation ****/
export const initMenu = (path) => {
    status = enu.gameMode.LOCAL;
    activateAniM1()
    if (path === enu.backendPath.LOCAL) {
        anon = true;
        players = [];
        clearInvitationList();
        moveTo(enu.sceneIdx.CREATION);
    } else {
        anon = false;
        clearInvitationList();
        moveTo(enu.sceneIdx.WELCOME);
    }
    setTimeout(desactivateAniM1, 700);

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
    if (idx === enu.sceneIdx.WELCOME) {
        document.getElementById('game-menu-pause-text').innerHTML = "P A U S E";
        status = enu.gameMode.LOCAL;
    } else if (idx === enu.sceneIdx.CREATION) {
        players = [];
        clearGame();
        document.getElementById('bracket-disable-image').innerHTML = '';
    } else if(idx === enu.sceneIdx.END_TR) countDivsWithColumnClass();
    scene[idx].forEach(div => {div.style.display = "flex";});
    if (idx === enu.sceneIdx.END && status !== enu.gameMode.MATCH) menuM6_button.style.display = "flex";
}

/*** banner update ****/
export const updateScore = (data) => {
    currentScore = data.score;
    currentPlayers = data.players;
}

export const clearScore = () => {
    currentScore =[0,0]
}

export const announcePhase = (data) => {
    document.getElementById('banner-phase-text').innerHTML = '';
    let odd = 0;
    const column = document.createElement('div');
    column.className = "column";
    data.forEach((matchData) => {
        const   item = document.createElement('li');
        const   itemPlayer1 = document.createElement('div');
        const   itemPlayer2 = document.createElement('div');
        const   itemVS = document.createElement('div');

        const winnerTop = document.createElement('div');
        const winnerBottom = document.createElement('div');
        const matchTop = document.createElement('div');
        const matchBottom = document.createElement('div');
        const columnUserTop = document.createElement('span');
        const columnUserBottom = document.createElement('span');
    
        item.className = 'list-banner-element';
        itemPlayer1.textContent = matchData.host;
        itemPlayer2.textContent = matchData.guest;
        itemVS.textContent = 'vs';
        itemPlayer1.className = 'list-banner-user-name';
        itemPlayer2.className = 'list-banner-user-name';
        itemVS.className = 'list-banner-vs';

        columnUserTop.textContent = matchData.host;
        columnUserBottom.textContent = matchData.guest;
        columnUserTop.className = "name";
        columnUserBottom.className = "name";
        winnerTop.className = "match winner-top";
        winnerBottom.className = "match winner-bottom";
        matchTop.className = "match-top team";
        matchBottom.className = "match-bottom team";

        if (odd === 0)
        {
            winnerTop.appendChild(matchTop);
            winnerTop.appendChild(matchBottom);
            matchTop.appendChild(columnUserTop);
            matchBottom.appendChild(columnUserBottom);
            winnerTop.innerHTML += `
            </div>
            <div class="match-lines">
              <div class="line one"></div>
              <div class="line two"></div>
            </div>
            <div class="match-lines alt">
              <div class="line one"></div>
            </div> `;
            column.appendChild(winnerTop);
            odd = 1;
        }
        else {
            winnerBottom.appendChild(matchTop);
            winnerBottom.appendChild(matchBottom);
            matchTop.appendChild(columnUserTop);
            matchBottom.appendChild(columnUserBottom);
            winnerBottom.innerHTML += `
            </div>
            <div class="match-lines">
              <div class="line one"></div>
              <div class="line two"></div>
            </div>
            <div class="match-lines alt">
              <div class="line one"></div>
            </div> `;
            column.appendChild(winnerBottom);
            odd = 0;
        }
        
        item.appendChild(itemPlayer1);
        item.appendChild(itemVS);
        item.appendChild(itemPlayer2);
        document.getElementById('banner-phase-text').appendChild(item);
    })
    document.getElementById('bracket-disable-image').appendChild(column);
}

export const announceMatch = (data) => {
    document.getElementById('game-announce-next-match').innerHTML = '';

    const   itemPlayer1 = document.createElement('div');
    const   itemPlayer2 = document.createElement('div');


    itemPlayer1.textContent = data.host;
    itemPlayer2.textContent = data.guest;

    itemPlayer1.className = 'banner-user-name1';
    itemPlayer2.className = 'banner-user-name2';

    document.getElementById('game-announce-next-match').appendChild(itemPlayer1);
    document.getElementById('game-announce-next-match').innerHTML += '<img class="img-vs" src="img/vs.png" />';
    document.getElementById('game-announce-next-match').appendChild(itemPlayer2);
    
    currentPlayers = [data.host, data.guest];
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
    const   banner2 = document.getElementById('game-menu-banner-end2')
    banner.innerHTML = "Congratulations! Winner is " + data.winner;
    banner2.innerHTML = "Congratulations! Winner is " + data.winner;
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


export const toggleLock = () => {
    if (locked == false) locked = true;
    else if (locked == true) locked = false;
}

export const togglePause = (pause) => {
    if (pause === true) document.getElementById('game-menu-pause-text').innerHTML = "R E S U M E";
    else document.getElementById('game-menu-pause-text').innerHTML = "P A U S E";
}


let gameSettings = {
    bonused:"True",
    scoreToWin:"5",
    maxPlayer:"8",
}

export const updateSettings = (data) => {
    gameSettings.bonused = data.bonused;
    gameSettings.scoreToWin = data.scoreToWin;
    if (is_match === true) {
        gameSettings.maxPlayer = 2;
        setMaxPlayer(); 
    } else {
        gameSettings.maxPlayer = data.maxPlayer;
        setMaxPlayer();
    }
    setScoreToWin();
    setBonused();
}


const resetSettings = () => {
    gameSocket.send(JSON.stringify({'type':enu.Game.DEFAULT}))
}

/*** event listener ****/
const sendCreate = (mode) => {
    resetSettings();
    gameSocket.send(JSON.stringify({'type': enu.Game.CREATE, 'mode':mode}));
    moveTo(enu.sceneIdx.CREATION);
} 

createMatch.addEventListener('click', () => {
    status = enu.gameMode.MATCH;
    document.getElementById('playersRange').min = 2;
    document.getElementById('playersRange').disabled = true;
    is_match = true;
    document.getElementById('game-menu-list-players-title').innerText = "Fast Match";
    sendCreate(enu.Game.MATCH)
});

export const fastmatchOK = () => {
    if (status === enu.gameMode.TOURNAMENT) return false; 
    return true; 
}

export const   fastmatch = (user) => {
    if (status === enu.gameMode.TOURNAMENT) return false; 
    
    if (status === enu.gameMode.LOCAL) {
        status = enu.gameMode.MATCH;
        document.getElementById('playersRange').min = 2;
        document.getElementById('playersRange').disabled = true;
        is_match = true;
        document.getElementById('game-menu-list-players-title').innerText = "Fast Match";
        sendCreate(enu.Game.MATCH)
    }
    gameSocket.send(JSON.stringify({
        'type': enu.Game.INVITE,
        'user': user,
        'mode': enu.Game.MATCH,
    }));
    return true;
}

createTournament.addEventListener('click', () => {
    status = enu.gameMode.TOURNAMENT;
    document.getElementById('playersRange').min = 4;
    document.getElementById('playersRange').disabled = false;
    document.getElementById('game-menu-list-players-title').innerText = "Pong Tournament";
    is_match = false;
    sendCreate(enu.Game.TRN)
});

createLocal.addEventListener('click', () => {
    status = enu.gameMode.LOCAL;
    document.getElementById('playersRange').min = 2;
    document.getElementById('playersRange').disabled = false;
    document.getElementById('game-menu-list-players-title').innerText = "Local Tournament";
    is_match = false;
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
    }

settingsReInit.addEventListener('click', () => {
    resetSettings();
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
    
    gameSocket.send(JSON.stringify(message));
})

const readyFunc = () => {
    if (status === enu.gameMode.LOCAL) {
        moveTo(enu.sceneIdx.MATCH);
        announceScore();
        startMatch();
    };
    gameSocket.send(JSON.stringify({'type': enu.Game.READY}));
};

readyP.addEventListener('click', readyFunc);

pause.addEventListener('click', () => {
    if (locked === true) return ;
    gameSocket.send(JSON.stringify({'type': enu.Match.PAUSE}));
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
    document.getElementById('bracket-disable-image').innerHTML = '';
    if (anon === true) {
        if (idx == enu.sceneIdx.CREATION) {
            if (gameSocket !== null) gameSocket.close();
            fullClear()
            activateAniM1()
            navigateTo("/");
            return ;
        }
        var to = enu.sceneIdx.CREATION;
    } else var to = enu.sceneIdx.WELCOME;
    gameSocket.send(JSON.stringify({'type': enu.Game.QUIT}));
    status == enu.gameMode.LOCAL
    if (idx === enu.sceneIdx.WELCOME) {
        fullClear()
        activateAniM1()
        navigateTo("/");
    }
    moveTo(to);
};

document.querySelectorAll(".button-menu-quit").forEach(div => {div.addEventListener('click', quitFunc)});

nextMatch.addEventListener('click', () => {
    gameSocket.send(JSON.stringify({'type': enu.Game.NEXT}));
})


const addUser = () => {
    const user = document.getElementById('game-menu-input-player').value;
    const inputField = document.getElementById('game-menu-input-player');
    const errorMessage = document.getElementById('input-error-message');

    if (validate_name(user) === false) {
        console.warn("bad input: " + user);
        inputField.classList.add('input-error');
        errorMessage.textContent = 'Invalid player name';
        errorMessage.style.display = 'block';

        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 1000);

        setTimeout(() => {
            inputField.classList.remove('input-error');
        }, 500);


        return;
    }

    inputField.value = '';
    errorMessage.style.display = 'none';

    players.push(user);
    if (status === enu.gameMode.LOCAL) {
        createListLocal(user);
    } else {
        gameSocket.send(JSON.stringify({
            'type': enu.Game.INVITE,
            'user': user,
            'mode': (status === enu.gameMode.MATCH ? enu.Game.MATCH : enu.Game.TRN),
        }));
    }
}; 

document.getElementById('game-menu-local-input-button').addEventListener('click', addUser);
document.getElementById('playerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    addUser();
  
});

const createListLocal = (user) => {
    const   item = document.createElement('li');
    const   itemName = document.createElement('div');
    const   button = document.createElement('button');
    
    item.className = 'list-tournoi-element';
    itemName.textContent = user;
    itemName.className = 'list-tournoi-user-name';
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

function countDivsWithColumnClass() {
    const divs = document.querySelectorAll('div.column');

    if (divs.length === 1) {
        const bracketImage = document.getElementById('bracket-disable-image');
        if (bracketImage) {
            bracketImage.style.display = 'none';
        }
    }
    else {
        const bracketImage = document.getElementById('bracket-disable-image');
        if (bracketImage) {
            bracketImage.style.display = 'flex';
        }
    }
}




const activateAniM1 = () => {
    document.getElementById('game-menu-invitationBox').style.opacity = 0;
    document.getElementById('game-menu-invitationBox2').style.opacity = 0;
    document.getElementById('menu-m1-button').style.opacity = 0;
    document.getElementById('game-menu-invitationBox').animation = "fadeIn 0.5s ease-in-out forwards";
    document.getElementById('game-menu-invitationBox2').animation = "fadeIn 0.5s ease-in-out forwards";
    document.getElementById('menu-m1-button').animation = "fadeIn 0.5s ease-in-out forwards";
}

const desactivateAniM1 = () => {
    document.getElementById('game-menu-invitationBox').style.opacity = 1;
    document.getElementById('game-menu-invitationBox2').style.opacity = 1;
    document.getElementById('menu-m1-button').style.opacity = 1;
    document.getElementById('game-menu-invitationBox').animation = "none";
    document.getElementById('game-menu-invitationBox2').animation = "none";
    document.getElementById('menu-m1-button').animation = "none";
}
