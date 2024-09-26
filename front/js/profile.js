import { showChat } from "./chat.js";
import { loggedInStatus } from "./home.js";
import { isUserAuthenticated, navigateTo, whoIam } from "./index.js";
import { clearView } from "./index.js";

let firstnameInput = document.querySelector("#first-name")
let lastnameInput = document.querySelector("#last-name")
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
            
            break;
    }
};

const activate2FaButton = document.querySelector(".activate-2fa");
const twoFactorButton = document.querySelector(".two-factor");

let displayUserInformations = (data) => {
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
        twoFactorButton.style.display = 'none';
    }

    else{
        twoFactorButton.removeEventListener("click", displayTwoFactorActivation);
        twoFactorButton.addEventListener("click", displayTwoFactorActivation);
        twoFactorButton.innerText = 'ENABLE 2FA';
    }
    
};

const errorMessage = document.getElementById('picture-error-message');

const updateProfilePicture = () => {
    const selectedFile = fileInput.files[0];
    const formData = new FormData();
    const inputField = document.getElementById('profile-btn-upload');
    formData.append("profile_picture", selectedFile);

    inputField.value = '';
    errorMessage.style.display = 'none';

    fetch('/auth/update_picture/', {
        method: 'PUT',
        credentials: 'same-origin',
        body: formData
    })
    .then(response => {
        if (response.ok) {
                window.location.reload();
        } else {
            inputField.classList.add('input-error');
            errorMessage.textContent = 'Invalid profile picture';
            errorMessage.style.display = 'block';
        
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 1500);
        
            setTimeout(() => {
                inputField.classList.remove('input-error');
            }, 500);
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
        genderValue = null; 
    }

    const userData = {
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
        const btnModify = document.querySelector(".modify");
        btnModify.classList.add('input-error');
        errorMessage.textContent = 'Invalid email format';
        errorMessage.style.display = 'block';

        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 1500);

        setTimeout(() => {
            btnModify.classList.remove('input-error');
        }, 500);
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
        qrImgElement.src = 'data:image/png;base64,' + qrImgBase64; 
        qrImgElement.alt = 'QR Code'; 
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
                if (data.success){
            closeTwoFactorActivate();
            window.location.reload();
        }

    })
    .catch(error => {
        
    });
}

async function getMatchHistory() {
    const url = `/user/match_history/${encodeURIComponent(whoIam)}`;
    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erreur: ${response.statusText}`);
        }

        const matchHistory = await response.json();

        return matchHistory;
    } catch (error) {
        return null;
    }
}

const settingsLink = document.querySelector(".link-settings");
const historyLink = document.querySelector(".link-history");
const profileContainer = document.querySelector(".profile-container");
const historyContainer = document.querySelector(".history-container");
const profileHistoryContainer = document.querySelector(".profile-history-container")

const showSettings = () => {
    historyContainer.style.display = "none";
    profileContainer.style.display = "flex";
    historyLink.classList.remove("focus-profile");
    settingsLink.classList.add("focus-profile");
}
const options = {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'UTC' 
};

const showMatchHistory = async () => {
    historyContainer.style.display = "none";
    historyContainer.style.display = "flex";
    const dataMatch = await getMatchHistory();
    if (dataMatch){
                profileHistoryContainer.innerHTML = "";
        const titleContainer = document.createElement("h3");
        titleContainer.innerText = "Match History";
        profileHistoryContainer.appendChild(titleContainer);
        dataMatch.forEach(object => {
            const newMatch = document.createElement("div");
            let otherPerson;
            let amItheWinner;
            if (object.winner === whoIam){
                newMatch.classList.add("match-profile", "profile-win");
                otherPerson = object.loser;
                amItheWinner = true;
            } else {
                newMatch.classList.add("match-profile", "profile-lose");
                otherPerson = object.winner;
                amItheWinner = false;
            }
            const date = new Date(object.date);

            newMatch.innerHTML = `  <div class="profile-score">${amItheWinner ? object.score_w : object.score_l}</div>
                                    <div class='profile-vs-text'><span>${whoIam}</span><span>VS</span><span>${otherPerson}</span></div>
                                    <div class="profile-score">${amItheWinner ? object.score_l : object.score_w}</div>
                                    <div class="profile-date">${date.toLocaleDateString('fr-FR', options)}</div>`
            profileHistoryContainer.appendChild(newMatch);
        })
    }
        settingsLink.classList.remove("focus-profile");
    historyLink.classList.add("focus-profile");
}


export const showHistory = async () => {
    if (await isUserAuthenticated() === true)
    {
        document.title = "bill | history";
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
        .then(async (data)  =>  {
            loggedInStatus(data.profile_picture, data.username);
            await showMatchHistory();
            clearView();
            document.querySelector("#history").style.display = "block";
        })
    };
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
        document.title = "bill | profile";
        clearView();
        loggedInStatus(data.profile_picture, data.username);
        displayUserInformations(data);
        const profileElement = document.querySelector("#profile");
        profileElement.style.display = "block";
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
    settingsLink.addEventListener("click", showSettings);

    activate2FaButton.addEventListener("click", confirm2FaRequest);
}





document.querySelector('.back-to-top-button').addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
});