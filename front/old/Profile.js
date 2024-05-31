import { isUserAuthenticated, navigateTo} from "./index.js";
import { logoutRequest } from "./Home.js";


const usernameElem = document.querySelector(".profile-username");
const firstNameElem = document.querySelector(".profile-first-name");
const lastNameElem = document.querySelector(".profile-last-name");
const emailElem = document.querySelector(".profile-email");
const genderElem = document.querySelector(".profile-gender");
const dateOfBirthElem = document.querySelector(".profile-date-of-birth");


let displayUserInformations = (data) => {
    usernameElem.value = data.username;
    if (!data.first_name)
        firstNameElem.placeholder = "Not Defined"
    firstNameElem.value = data.first_name;
    lastNameElem.value = data.last_name;
    if (!data.last_name)
        lastNameElem.placeholder = "Not Defined"
    emailElem.value = data.email;
    if (!data.email)
        emailElem.placeholder = "Not Defined"
    genderElem.value = data.gender;
    if (!data.gender)
        genderElem.placeholder = "Not Defined"
    dateOfBirthElem.value = data.date_of_birth;
    if (!data.date_of_bith)
        dateOfBirthElem.placeholder = "Not Defined"
}

let updateClientRequest = async () => {
    let isAuthenticated = await isUserAuthenticated();
    if (isAuthenticated){
        const userData = {
            username: usernameElem.value,
            first_name: firstNameElem.value,
            last_name: lastNameElem.value,
            email: emailElem.value,
            gender: genderElem.value,
            date_of_birth: dateOfBirthElem.value
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
                
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour des informations de l\'utilisateur:', error);
        });
    }
    else {
        logoutRequest();
        navigateTo("/")
    }
}


export const showProfile = () => {
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
        console.log(data);
    })
    document.querySelector("#Profile").style.display = "block";
    console.log(document.querySelector(".profile-button"));
    document.querySelector(".profile-button").addEventListener('click', updateClientRequest);
    
};