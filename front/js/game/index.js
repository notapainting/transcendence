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
    document.querySelector("#game").style.display = "block";
    initMenu(path);
}

export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}