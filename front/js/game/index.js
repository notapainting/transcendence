import { initMenu } from './menu.js';
import { initGameWebSocket, initLocalGameWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearThree } from './game.js';
import { clearView } from "../index.js";
import * as enu from './enums.js'


export const showGame = () => {
    clearView();
    fullClear();
    initGameWebSocket()
    document.querySelector("#game").style.display = "block";
    initMenu(enu.backendPath.REMOTE);
    
}

export const showGameLocal = () => {
    clearView();
    fullClear();
    initLocalGameWebSocket();
    document.querySelector("#game").style.display = "block";
    initMenu(enu.backendPath.LOCAL);
}



export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}
