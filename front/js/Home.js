import { navigateTo } from "./index.js";
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

const adjustZoom = (event) => {
    document.querySelectorAll(".banner").forEach(x => x.style.opacity = "0")
    const zoomIntensity = 0.5;
    if (event.deltaY < 0) {
        zoomFactor += zoomIntensity;
    }
    else {
        return ;
    }

    zoomFactor = Math.max(1, Math.min(10, zoomFactor)); // Limiter le zoom entre 0.5x et 2x

    const backThrees = document.querySelector('.back-threes');
    const backgroundThrees = document.querySelector('.background-threes')
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');
    switch (indexZoom){
        case 0:
            backThrees.style.transform = `scale(${zoomFactor})`;
            backgroundThrees.style.filter = 'blur(3px)';
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
    }
    indexZoom++;

};


export const showHome = () => {
    const homeElement = document.querySelector("#Home");
    homeElement.style.opacity = "0";
    homeElement.style.display = "block";
    document.querySelector("body").style.backgroundColor = "#0C3452"
    setTimeout(() => {
        homeElement.style.opacity = 1; 
    }, 10); 
    // Ici, vous pouvez ajouter des manipulations supplémentaires spécifiques à la vue du dashboard
    document.addEventListener('mousemove', parallaxEffect);
    document.addEventListener('wheel', adjustZoom);
};