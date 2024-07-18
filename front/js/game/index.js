import { initMenu } from './menu.js';
import { initGameWebSocket, initLocalGameWebSocket, clearGame } from './websocket.js';
import { clearScene } from './utils.js';
import { clearThree } from './game.js';
import { clearView } from "../index.js";
import { loggedInStatus } from '../home.js';
import { isUserAuthenticated } from '../index.js';
import * as enu from './enums.js'

let flg2 = 0;
let flg3 = 0;

export const showGame = async () => {
    await isUserAuthenticated();
    fetch('/auth/get_pers_infos/', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else {
            throw new Error("Unauthorized");
        }
    })
    .then(data => {
        clearView();
        fullClear();
        loggedInStatus(data.profile_picture, data.username);
        if (!flg3)
            initGameWebSocket();
        flg3 = 1;
        document.querySelector("body").style.backgroundColor = "#34A0A4"
        document.querySelector("#game").style.display = " block"
        setTimeout(()=> {
            document.querySelector("#game").style.opacity = "1";
        }, 200)
        initMenu(enu.backendPath.LOCAL);
    })
}

export const showGameLocal  = async () => {
    await isUserAuthenticated();
    fetch('/auth/get_pers_infos/', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else {
            throw new Error("Unauthorized");
        }
    })
    .then(data => {
        clearView();
        fullClear();
        loggedInStatus(data.profile_picture, data.username);
        if (!flg2)
            initLocalGameWebSocket();
        flg2 = 1;
        document.querySelector("body").style.backgroundColor = "#34A0A4"
        document.querySelector("#game").style.display = " block"
        setTimeout(()=> {
            document.querySelector("#game").style.opacity = "1";
        }, 200)
        initMenu(enu.backendPath.LOCAL);
    })
}



export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}
