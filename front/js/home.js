const parallaxEffect = (event) => {
    const backThrees = document.querySelector('.back-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');

    const maxOffsetX = 75; 
    const maxOffsetY = 75; 

    let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
    let yAxis = (window.innerHeight / 2 - event.pageY) / 10;

    xAxis = Math.min(Math.max(xAxis, -maxOffsetX), maxOffsetX);
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
const homeFormButton = document.querySelector(".home-form-btn");
const loginOrSigninText = document.querySelector(".login-or-register-text");
const homeEmailInput = document.querySelector("#home-email");
const homeAccept = document.querySelector(".accept");

const switchToLoginForm = () => {
    homeEmailInput.style.transform = "scale(0)";
    setTimeout(()=> {
        homeAccept.style.transform = "scale(0)"
        homeFormButton.innerHTML = "LOGIN";
    }, 200)
    loginOrSigninText.innerHTML = `Don't have an account ? <br><span class="switch-form">Create One</span>`;
}

const switchToRegisterForm = () => {
    homeEmailInput.style.transform = "scale(1)";
        setTimeout(()=> {
        homeAccept.style.transform = "scale(1)"
        homeFormButton.innerHTML = "REGISTER";
    }, 200)

    loginOrSigninText.innerHTML = `Have an account ? <br><span class="switch-form">Login</span>`;
}

const switchForm = (event) => {
    const switchFormLink = event.target.closest(".switch-form");
    if (switchFormLink) {
        if (switchFormLink.textContent === "Create One") {
            switchToRegisterForm();
        } else {
            switchToLoginForm();
        }
    }
}

export const showHome = () => {
    const homeElement = document.querySelector("#home");
    homeElement.style.display = "block";
    const playOfflineBtnElement = document.querySelector(".play-offline-btn");
    document.addEventListener('mousemove', parallaxEffect);
    document.addEventListener('wheel', scrollDownEffect);
    playOfflineBtnElement.addEventListener("click", scrollUpEffect)
    document.addEventListener("click", switchForm);
}