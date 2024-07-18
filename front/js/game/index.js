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
    document.querySelector("body").style.backgroundColor = "#34A0A4"
    document.querySelector("#game").style.display = " block"
    setTimeout(()=> {
        document.querySelector("#game").style.opacity = "1";
    }, 200)
    initMenu(enu.backendPath.REMOTE);
    
}

export const showGameLocal = () => {
    clearView();
    fullClear();
    initLocalGameWebSocket();
    document.querySelector("body").style.backgroundColor = "#34A0A4"
    document.querySelector("#game").style.display = " block"
    setTimeout(()=> {
        document.querySelector("#game").style.opacity = "1";
    }, 200)
    initMenu(enu.backendPath.LOCAL);
}



export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}
