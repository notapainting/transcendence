import { initMenu } from './menu.js';
import { initWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearThree } from './game.js';
import { clearView } from "../index.js";
import * as enu from './enums.js'


export const showGame = () => {initGame(enu.backendPath.REMOTE);}

export const showGameLocal = () => {initGame(enu.backendPath.LOCAL);}

const initGame = (path) => {
    clearView();
    fullClear();
    initWebSocket(path);
    document.querySelector("body").style.backgroundColor = "#34A0A4"
    document.querySelector("#game").style.display = " block"
    setTimeout(()=> {
        document.querySelector("#game").style.opacity = "1";
    }, 200)
    initMenu(path);
}

export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}