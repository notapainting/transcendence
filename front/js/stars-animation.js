document.addEventListener("DOMContentLoaded", function() {
    const shootingStarInterval = 3000; 
    const gameMenu = document.getElementById("game-menu"); 
    function createShootingStar() {
      const shootingStar = document.createElement("div");
      shootingStar.className = "shooting-star";
      shootingStar.style.top = `${Math.random() * 100}%`;
      shootingStar.style.left = `${Math.random() * 100}%`;
      gameMenu.appendChild(shootingStar); 
      setTimeout(() => {
        gameMenu.removeChild(shootingStar);
      }, 3000);
    }
  
    setTimeout(createShootingStar, Math.random() * shootingStarInterval); 
  
    function randomizeShootingStarInterval() {
      const interval = Math.random() * shootingStarInterval;
      setTimeout(function() {
        createShootingStar();
        randomizeShootingStarInterval();
      }, interval);
    }
  
    randomizeShootingStarInterval();
});
