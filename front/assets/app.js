
function hideSignInContent() {
    document.getElementById('signin-content').style.display = 'none';
}

function hideSignUpContent() {
    document.getElementById('signup-content').style.display = 'none';
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

function showSignUpContent() {
    document.getElementById('signup-content').style.display = 'block';
}

function showSignInContent() {
    document.getElementById('signin-content').style.display = 'block';
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

function showSelectedPage(page)
{
    hideSignUpContent();
    hideSignInContent()
    hideJeuContent(); 
    hideChatContent(); 
    hideAccueilContent();
    if (page === 'jeu')
        showJeuContent(); 
    else if (page === 'chat')
        showChatContent(); 
    else if (page === 'accueil')
        showAccueilContent();
    else if (page === 'signup')
        showSignUpContent();
    else if (page === 'signin')
        showSignInContent();
}

document.querySelector('a[href="#jeu"]').addEventListener('click', function(event) {
    showSelectedPage("jeu");
});

document.querySelector('a[href="#chat"]').addEventListener('click', function(event) {
    showSelectedPage("chat");
});

document.querySelector('a[href="#accueil"]').addEventListener('click', function(event) {
    showSelectedPage("accueil");
});

document.querySelector('a[href="#signup"]').addEventListener('click', function(event) {
    showSelectedPage("signup");
});

document.querySelector('a[href="#signin"]').addEventListener('click', function(event) {
    showSelectedPage("signin");
});

function selectPage()
{
    if (location.hash === "#jeu")
        showSelectedPage("jeu");
    else if (location.hash === "#chat")
        showSelectedPage("chat");
    else if (location.hash === "#accueil")
        showSelectedPage("accueil");
    else if (location.hash === "#signup")
        showSelectedPage("signup");
    else if (location.hash === "#signin")
        showSelectedPage("signin");
}

window.addEventListener('hashchange', function() {
    var hash = window.location.hash.substring(1); 
    if (hash === 'jeu')
        showSelectedPage("jeu");
    else if (hash === 'chat')
        showSelectedPage("chat");
    else if (hash === 'accueil') 
        showSelectedPage("accueil");
    else if (hash === 'signup') 
        showSelectedPage("signup");
    else if (hash === 'signin') 
        showSelectedPage("signin");
});

selectPage();
