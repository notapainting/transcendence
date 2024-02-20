
var connexion = document.getElementById("anon");

connexion.addEventListener('click', launchSite);

function launchSite()
{
    hideConnexionContent();
    showNavBar();
    showAccueilContent();
}

function hideConnexionContent() {
    document.getElementById('connexion-content').style.display = 'none';
}

function hideJeuContent() {
    document.getElementById('jeu-content').style.display = 'none';
}

function hideChatContent() {
    document.getElementById('chat-content').style.display = 'none';
}

function hideAccueilContent() {
    document.getElementById('accueil-content').style.display = 'none';
}

function showJeuContent() {
    document.getElementById('jeu-content').style.display = 'block';
}

function showChatContent() {
    document.getElementById('chat-content').style.display = 'block';
}

function showAccueilContent() {
    document.querySelector('#accueil-content').style.display = 'block';
}

function showNavBar() {
    document.querySelector('#navbar').style.display = 'block';
}


document.querySelector('a[href="#jeu"]').addEventListener('click', function(event) {
    event.preventDefault(); 
    hideJeuContent(); 
    hideChatContent(); 
    hideAccueilContent();
    showJeuContent(); 
});

document.querySelector('a[href="#chat"]').addEventListener('click', function(event) {
    event.preventDefault(); 
    hideChatContent(); 
    hideJeuContent();
    hideAccueilContent();
    showChatContent(); 
});

document.querySelector('a[href="#accueil"]').addEventListener('click', function(event) {
    event.preventDefault(); 
    hideChatContent(); 
    hideJeuContent();
    hideAccueilContent();
    showAccueilContent();
});

document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') !== '#jeu') { 
        link.addEventListener('click', function(event) {
            event.preventDefault(); 
            hideJeuContent(); 
        });
    }
    else if (link.getAttribute('href') !== '#chat') { 
        link.addEventListener('click', function(event) {
            event.preventDefault(); 
            hideChatContent(); 
        });
    }
    else if (link.getAttribute('href') !== '#accueil') { 
        link.addEventListener('click', function(event) {
            event.preventDefault(); 
            hideAccueilContent(); 
        });
    }
});
