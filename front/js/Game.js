export const showGame = () => {
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