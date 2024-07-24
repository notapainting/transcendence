import { initMenu } from './menu.js';
import { initGameWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearThree } from './game.js';
import { clearView, isUserAuthenticated, navigateTo } from "../index.js";
import { loggedInStatus, getPersInfo } from '../home.js';
import * as enu from './enums.js'

let flg2 = 0;
let flg3 = 0;

export const showGame = async () => {
    console.log("in show : rem")
    await isUserAuthenticated();
    const data = await getPersInfo();
    clearView();
    fullClear();
    loggedInStatus(data.profile_picture, data.username);
    initGameWebSocket(enu.backendPath.REMOTE);
    document.querySelector("body").style.backgroundColor = "#34A0A4"
    document.querySelector("#game").style.display = " block"
    setTimeout(()=> {
        document.querySelector("#game").style.opacity = "1";
    }, 200)
    initMenu(enu.backendPath.REMOTE);
}

export const showGameLocal  = async () => {
    console.log("in show : loc")

    clearView();
    fullClear();
    if (await isUserAuthenticated()){
        navigateTo("/");
        return ;
    }
    initGameWebSocket(enu.backendPath.LOCAL);
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
