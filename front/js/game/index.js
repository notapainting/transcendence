import { clearMenu, initMenu } from './menu.js';
import { initGameWebSocket, clearGame } from './websocket.js';
import { clearScene } from './game.js';
import { clearThree } from './game.js';
import { clearView, isUserAuthenticated, navigateTo } from "../index.js";
import { loggedInStatus, getPersInfo } from '../home.js';
import * as enu from './enums.js'

const   transition = document.getElementById('menu-transition')


export const showGame = async () => {
    if (await isUserAuthenticated() === true) {
        try {
            const data = await getPersInfo();
            loggedInStatus(data.profile_picture, data.username);
        }
        catch (error){
            navigateTo("/");
            return
        }
        document.title = "bill | game";
        transitionToGame(enu.backendPath.REMOTE);
    } else {
        navigateTo("/");
    };
}

export const showGameLocal  = async () => {
    if (await isUserAuthenticated()){
        navigateTo("/");
        return ;
    }
    document.title = "bill | game";
    transitionToGame(enu.backendPath.LOCAL);
}

const transitionToGame = (path) => {
    clearView();
    fullClear();
    if (path === enu.backendPath.LOCAL) initGameWebSocket(path);
    document.querySelector("body").style.backgroundColor = "#34A0A4"
    document.querySelector("#game").style.display = " block"
    setTimeout(()=> {
        document.querySelector("#game").style.opacity = "1";
    }, 200)
    clearMenu();
    transition.style.display = 'flex';
    transition.style.backgroundPosition = 'center top';
    setTimeout(initMenu, 2000, path);
}

export const fullClear = () => {
    clearScene();
    clearGame();
    clearThree();
}
