import { navigateTo } from "./index.js";

const parallaxEffect = (event) => {
    const backThrees = document.querySelector('.back-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');

    const maxOffsetX = 75; 
    const maxOffsetY = 75; 

    let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
    let yAxis = (window.innerHeight / 2 - event.pageY) / 10;

    // xAxis = Math.min(Math.max(xAxis, -maxOffsetX), maxOffsetX);
    yAxis = Math.min(Math.max(yAxis, -maxOffsetY), maxOffsetY);

    backThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.2}px) calc(50% + ${yAxis * 0.2}px)`;
    middleThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.4}px) calc(50% + ${yAxis * 0.4}px)`;
    frontThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.9}px) calc(50% + ${yAxis * 0.9}px)`;
}
let isScrolling = false;

const scrollUpEffect = (event) => {
    document.removeEventListener('wheel', scrollDownEffect);
    event.preventDefault();
    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
    let zoomFactor = 1; 
    const backThrees = document.querySelector('.back-threes');
    const backgroundThrees = document.querySelector('.background-threes')
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');
    setTimeout(() => {
        for (let i = 0; i < 4; i++){
            setTimeout(() => {
                const zoomIntensity = 0.5;
                zoomFactor += zoomIntensity;
                zoomFactor = Math.max(1, Math.min(10, zoomFactor));
    
                switch (i){
                    case 0:
                        backgroundThrees.style.filter = 'blur(3px)';
                        backThrees.style.transform = `scale(${zoomFactor * 0.8})`;
                        middleThrees.style.transform = `scale(${zoomFactor * 1})`;
                        frontThrees.style.transform = `scale(${zoomFactor * 2})`;
                        break;
                    case 1:
                        document.querySelectorAll(".banner").forEach(x => x.style.opacity = "0")
                        backThrees.style.transform = `scale(${zoomFactor})`;
                        backgroundThrees.style.filter = 'blur(2px)';
                        middleThrees.style.transform = `scale(${zoomFactor * 2})`;
                        frontThrees.style.transform = `scale(${zoomFactor * 3})`;
                        frontThrees.style.opacity = "0"
                        break;
                    case 2:
                        backThrees.style.transform = `scale(${zoomFactor * 2})`;
                        middleThrees.style.transform = `scale(${zoomFactor * 3})`;
                        backgroundThrees.style.filter = 'blur(1px)';
                        middleThrees.style.opacity = "0"
                        break;
                    case 3:
                        backThrees.style.transform = `scale(${zoomFactor * 3})`;
                        backgroundThrees.style.filter = 'blur(0px)';
                        backThrees.style.opacity = "0";
                }
            }, i * 180);
        }
    }, 500)
}


const scrollDownEffect = (event) => {
    if (isScrolling)
        return ;
    isScrolling = true;
    const delta = Math.sign(event.deltaY);
    const separatorPosition = document.querySelector('.home-sep').getBoundingClientRect().top + window.pageYOffset;
    if (window.pageYOffset >= separatorPosition && delta > 0) {
        isScrolling = false;
        return;
    }
    window.scrollBy({
        top: delta * separatorPosition,
        behavior: "smooth",
    })
    setTimeout(() => {
        isScrolling = false;
    }, 900); 
}

let isLoginForm = true;
let homeFormButton = document.querySelector(".home-form-btn");
let loginOrSigninText = document.querySelector(".login-or-register-text");
let homeEmailInput = document.querySelector("#home-email");
let homeAccept = document.querySelector(".accept");
let homeEmailUsernameInput = document.querySelector("#home-username")
let homePasswordInput = document.querySelector("#home-password")


const switchToLoginForm = () => {
    homeEmailInput.style.transform = "scale(0)";
    setTimeout(()=> {
        homeAccept.style.transform = "scale(0)"
        homeEmailUsernameInput.placeholder = "username / e-mail"
        homeFormButton.innerHTML = "LOGIN";
    }, 200)
    loginOrSigninText.innerHTML = `Don't have an account ? <br><span class="switch-form">Create One</span>`;
}

const switchToRegisterForm = () => {
    homeEmailInput.style.transform = "scale(1)";
    setTimeout(()=> {
        homeAccept.style.transform = "scale(1)"
        homeEmailUsernameInput.placeholder = "username"
        homeFormButton.innerHTML = "REGISTER";
    }, 200)

    loginOrSigninText.innerHTML = `Have an account ? <br><span class="switch-form">Login</span>`;
}

const switchForm = (event) => {
    const switchFormLink = event.target.closest(".switch-form");
    if (switchFormLink) {
        if (switchFormLink.textContent === "Create One") {
            isLoginForm = false;
            switchToRegisterForm();
        } else {
            isLoginForm = true;
            switchToLoginForm();
        }
    }
}

const messageBox = document.querySelector(".message-box");

const loggedInStatus = () => {
    document.querySelector(".navbar").style.display= "flex"
    document.querySelector(".login-signin-form").style.display = "none"
    document.querySelector(".play-online-btn").style.display = "block"
    setTimeout(()=> {
        document.querySelector(".play-online-btn").style.transform = "scale(1)"
    }, 100)
}

