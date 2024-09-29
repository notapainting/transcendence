import { navigateTo, whoIam } from "./index.js";
import { clearView, isUserAuthenticated } from "./index.js";
import { fetchUsers, initializeWebSocket, showChat } from "./chat.js";

export const getPersInfo = () => {
    return fetch('/auth/get_pers_infos/', {
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
}

const parallaxEffect = (event) => {
    const backThrees = document.querySelector('.back-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');
    const titleSite = document.querySelector('.title-site');

    const maxOffsetX = 75; 
    const maxOffsetY = 75; 

    let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
    let yAxis = (window.innerHeight / 2 - event.pageY) / 10;

    
    yAxis = Math.min(Math.max(yAxis, -maxOffsetY), maxOffsetY);

    backThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.2}px) calc(50% + ${yAxis * 0.2}px)`;
    middleThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.4}px) calc(50% + ${yAxis * 0.4}px)`;
    frontThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.9}px) calc(50% + ${yAxis * 0.9}px)`;
    titleSite.style.backgroundPosition = `calc(50% + ${xAxis * 1.4}px) calc(50% + ${yAxis * 1.4}px)`;
}

function authenticateWith42() {
    fetch('auth/authenticate_with_42/', {
        method: 'GET',
        redirect: 'follow'
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        const authorizationUrl = data.authorization_url;
        window.location.href = authorizationUrl;
    })
    .catch(error => {
    });
}

let isScrolling = false;



const scrollUpEffect = (event, path) => {
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
    const titleSite = document.querySelector('.title-site');
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
                        titleSite.style.transform = `translateY(-${zoomFactor * 200}px)`;
                        titleSite.style.opacity = "0"
                        break;
                    case 1:
                        document.querySelectorAll(".banner").forEach(x => x.style.opacity = "0")
                        backThrees.style.transform = `scale(${zoomFactor})`;
                        backgroundThrees.style.filter = 'blur(2px)';
                        middleThrees.style.transform = `scale(${zoomFactor * 2})`;
                        frontThrees.style.transform = `scale(${zoomFactor * 3})`;
                        frontThrees.style.opacity = "0"
                        titleSite.style.opacity = "0"
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
                            navigateTo(path);
                         }, 800);

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

const playBtnElement = document.querySelector(".play-btn");

const playOfflineEvent = (event) => {
    scrollUpEffect(event, "/local");
}

const playOnlineEvent = (event) => {
    scrollUpEffect(event, "/play");
}

playBtnElement.addEventListener("click", playOfflineEvent);

const messageBox = document.querySelector(".message-box");

export const loggedInStatus = (profile_picture, username) => {
    document.querySelector(".login-signin-form").style.display = "none"
    playBtnElement.removeEventListener("click", playOfflineEvent);
    playBtnElement.addEventListener("click", playOnlineEvent);
    
    
    
    showChat();
    
    document.querySelector(".profile-picture-home").style.backgroundImage = `url('${profile_picture}')`
    document.querySelector(".navbar").style.display= "flex"
}

const twoFactorDisplay = document.querySelector(".two-factor-display");
const twoFactorContainerLogin = document.querySelector(".two-factor-container-login");
const login2faButton = document.querySelector(".login-2fa")

const closeTwoFactorLogin = (event) => {
    login2faButton.removeEventListener("click", loginRequest);
    twoFactorContainerLogin.style.transform = "scale(0)"
    setTimeout(()=> {
            twoFactorDisplay.style.display = "none"
    }, 200)
}


const displayTwoFactorLogin = async ()  => {
    twoFactorDisplay.style.display = "flex"
    setTimeout(()=> {
        twoFactorContainerLogin.style.transform = "scale(1)"
    }, 200)
    login2faButton.removeEventListener("click", loginRequest);
    login2faButton.addEventListener("click", loginRequest);
}


const loginRequest = (event) => {
    const dataSend = {
        username: homeEmailUsernameInput.value,
        password: homePasswordInput.value
    };
    const input2FaLoginValue = document.querySelector(".input-f2a-login").value;
    if (input2FaLoginValue) {
        dataSend.code = input2FaLoginValue;
    }
    fetch('/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataSend)
    })
    .then(response => {
        if (response.ok){
            closeTwoFactorLogin();
            return response.json();
        } else if (response.status === 403) {

            return response.json().then(data => {
                                messageBox.style.backgroundColor = "#f44336";
                if (data === 'Two Factor Authentification needed.') {
                                        displayTwoFactorLogin();
                }
                else {
                    messageBox.innerHTML = `Username / e-mail or password incorrect.<span class="closebtn" onclick="this.parentElement.style.transform='scale(0)';">&times;</span>`
                    messageBox.style.transform = "scale(1)";
                }
            });
        } else {
                        messageBox.style.backgroundColor = "#f44336";
            messageBox.innerHTML = `Invalid field, please retry.<span class="closebtn" onclick="this.parentElement.style.transform='scale(0)';">&times;</span>`
            messageBox.style.transform = "scale(1)";
        }
    })
    .then(data => {
        loggedInStatus(data.profile_picture, data.username);
        var buttonLogout = document.querySelector('.menu-logout');
        var buttonSettings = document.querySelector('.menu-settings');
        buttonLogout.removeAttribute('disabled');
        buttonSettings.removeAttribute('disabled');
        buttonLogout.classList.add('clickable');
        buttonSettings.classList.add('clickable');
    })  
    .catch(error => {
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
            messageBox.style.backgroundColor = "#f44336";
            return response.json().then(data => {
                                if (data.password)
                    data.password = "Password too short, min. 8 characters";
                if (data.email === "This field must be unique")
                    data.email = "E-mail incorrect or already used"
                messageBox.innerHTML = `${data.email || data.username || data.password}<span class="closebtn" onclick="this.parentElement.style.transform='scale(0)';">&times;</span>`
                messageBox.style.transform = "scale(1)";
            });
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
    zoomFactor = Math.max(1, Math.min(10, zoomFactor)); 
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
        isZooming = false; 
    }, 400); 
    
};

export const loggedOutStatus = () => {
    document.querySelector(".login-signin-form").style.display = "flex"
    playBtnElement.removeEventListener("click", playOfflineEvent);
    playBtnElement.addEventListener("click", playOnlineEvent);
    document.querySelector(".bubble").style.display = "none";
    document.querySelector(".chatbox").style.display = "none";
    document.querySelector(".navbar").style.display= "none";
}

export let logoutRequest = (event) => {
    event.preventDefault();
    fetch('/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            loggedOutStatus();
            navigateTo("/");
        } else {
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

const smoothSroll = (event) => {

    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
    document.removeEventListener('wheel', scrollDownEffect);
    document.addEventListener('wheel', adjustZoom);
}

export const showHome = async () => {
    clearView();
    document.title = "bill | home";
    let isAuthenticated = await isUserAuthenticated();
    const homeElement = document.querySelector("#home");
    homeElement.style.display = "block";
    const personData = await fetchUsers(whoIam);
    if (isAuthenticated)
    {
        loggedInStatus(personData.profile_picture, personData.username);
        var buttonLogout = document.querySelector('.menu-logout');
        var buttonSettings = document.querySelector('.menu-settings');
        buttonLogout.removeAttribute('disabled');
        buttonSettings.removeAttribute('disabled');
        buttonLogout.classList.add('clickable');
        buttonSettings.classList.add('clickable');
    }
    document.removeEventListener('mousemove', parallaxEffect);
    document.removeEventListener('wheel', scrollDownEffect);
    document.addEventListener('mousemove', parallaxEffect);
    document.addEventListener('wheel', scrollDownEffect);
    document.removeEventListener("click", switchForm);
    document.addEventListener("click", switchForm);
    document.querySelector(".close-two-factor-login").removeEventListener("click", closeTwoFactorLogin)
    homeFormButton.removeEventListener("click", loginOrRegisterRequest)
    document.querySelector(".login-42").removeEventListener('click', authenticateWith42);
    document.querySelector(".close-two-factor-login").addEventListener("click", closeTwoFactorLogin)
    homeFormButton.addEventListener("click", loginOrRegisterRequest)
    document.querySelector(".login-42").addEventListener('click', authenticateWith42);
} 
