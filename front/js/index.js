import { showHome, parallaxEffect } from './Home.js';

const navigateTo = url => {
    history.pushState(null, null, url)
    router()
}

const showGame = () => {
    const headerBgElement = document.querySelector(".header-bg");
    headerBgElement.style.transform = "translateY(-200px)";

    document.querySelector("#Game").style.display = "block";
    document.querySelector("body").style.backgroundColor = "#FFCC00"
    const soloElement = document.querySelector(".solo");
    const multiElement = document.querySelector(".multi");
    soloElement.style.opacity = "0";
    multiElement.style.opacity = "0";
    setTimeout(() => {
        headerBgElement.style.transform = "translateY(0px)";
    }, 10); 
    setTimeout(() => {
        soloElement.style.opacity = "1";
    }, 500); 
    setTimeout(() => {
        multiElement.style.opacity = "1";
    }, 1000); 

};

const showProfile = () => {
    document.querySelector("#Profile").style.display = "block";
    // Ici, vous pouvez ajouter des manipulations supplémentaires spécifiques à la vue des paramètres
};

const showSettings = () => {
    document.querySelector("#Settings").style.display = "block";
    // Ici, vous pouvez ajouter des manipulations supplémentaires spécifiques à la vue des paramètres
};

const clearView = () => {
    document.querySelectorAll(".view").forEach(div => {
        div.style.display = "none";
    });
    document.removeEventListener('mousemove', parallaxEffect);
}

const router = async () => {
    const routes = [
        {path: "/", view:() => showHome() },
        {path: "/game", view:() => showGame()},
        {path: "/profile", view:() => showProfile()},
        {path: "/settings", view:() => showSettings()},
    ];
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: window.location.pathname === route.path ? true : false
        };
    })
    let match = potentialMatches.find(potentialMatches => potentialMatches.isMatch === true)
    console.log(match)
    if (!match){
        match = {
            route: routes[0],
            isMatch: true
        }
    }
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