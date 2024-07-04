import { moveTo } from './menu.js';
import { initWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearView } from "../index.js";
import * as enu from './enums.js'


export const showGame = () => {initGame("/game/");}

export const showGameLocal = () => {initGame("/game/local/");}

const initGame = (path) => {
    clearScene();
    clearGame();
    clearView();
    initWebSocket(path);
    document.querySelector("#game").style.display = "block"
    moveTo(enu.sceneIdx.WELCOME);
}

