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


    let zoomFactor = 1; 
    let i = 0;

    export const adjustZoom = (event) => {
        const zoomIntensity = 0.5;
        i++;
        if (i === 3)
            return 0;
        if (event.deltaY < 0) {
            zoomFactor += zoomIntensity;
        } else {
            zoomFactor -= zoomIntensity;
        }

        zoomFactor = Math.max(1, Math.min(10, zoomFactor)); // Limiter le zoom entre 0.5x et 2x

        const backThrees = document.querySelector('.back-threes');
        const middleThrees = document.querySelector('.middle-threes');
        const frontThrees = document.querySelector('.front-threes');

        backThrees.style.transform = `scale(${zoomFactor})`;
        middleThrees.style.transform = `scale(${zoomFactor * 1})`;
        frontThrees.style.transform = `scale(${zoomFactor * 2})`;
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