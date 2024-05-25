import { isUserAuthenticated } from "./index.js";

let firstnameInput = document.querySelector("#first-name")
let lastnameInput = document.querySelector("#last-name")
let usernameInput = document.querySelector("#username")
let emailInput = document.querySelector("#email")
let maleInput = document.querySelector("#male")
let femaleInput = document.querySelector("#female")
let otherInput = document.querySelector("#other")
let dateOfBirthInput = document.querySelector("#date-of-birth")
let profilePictureImage = document.querySelector(".profile-picture")
let genderValue;

let determineGender = (gender) => {
    switch (gender) {
        case 'M':
            maleInput.checked = true;
            break;
        case 'F':
            femaleInput.checked = true;
            break;
        case 'O':
            otherInput.checked = true;
            break;
        default:
            // Aucun genre spécifié ou genre invalide, ne coche aucune case
            break;
    }
};

let displayUserInformations = (data) => {
    usernameInput.value = data.username || "";
    usernameInput.placeholder = !data.username ? "Not Defined" : "";
    firstnameInput.value = data.first_name || "";
    firstnameInput.placeholder = !data.first_name ? "Not Defined" : "";
    lastnameInput.value = data.last_name || "";
    lastnameInput.placeholder = !data.last_name ? "Not Defined" : "";
    emailInput.value = data.email || "";
    emailInput.placeholder = !data.email ? "Not Defined" : "";
    dateOfBirthInput.value = data.date_of_birth || "";
    dateOfBirthInput.placeholder = !data.date_of_birth ? "Not Defined" : "";
    profilePictureImage.style.backgroundImage = `url("${data.profile_picture}")`
    determineGender(data.gender);
};

const modifyProfilePicture = () => {
    // Créer un input de type "file"
    const fileInput = document.createElement("input");
    fileInput.type = "file";

    // Définir les attributs pour permettre le choix de fichiers d'image uniquement
    fileInput.accept = "image/*";

    // Cacher l'input de type "file"
    fileInput.style.display = "none";

    // Ajouter l'input de type "file" au document
    document.body.appendChild(fileInput);

    // Écouter l'événement de changement sur l'input de type "file"
    fileInput.addEventListener("change", () => {
        // Récupérer le fichier sélectionné par l'utilisateur
        const selectedFile = fileInput.files[0];

        // Créer un objet FormData pour envoyer le fichier
        const formData = new FormData();
        formData.append("profile_picture", selectedFile);

        // Envoyer le fichier à l'API via une requête fetch
        fetch('/auth/update_picture/', {
            method: 'PUT',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                console.log("Image de profil mise à jour avec succès !");
                window.location.reload();
            } else {
                throw new Error("Erreur lors de la mise à jour de l'image de profil !");
            }
        })
        .catch(error => {
            console.error(error);
        });

        // Supprimer l'input de type "file" du document
        document.body.removeChild(fileInput);
    });

    // Simuler un clic sur l'input de type "file"
    fileInput.click();
};

let updateUserInfosRequest = async () => {
    await isUserAuthenticated();
    if (maleInput.checked) {
        genderValue = 'M';
    } else if (femaleInput.checked) {
        genderValue = 'F';
    } else if (otherInput.checked) {
        genderValue = 'O';
    } else {
        genderValue = null; // Aucun genre sélectionné
    }

    const userData = {
        username: usernameInput.value,
        first_name: firstnameInput.value,
        last_name: lastnameInput.value,
        email: emailInput.value,
        gender: genderValue,
        date_of_birth: dateOfBirthInput.value
    };
    fetch('/auth/update_client/', {
            method: 'PUT',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(userData)
    })
    .then(response => {
        if (response.ok)
            return response.json();
        else {
            throw new Error("Error asdasd");
        }
    })
    .then(data => {
        window.location.reload();
    })
    .catch(error => {
        console.error('Erreur lors de la mise à jour des informations de l\'utilisateur:', error);
    });
}


export const showProfile = async () => {
    await isUserAuthenticated();
    fetch('/auth/get_pers_infos/', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok)
            return response.json();


        else {
            throw new Error("Identifiant ou mot de passe incorrect");
        }
    })
    .then(data => {
        displayUserInformations(data);
        const profileElement = document.querySelector("#profile");
        profileElement.style.display = "block";
        console.log(data);
    })
    const modifyButton = document.querySelector(".modify");
    modifyButton.addEventListener("click", updateUserInfosRequest);
    const uploadButton = document.querySelector(".upload");
    uploadButton.addEventListener("click", modifyProfilePicture)
}