
let buttonElement = document.querySelector(".login-button");
export const sendData = () => {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const data = {
        username: username,
        password: password
    };
    fetch('/auth/token/', {
        method: 'POST',
        credentials: 'include', // Ajoutez cette option pour inclure les cookies dans la requête
        headers: {
            'Content-Type': 'application/json' // Définir le type de contenu de la requête
        },
        body: JSON.stringify(data) // Convertir les données en JSON et les inclure dans le corps de la requête
    })
    .then(response => {
        // Log the access_token cookie
        if (response.ok) {
            return response.json(); // Convertir la réponse en JSON
        } else {
            throw new Error('La requête a échoué');
        }
    })
    .then(data => {

        // Traitez la réponse JSON ici si nécessaire
    })
    .catch(error => {
        document.getElementById('loginResponse').innerText = 'Erreur : ' + error.message;
    });
}

export const showSignin = () => {
    document.querySelector("#Signin").style.display = "block";
    document.querySelector("body").style.backgroundColor = "#FFCC00";
    buttonElement.addEventListener("click", sendData());
};