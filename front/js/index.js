import { showHome, parallaxEffect } from './Home.js';
import { showGame } from './Game.js';
import { showProfile } from './Profile.js';
import { showSettings } from './Settings.js';
import { showSignin, sendData } from './Signin.js';

const navigateTo = url => {
    history.pushState(null, null, url)
    router()
}

const clearView = () => {
    document.querySelectorAll(".view").forEach(div => {
        div.style.display = "none";
    });
    document.removeEventListener('mousemove', parallaxEffect);
}

const isUserAuthenticated = () => {
    return fetch('auth/validate_token/', {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            console.log("Je return true dans access")
            return true;
        } else {
            return fetch('auth/token/refresh/', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(refreshResponse => {
                if (refreshResponse.ok) {
                    console.log("Je return true dans refresh")
                    return true;
                } else {
                    console.log("Je return false dans refresh")
                    return false;  
                }
            });
        }
    });
}

const router = async () => {
    const routes = [
        {path: "/", view:() => showHome() },
        {path: "/game", view:() => showGame()},
        {path: "/profile", view:() => showProfile()},
        {path: "/settings", view:() => showSettings()},
        {path: "/signin", view:() => showSignin()},
    ];
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: window.location.pathname === route.path ? true : false
        };
    })
    let match = potentialMatches.find(potentialMatches => potentialMatches.isMatch === true)
    if (!match){
        match = {
            route: routes[0],
            isMatch: true
        }
    }
    if (match.route.path === "/profile"){
        console.log("yooo")
        const isAuthenticated = await isUserAuthenticated();
        if (!isAuthenticated){
            console.log("hello")
            match = {
                route: routes[4],
                isMatch: true
            }
        }
    }
    history.pushState(null, null, match.route.path)
    clearView();
    match.route.view();
};

window.addEventListener("popstate", router);

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener('click', e => {
        if (e.target.matches("[data-link]")){
            e.preventDefault();
            navigateTo(e.target.href)
        }
    })
    router();
})