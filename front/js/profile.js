import { loggedInStatus } from "./home.js";
import { isUserAuthenticated } from "./index.js";
import { clearView } from "./index.js";

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
let fileInput;
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

const activate2FaButton = document.querySelector(".activate-2fa");
const twoFactorButton = document.querySelector(".two-factor");

let displayUserInformations = (data) => {
    usernameInput.value = data.username || "";
    usernameInput.placeholder = !data.username ? "Not Defined" : "";
    firstnameInput.value = data.first_name || "";
    firstnameInput.placeholder = !data.first_name ? "Not Defined" : "";
    lastnameInput.value = data.last_name || "";
    lastnameInput.placeholder = !data.last_name ? "Not Defined" : "";
    emailInput.value = data.email || "";
    emailInput.placeholder = !data.email ? "Not Defined" : "";
    profilePictureImage.style.backgroundImage = `url("${data.profile_picture}")`
    determineGender(data.gender);
    if (data.is_2fa_enabled){ 
        twoFactorButton.removeEventListener("click", displayTwoFactorActivation);
        twoFactorButton.innerText = 'DISABLE 2FA';
    }

    else{
        twoFactorButton.removeEventListener("click", displayTwoFactorActivation);
        twoFactorButton.addEventListener("click", displayTwoFactorActivation);
        twoFactorButton.innerText = 'ENABLE 2FA';
    }
    
};

const updateProfilePicture = () => {
    const selectedFile = fileInput.files[0];
    const formData = new FormData();
    formData.append("profile_picture", selectedFile);

    fetch('/auth/update_picture/', {
        method: 'PUT',
        credentials: 'same-origin',
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
    document.body.removeChild(fileInput);
}

const modifyProfilePicture = async () => {
    fileInput = document.createElement("input");
    fileInput.type = "file";

    fileInput.accept = "image/*";

    fileInput.style.display = "none";

    document.body.appendChild(fileInput);
    await isUserAuthenticated();
    fileInput.removeEventListener("change", updateProfilePicture);
    fileInput.addEventListener("change", updateProfilePicture);
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
const twoFactorDisplay = document.querySelector(".two-factor-display");
const twoFactorContainer = document.querySelector(".two-factor-container");

const displayTwoFactorActivation = async (event) => {
    await isUserAuthenticated()
    twoFactorDisplay.style.display = "flex"
    setTimeout(()=> {
        twoFactorContainer.style.transform = "scale(1)"
    }, 200)
    fetch('/auth/activate2FA/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const qrImgBase64 = data.qr_img;
        const qrImgElement = document.querySelector(".qr-code-img");
        qrImgElement.src = 'data:image/png;base64,' + qrImgBase64; // Définir la source de l'image sur l'image QR base64
        qrImgElement.alt = 'QR Code'; // Ajouter une description alternative pour l'image
        const manualCodeElement = document.querySelector(".manual-code");
        manualCodeElement.innerText = 'Manual code : ' + data.secret_key;
    })
    .catch(error => {
        document.getElementById('activate2FAResponse').innerText = 'Erreur : ' + error.message;
    });

}

const closeTwoFactorActivate = (event) => {
    twoFactorContainer.style.transform = "scale(0)"
    setTimeout(()=> {
            twoFactorDisplay.style.display = "none"
    }, 200)
} 

const confirm2FaRequest = async (event) => {
    await isUserAuthenticated()
    const code = document.querySelector(".input-f2a-activation").value;
    const data = {
        code: code
    };
    fetch('/auth/confirm2FA/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        closeTwoFactorActivate();
        window.location.reload();
    })
    .catch(error => {
        
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
        clearView();
        loggedInStatus(data.profile_picture, data.username);
        displayUserInformations(data);
        const profileElement = document.querySelector("#profile");
        profileElement.style.display = "block";
        console.log(data);
    })
    const modifyButton = document.querySelector(".modify");
    modifyButton.removeEventListener("click", updateUserInfosRequest);
    modifyButton.addEventListener("click", updateUserInfosRequest);
    const uploadButton = document.querySelector(".upload");
    uploadButton.removeEventListener("click", modifyProfilePicture)
    twoFactorButton.removeEventListener("click", displayTwoFactorActivation);
    uploadButton.addEventListener("click", modifyProfilePicture)
    twoFactorButton.addEventListener("click", displayTwoFactorActivation);
    document.querySelector(".close-two-factor").removeEventListener("click", closeTwoFactorActivate)
    document.querySelector(".close-two-factor").addEventListener("click", closeTwoFactorActivate)
    activate2FaButton.removeEventListener("click", confirm2FaRequest);
    activate2FaButton.addEventListener("click", confirm2FaRequest);
}