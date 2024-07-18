import { logoutRequest, showHome } from "./home.js"
import { showProfile } from "./profile.js"

import {showSettings} from "./settings.js"
import { loggedInStatus } from "./home.js";
import { showGame, showGameLocal } from "./game/index.js"
export let whoIam;


export const navigateTo = url => {
    history.pushState(null, null, url)
    router()
}

export const clearView = () => {
console.log("Appel ClearView")
    document.querySelectorAll(".view").forEach(div => {
        div.style.display = "none";
    });
}

export const isUserAuthenticated = () => {
    return fetch('auth/validate_token/', {
        method: 'POST',
        credentials: 'same-origin'
    })
    .then(response => response.json().then(data => {
        if (response.ok) {
            whoIam = data.username; 
            console.log("Je return true dans access");
            return true;
        } else {
            return fetch('auth/token/refresh/', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(refreshResponse => refreshResponse.json().then(refreshData => {
                if (refreshResponse.ok) {
                    whoIam = refreshData.username;  // Stocker le username
                    console.log("Je return true dans refresh");
                    return true;
                } else {
                    console.log("Je return false dans refresh");
                    return false;  
                }
            }));
        }
    }))
    .catch(error => {
        console.error("Error during authentication process:", error);
        return false;
    });
};

const router = async () => {
    console.log("Appel Router")
    const routes = [
        {path: "/", view:() => showHome() },
        {path: "/profile", view:() => showProfile()},
        {path: "/settings", view:() => showSettings()},
        {path: "/play", view:() => showGame()},
        {path: "/local", view:() => showGameLocal()},
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
    match.route.view()
};

window.addEventListener("popstate", router);


document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener('click', e => {
        if (e.target.matches("[data-link]")){
            e.preventDefault();
            navigateTo(e.target.dataset.href);
        }
    });
    const logoutButton = document.querySelector(".fa-right-from-bracket");
    logoutButton.addEventListener("click", logoutRequest);
    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
    router();
});

// document.addEventListener("DOMContentLoaded", () => {
//     document.addEventListener('click', e => {
//         if (e.target.matches("[data-link]")){
//             e.preventDefault();
//             navigateTo(e.target.href)
//         }
//     })
//     document.querySelector(".login-signin-form").addEventListener("submit", event => {
//         event.preventDefault();
//     })
//     router();
// })