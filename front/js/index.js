import { logoutRequest, showHome } from "./home.js"
import { showProfile } from "./profile.js"
import {showSettings} from "./settings.js"
import {showChat} from "./chat.js"

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
    .then(response => {
        if (response.ok) {
            console.log("Je return true dans access")
            document.querySelector(".navbar").style.display = "flex"
            return true;
        } else {
            return fetch('auth/token/refresh/', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(refreshResponse => {
                if (refreshResponse.ok) {
                    document.querySelector(".navbar").style.display = "flex"
                    return true;
                } else {
                    logoutRequest();
                    return false;  
                }
            });
        }
    });
}

const router = async () => {
    console.log("Appel Router")
    const routes = [
        {path: "/", view:() => showHome() },
        {path: "/profile", view:() => showProfile()},
        {path: "/chat", view:() => showChat()},
        {path: "/settings", view:() => showSettings()},
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