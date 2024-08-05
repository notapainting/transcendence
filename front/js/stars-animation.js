document.addEventListener("DOMContentLoaded", function() {
    const shootingStarInterval = 3000; // Interval between shooting stars in milliseconds
  
    function createShootingStar() {
      const shootingStar = document.createElement("div");
      shootingStar.className = "shooting-star";
      shootingStar.style.top = `${Math.random() * 100}%`;
      shootingStar.style.left = `${Math.random() * 100}%`;
      document.body.appendChild(shootingStar);
      setTimeout(() => {
        document.body.removeChild(shootingStar);
      }, 3000);
    }
  
    setTimeout(createShootingStar, Math.random() * shootingStarInterval); // Initial shooting star
  
    // Randomize shooting star interval
    function randomizeShootingStarInterval() {
      const interval = Math.random() * shootingStarInterval;
      setTimeout(function() {
        createShootingStar();
        randomizeShootingStarInterval();
      }, interval);
    }
  
    randomizeShootingStarInterval();
  });
  