const loginRequest = (event) => {
    const dataSend = {
        username: homeEmailUsernameInput.value,
        password: homePasswordInput.value
    };
    console.log(dataSend.username)
    console.log(dataSend.password)
    fetch('/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataSend)
    })
    .then(response => {
        if (response.ok){

            loggedInStatus();
            return response.json();
        }
        else {
            messageBox.style.backgroundColor = "#f44336";
            messageBox.innerHTML = `Username / e-mail or password incorrect.<span class="closebtn" onclick="this.parentElement.style.transform='scale(0)';">&times;</span>`
            messageBox.style.transform = "scale(1)";
        }
    })
    .then(data => {
        // loggedInStatus(data);
    })  
    .catch(error => {
        console.log("Login Error:", error.message);
    })
}

const registerRequest = (event) => {
    const dataSend = {
        email: homeEmailInput.value,
        username: homeEmailUsernameInput.value,
        password: homePasswordInput.value
    };
    fetch('/auth/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataSend)
    })
    .then(response => {
        if (response.ok){
            messageBox.style.backgroundColor = "#36B985";
            messageBox.innerHTML = `An link have been send to your e-mail address<br> please check you mailbox.<span class="closebtn" onclick="this.parentElement.style.transform='scale(0)';">&times;</span>`
            messageBox.style.transform = "scale(1)";
            return response.json();
        }
        else {
            console.log("IL Y A UNE ERREUR");
            throw new Error("Identifiant ou mot de passe incorrect");
        }
    })
    .then(data => {
    })  
    .catch(error => {
    })
}

const loginOrRegisterRequest = (event) => {
    event.preventDefault();
    if (isLoginForm)
        loginRequest();
    else
        registerRequest();
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
let isZooming = false;
let indexZoom = 0;
let zoomFactor = 1;
const adjustZoom = (event) => {
    if (isZooming) return;
    isZooming = true;
    
    const zoomIntensity = 0.5;
    if (event.deltaY < 0) {
        zoomFactor += zoomIntensity;
    }
    else {
        isZooming = false;
        return ;
    }
    zoomFactor = Math.max(1, Math.min(10, zoomFactor)); // Limiter le zoom entre 0.5x et 2x
    document.querySelectorAll(".banner").forEach(x => x.style.opacity = "0")
    const backThrees = document.querySelector('.back-threes');
    const backgroundThrees = document.querySelector('.background-threes')
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');
    switch (indexZoom){
        case 0:
            backgroundThrees.style.filter = 'blur(3px)';
            backThrees.style.transform = `scale(${zoomFactor * 0.8})`;
            middleThrees.style.transform = `scale(${zoomFactor * 1})`;
            frontThrees.style.transform = `scale(${zoomFactor * 2})`;
            break;
        case 1:
            backThrees.style.transform = `scale(${zoomFactor})`;
            backgroundThrees.style.filter = 'blur(2px)';
            middleThrees.style.transform = `scale(${zoomFactor * 2})`;
            frontThrees.style.transform = `scale(${zoomFactor * 3})`;
            frontThrees.style.opacity = "0"
            break;
        case 2:
            backThrees.style.transform = `scale(${zoomFactor * 2})`;
            middleThrees.style.transform = `scale(${zoomFactor * 3})`;
            backgroundThrees.style.filter = 'blur(1px)';
            middleThrees.style.opacity = "0"
            break;
        case 3:
            backThrees.style.transform = `scale(${zoomFactor * 3})`;
            backgroundThrees.style.filter = 'blur(0px)';
            backThrees.style.opacity = "0";
    
            setTimeout(() => {
               document.querySelectorAll(".parallax-items").forEach(x => x.style.display = "none")
            }, 800);
    }
    indexZoom++;
    setTimeout(() => {
        isZooming = false; // Réinitialiser l'indicateur après 2 secondes
    }, 400); // Attendre 2 secondes avant de permettre un autre événement wheel
};

export let logoutRequest = (event) => {
    fetch('/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            navigateTo("/");
            window.location.reload();
            // Effectuez ici les actions nécessaires après la déconnexion, par exemple rediriger l'utilisateur vers une autre page
        } else {
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}
import { clearView } from "./index.js";
export const showHome = async () => {


    let isAuthenticated = await isUserAuthenticated();
    clearView();
    const homeElement = document.querySelector("#home");
    homeElement.style.display = "block";

    if (isAuthenticated)
        loggedInStatus();
    const playOfflineBtnElement = document.querySelector(".play-offline-btn");
    const playOnlineBtnElement = document.querySelector(".play-online-btn");
    document.addEventListener('mousemove', parallaxEffect);
    document.addEventListener('wheel', scrollDownEffect);
    playOfflineBtnElement.addEventListener("click", scrollUpEffect)
    playOnlineBtnElement.addEventListener("click", event => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
        document.removeEventListener('wheel', scrollDownEffect);
        document.addEventListener('wheel', adjustZoom);
    })
    document.addEventListener("click", switchForm);
    homeFormButton.addEventListener("click", loginOrRegisterRequest)
    const logoutButton = document.querySelector(".fa-right-from-bracket");
    logoutButton.addEventListener("click", logoutRequest);
} 