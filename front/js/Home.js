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
};