
console.log(location.hash)

function hideConnexionContent() {
    document.getElementById('connexion-content').style.display = 'none';
}

function hideJeuContent() {
    document.getElementById('jeu-content').style.display = 'none';
    if ( document.getElementById("jeuID").classList.contains('active') )
        document.getElementById("jeuID").classList.toggle('active');
}

function hideChatContent() {
    document.getElementById('chat-content').style.display = 'none';
    if ( document.getElementById("chatID").classList.contains('active') )
        document.getElementById("chatID").classList.toggle('active');
}

function hideAccueilContent() {
    document.getElementById('accueil-content').style.display = 'none';
    if ( document.getElementById("accID").classList.contains('active') )
        document.getElementById("accID").classList.toggle('active');
}

function showJeuContent() {
    document.getElementById('jeu-content').style.display = 'block';
    document.getElementById("jeuID").classList.add('active');
}

function showChatContent() {
    document.getElementById('chat-content').style.display = 'block';
    document.getElementById("chatID").classList.add('active');
}

function showAccueilContent() {
    document.querySelector('#accueil-content').style.display = 'block';
    document.getElementById("accID").classList.add('active');
}

function showNavBar() {
    document.querySelector('#navbar').style.display = 'block';
}


document.querySelector('a[href="#jeu"]').addEventListener('click', function(event) {
    hideJeuContent(); 
    hideChatContent(); 
    hideAccueilContent();
    showJeuContent(); 
});

document.querySelector('a[href="#chat"]').addEventListener('click', function(event) {
    hideChatContent(); 
    hideJeuContent();
    hideAccueilContent();
    showChatContent(); 
});

document.querySelector('a[href="#accueil"]').addEventListener('click', function(event) {
    hideChatContent(); 
    hideJeuContent();
    hideAccueilContent();
    showAccueilContent();
});

function selectPage()
{
    if (location.hash === "#jeu")
    {
        hideJeuContent(); 
        hideChatContent(); 
        hideAccueilContent();
        showJeuContent(); 
    }
    else if (location.hash === "#chat")
    {
        hideChatContent(); 
        hideJeuContent();
        hideAccueilContent();
        showChatContent(); 
    }
    else if (location.hash === "#accueil")
    {
        hideChatContent(); 
        hideJeuContent();
        hideAccueilContent();
        showAccueilContent();
    }
}

// document.querySelectorAll('.nav-link').forEach(link => {
//     if (link.getAttribute('href') !== '#jeu') { 
//         link.addEventListener('click', function(event) {
//             // event.preventDefault(); 
//             hideJeuContent(); 
//         });
//     }
//     else if (link.getAttribute('href') !== '#chat') { 
//         link.addEventListener('click', function(event) {
//             // event.preventDefault(); 
//             hideChatContent(); 
//         });
//     }
//     else if (link.getAttribute('href') !== '#accueil') { 
//         link.addEventListener('click', function(event) {
//             // event.preventDefault(); 
//             hideAccueilContent(); 
//         });
//     }
// });

selectPage();