document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.nav-link');
    const backThrees = document.querySelector('.back-threes');
    const middleThrees = document.querySelector('.middle-threes');
    const frontThrees = document.querySelector('.front-threes');

    // Fonction pour afficher une section et masquer les autres
    function showSection(sectionId) {
        sections.forEach(section => {
            if (section.id === sectionId) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }

    // Fonction pour mettre à jour l'historique de navigation
    function updateHistory(sectionId) {
        history.pushState({ sectionId: sectionId }, '', '#' + sectionId);
    }

    // Fonction pour mettre à jour la position des couches en fonction du mouvement de la souris
    function parallaxEffect(event) {
        let xAxis = (window.innerWidth / 2 - event.pageX) / 10;
        let yAxis = (window.innerHeight / 2 - event.pageY) / 10;
        backThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.2}px) calc(50% + ${yAxis * 0.2}px)`;
        middleThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.4}px) calc(50% + ${yAxis * 0.4}px)`;
        frontThrees.style.backgroundPosition = `calc(50% + ${xAxis * 0.9}px) calc(50% + ${yAxis * 0.9}px)`;
    }

    // Gestion des clics sur les liens de navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Empêche le comportement par défaut du lien
            const sectionId = this.getAttribute('href').substring(1); // Récupère l'ID de la section à afficher
            showSection(sectionId);
            updateHistory(sectionId);
        });
    });

    // Gestion des événements de changement d'URL
    window.addEventListener('popstate', function(event) {
        const sectionId = event.state ? event.state.sectionId : 'home'; // Récupère l'ID de la section à afficher
        showSection(sectionId);
    });

    // Afficher la section par défaut au chargement de la page
    const initialSectionId = window.location.hash.substring(1) || 'home'; // Récupère l'ID de la section à afficher depuis l'URL
    showSection(initialSectionId);
    updateHistory(initialSectionId);
    // Écouter les événements de mouvement de la souris sur tout le document pour l'effet de parallaxe
    document.addEventListener('mousemove', parallaxEffect);
    const redSection = document.querySelector('.red');
    const gameLink = document.querySelector('.game');
    gameLink.addEventListener('click', function(event) {
        event.preventDefault();
        const sectionId = this.getAttribute('href').substring(1); // Récupère l'ID de la section à afficher
        showSection(sectionId);
        updateHistory(sectionId);
        redSection.style.opacity = '1';
    });
});