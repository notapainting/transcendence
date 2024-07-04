import { moveTo } from './menu.js';
import { initWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearThree } from './game.js';
import { clearView } from "../index.js";
import * as enu from './enums.js'


export const showGame = () => {initGame("/game/");}

export const showGameLocal = () => {initGame("/game/local/");}

const initGame = (path) => {
    fullClear();
    initWebSocket(path);
    document.querySelector("#game").style.display = "block"
    moveTo(enu.sceneIdx.WELCOME);
}

export const fullClear = () => {
    clearScene();
    clearGame();
    clearView();
    clearThree();
}