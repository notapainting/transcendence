import { isUserAuthenticated, navigateTo} from "./index.js";
        // export const parallaxEffect = (event) => {
    //     const backThrees = document.querySelector('.back-threes');
    //     const middleThrees = document.querySelector('.middle-threes');
    //     const frontThrees = document.querySelector('.front-threes');

    //     let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
    //     let yAxis = (window.innerHeight / 2 - event.pageY) / 10;

    //     backThrees.style.transform = `translate3d(${xAxis * 0.2}px, ${yAxis * 0.2}px, 0)`;
    // middleThrees.style.transform = `translate3d(${xAxis * 0.4}px, ${yAxis * 0.4}px, 0)`;
    // frontThrees.style.transform = `translate3d(${xAxis * 0.9}px, ${yAxis * 0.9}px, 0)`;
    // }

export const parallaxEffect = (event) => {
    const backThrees = document.querySelector('.back-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');

    let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
    let yAxis = (window.innerHeight / 2 - event.pageY) / 10;

    backThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.2}px) calc(50% + ${yAxis * 0.2}px)`;
    middleThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.4}px) calc(50% + ${yAxis * 0.4}px)`;
    frontThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.9}px) calc(50% + ${yAxis * 0.9}px)`;
}


let zoomFactor = 1; 
let indexZoom = 0;
let isZooming = false;
const adjustZoom = (event) => {
    if (isZooming) return;
    isZooming = true;
    document.querySelectorAll(".banner").forEach(x => x.style.opacity = "0")
    const zoomIntensity = 0.5;
    if (event.deltaY < 0) {
        zoomFactor += zoomIntensity;
    }
    else {
        isZooming = false;
        return ;
    }
    zoomFactor = Math.max(1, Math.min(10, zoomFactor)); // Limiter le zoom entre 0.5x et 2x

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

let logoutRequest = (event) => {
    fetch('/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            console.log('Déconnecté avec succès');
            window.location.reload();
            // Effectuez ici les actions nécessaires après la déconnexion, par exemple rediriger l'utilisateur vers une autre page
        } else {
            console.error('Erreur lors de la déconnexion');
            // Traitez ici les erreurs de déconnexion
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

let loggedInStatus = (data) => {
    const homeFormElement = document.querySelector(".home-form");
    const logoutIconElement = document.querySelector(".logout-icon-nav");
    logoutIconElement.style.display = "block";
    homeFormElement.innerHTML = `
        <div class="button play-online-button">Play Online</div>
    `
    const profilePictureElement = document.querySelector(".profile-picture-nav")
    profilePictureElement.style.backgroundImage = `url("${data.profile_picture}")`
    profilePictureElement.style.display = "block";
    document.querySelector(".welcome-text-nav").innerHTML = `
        Welcome ${data.username}
    `
    logoutIconElement.addEventListener("click", logoutRequest);
}

let loginRequest = (event) => {
    const loginInputValue = document.querySelector(".home-login").value
    const passwordInputValue = document.querySelector(".home-password").value
    const data = {
        username: loginInputValue,
        password: passwordInputValue
    };
    fetch('/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else {
            throw new Error("Identifiant ou mot de passe incorrect");
        }
    })
    .then(data => {
        loggedInStatus(data);
    })  
    .catch(error => {
        console.log("Login Error:", error.message);
    })
}

let registerRequest = (event) => {
    const loginInputValue = document.querySelector(".home-login").value
    const passwordInputValue = document.querySelector(".home-password").value
    const emailInputValue = document.querySelector(".home-email").value
    const data = {
        email: emailInputValue,
        username: loginInputValue,
        password: passwordInputValue
    };
    fetch('/auth/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else {
            throw new Error("Identifiant ou mot de passe incorrect");
        }
    })
    .then(data => {
        const homeFormElement = document.querySelector(".home-form");
        homeFormElement.innerHTML = `
            <div class="button play-online-button">Play Online</div>
        `
    })  
    .catch(error => {
        console.log("Login Error:", error.message);
    })
}

const loginOrRegisterButtonElement = document.querySelector(".login-register-button");
const emailInputElement = document.querySelector(".home-email");
const registerOrLoginLink = document.querySelector(".register-login-text")
let isLoginForm = true;


let changeFormForLogin = (event) => {
    emailInputElement.style.transform = "scale(0)";
    loginOrRegisterButtonElement.innerHTML = "LOGIN";
    registerOrLoginLink.innerHTML = `
        <p>Don't have an account ? <br><span class="register-login-link">Create an account</span></p>
    `
    isLoginForm = true;
}

let changeFormForRegister = (event) => {
    emailInputElement.style.transform = "scale(1)";
    loginOrRegisterButtonElement.innerHTML = "REGISTER";
    registerOrLoginLink.innerHTML = `
        <p>Have an account ? <br><span class="register-login-link">Login Now</span></p>
    `
    isLoginForm = false;

}

let registerOrLoginSwitch = (event) => {
    if (isLoginForm)
        changeFormForRegister();
    else
        changeFormForLogin();
}

let registerOrLoginRequest = (event) => {
    if (isLoginForm)
        loginRequest(event);
    else
        registerRequest(event);
}



export const showHome = async () => {
    const homeElement = document.querySelector("#Home");
    let isAuthenticated = await isUserAuthenticated();
    if (isAuthenticated){
        fetch('/auth/get_pers_infos/', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.ok)
                return response.json();
            else {
                throw new Error("Identifiant ou mot de passe incorrect");
            }
        })
        .then(data => {
            loggedInStatus(data);
        })  
    }
    console.log(isAuthenticated);
    homeElement.style.opacity = "0";
    homeElement.style.display = "block";
    document.querySelector("body").style.backgroundColor = "#0C3452"
    homeElement.style.opacity = 1; 
    document.addEventListener('mousemove', parallaxEffect);
    document.addEventListener('wheel', adjustZoom);
    loginOrRegisterButtonElement.addEventListener('click', registerOrLoginRequest);
    registerOrLoginLink.addEventListener('click', registerOrLoginSwitch);
};