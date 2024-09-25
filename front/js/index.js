import { logoutRequest, showHome } from "./home.js"
import { showProfile, showHistory } from "./profile.js"

import { showGame, showGameLocal } from "./game/index.js"
export let whoIam;


export const navigateTo = url => {
    history.pushState(null, null, url);
    router()
}

export const clearView = () => {
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
                        return true;
        } else {
            return fetch('auth/token/refresh/', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(refreshResponse => refreshResponse.json().then(refreshData => {
                if (refreshResponse.ok) {
                    whoIam = refreshData.username;  // Stocker le username
                                        return true;
                } else {
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

function resetHomePage() {
    const backThrees = document.querySelector('.back-threes');
    const backgroundThrees = document.querySelector('.background-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');
    
    backThrees.style.transform = 'scale(1)';
    backgroundThrees.style.filter = 'blur(0px)';
    middleThrees.style.transform = 'scale(1)';
    frontThrees.style.transform = 'scale(1)';
    
    document.querySelectorAll(".banner").forEach(x => x.style.opacity = "1");
    frontThrees.style.opacity = "1";
    middleThrees.style.opacity = "1";
    backThrees.style.opacity = "1";

    document.querySelector("#game").style.display = " none"
    document.querySelector("#game").style.opacity = "0";
}


const router = async () => {
    if (window.location.pathname === '/') { 
        resetHomePage();
    }
    const routes = [
        {path: "/", view:() => showHome() },
        {path: "/profile", view:() => showProfile()},
        {path: "/history", view:() => showHistory()},
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

const profileTargetContainer = document.querySelector(".profile-target-info");
const profileTargetDisplay = document.querySelector(".target-profile-display");

const closeProfileDisplay = (event) => {
    profileTargetContainer.style.transform = "scale(0)"
    setTimeout(()=> {
            profileTargetDisplay.style.display = "none"
    }, 200)
}

export let permissionNotification = null;


document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener('click', e => {
        if (e.target.matches("[data-link]")){
            e.preventDefault();
            navigateTo(e.target.dataset.href);
        }
    });
    const logoutButton = document.querySelector(".fa-right-from-bracket");
    const logoutButtonMenu = document.querySelector(".menu-logout");
    document.querySelector(".close-profile-display").addEventListener("click", closeProfileDisplay);
    logoutButton.addEventListener("click", logoutRequest);
    logoutButtonMenu.addEventListener("click", logoutRequest);
    const notificationContainer = document.querySelector(".notification-container");
    if ("Notification" in window) {
        // Demande la permission à l'utilisateur
        Notification.requestPermission().then(permission => {
            permissionNotification = permission;
        });
      }
    document.querySelectorAll('.profile-menu-quit').forEach(elem => elem.addEventListener('click', () => {
        navigateTo('/')
    }));

    document.querySelector(".fa-bell").addEventListener('click', () => {
        const currentDisplay = window.getComputedStyle(notificationContainer).display;
        if (currentDisplay === 'flex') {
            notificationContainer.style.display = "none";
        } else {
            notificationContainer.style.display = "flex";
        }
    })
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

