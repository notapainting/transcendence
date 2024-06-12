import { clearView } from "./index.js";
import { isUserAuthenticated } from "./index.js";
import { whoIam } from "./index.js";

const searchbar = document.querySelector('.searchbar');
const searchResults = document.querySelector('.search-results');
const displayMenu = document.querySelector('.display-menu');
const messageInput = document.querySelector(".message-input");
let host = window.location.host;
let contactSummary;

let socket;

let usernamePrivateGroupList = {}

function formatDate(dateString) {
    const date = new Date(dateString);
    const currentDate = new Date();
    
    if (date.toDateString() === currentDate.toDateString()) {
        return `${date.getHours().toString().padStart(2, '0')}h${date.getMinutes().toString().padStart(2, '0')}`;
    } else if (date.getFullYear() === currentDate.getFullYear()) {
        return `${date.getDate()}/${date.getMonth() + 1} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    } else {
        return `${date.getFullYear()}/${date.getDate()}/${date.getMonth() + 1} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    }
}

function addUserToMenu(target, profile_picture) {
    const displayMenu = document.querySelector('.display-menu');
    const existingPersonDiv = displayMenu.querySelector(`[data-username="${target}"]`);
    if (existingPersonDiv) {
        console.log("je vais remonter le user: " + target + "avec la photo de profil : " + profile_picture);
        displayMenu.insertBefore(existingPersonDiv, displayMenu.children[1]);
    } else {
        console.log("je vais add le user: " + target + "avec la photo de profil : " + profile_picture);
        const personDiv = document.createElement('div');
        personDiv.classList.add('person');
        personDiv.setAttribute('data-username', target);

        const picturePersonDiv = document.createElement('div');
        picturePersonDiv.classList.add('picture-person');
        picturePersonDiv.style.backgroundImage = `url(${profile_picture})`;

        const descriptionPersonDiv = document.createElement('div');
        descriptionPersonDiv.classList.add('description-person');
        descriptionPersonDiv.innerHTML = `
            <h4 class="username-person">${target}</h4>
            <div class="last-message">Last message</div>
        `;
        personDiv.appendChild(picturePersonDiv);
        personDiv.appendChild(descriptionPersonDiv);
        displayMenu.insertBefore(personDiv, displayMenu.children[1]);
        personDiv.addEventListener("click", async function() {
            document.querySelectorAll('.person').forEach(elem => {
                elem.classList.remove('focus');
            });
            personDiv.classList.add('focus');
            const username = personDiv.getAttribute('data-username');
            const pictureChat = document.querySelector(".picture-chat");
            const usernameTitle = document.querySelector(".username-title");
            usernameTitle.innerHTML = `${target}`
            pictureChat.style.backgroundImage = `url(${profile_picture})`;
            document.querySelectorAll('.message-person').forEach(messageElem => {
                if (messageElem.classList.contains(`username-${username}`)) {
                    messageElem.style.display = 'flex';
                } else {
                    messageElem.style.display = 'none';
                }
            });
        });
    }
}

async function fetchUsers(username = null) {
    try {
        let url = '/user/users_info/';
        if (username) {
            url += `?username=${encodeURIComponent(username)}`;
        }
        
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            console.error('Error fetching users:', response.statusText);
            return username ? null : []; // Retourne null si une seule recherche d'utilisateur échoue, sinon retourne un tableau vide pour la recherche de tous les utilisateurs
        }
    } catch (error) {
        console.error('Error fetching users:', error);
        return username ? null : [];
    }
}

let createGroup = async (message) => {
    console.log("je cree le groupe au front: ");
    console.log(message);
    const target = message.data.members.find(person => person != whoIam);
    console.log("LE GROUPE SE CREE sur la target :" + target);
    const personData = await fetchUsers(target);
    const profile_picture = personData.profile_picture;
    addUserToMenu(target, profile_picture);
    let messageContainer = document.getElementById(message.data.group);
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.classList.add('message-person', `username-${target}`);
        messageContainer.setAttribute('id', message.data.id);
        document.querySelector('.messages').appendChild(messageContainer);
    }
    const newMessageDiv = document.createElement('div');
    newMessageDiv.classList.add('message', `${message.data.messages[0].author === whoIam ? 'left-message' : 'right-message'}`);
    newMessageDiv.innerHTML = `<p>${message.data.messages[0].body}</p><span>${formatDate(message.data.messages[0].date)}</span>`;   
    messageContainer.appendChild(newMessageDiv);
    const focusedPerson = document.querySelector('.person.focus');
    console.log("AHHHHH");
    console.log(focusedPerson)
    console.log("AHHHHH");
    console.log(target);
    console.log("AHHHHH");
    messageContainer.scrollTop = messageContainer.scrollHeight;
    if (focusedPerson.getAttribute('data-username') === target){
        messageContainer.style.display = 'flex';
        console.log("je display le message");
    }
    messageInput.value = ``;
}
let receiveMessage = async (message) => {
    let messageContainer = document.getElementById(message.data.group);
    console.log(messageContainer);
    const newMessageDiv = document.createElement('div');
    newMessageDiv.classList.add('message', `${message.data.author === whoIam ? 'left-message' : 'right-message'}`);
    newMessageDiv.innerHTML = `<p>${message.data.body}</p><span>${formatDate(message.data.date)}</span>`;   
    messageContainer.appendChild(newMessageDiv);
    messageInput.value = ``;
    const focusedPerson = document.querySelector('.person.focus');
    messageContainer.scrollTop = messageContainer.scrollHeight;
    // if (focusedPerson === message.data.author)
    //         messageContainer.style.display = 'flex';
}


const displayHistoryConversations = async (id, person, message, personList) => {
    addUserToMenu(person, personList.find(elem => elem.username===person).profile_picture);
    const personDiv = displayMenu.querySelector(`[data-username="${person}"]`);
    let messageContainer = document.createElement('div');
    messageContainer.classList.add('message-person', `username-${person}`);
    messageContainer.setAttribute('id', id);
    document.querySelector('.messages').appendChild(messageContainer);
    message.forEach(bullet => {
        const newMessageDiv = document.createElement('div');
        newMessageDiv.classList.add('message', `${bullet.author === whoIam ? 'left-message' : 'right-message'}`);
        newMessageDiv.setAttribute('id', bullet.id);
        newMessageDiv.innerHTML = `<p>${bullet.body}</p><span>${formatDate(bullet.date)}</span>`;
        messageContainer.insertBefore(newMessageDiv, messageContainer.firstChild);
    })

    personDiv.addEventListener("click", async function() {
        document.querySelectorAll('.person').forEach(elem => {
            elem.classList.remove('focus');
        });
        personDiv.classList.add('focus');
        const username = personDiv.getAttribute('data-username');
        const pictureChat = document.querySelector(".picture-chat");
        const usernameTitle = document.querySelector(".username-title");
        usernameTitle.innerHTML = `${person}`
        pictureChat.style.backgroundImage = `url(${personList.find(elem => elem.username===person).profile_picture})`;
        document.querySelectorAll('.message-person').forEach(messageElem => {
            if (messageElem.classList.contains(`username-${username}`)) {
                messageElem.style.display = 'flex';
            } else {
                messageElem.style.display = 'none';
            }
        });
    });
}


async function handleMessage(message) {
    if (message.type === 'group.summary'){
        console.log("EVENT GROUP SUMMARY");
        while (displayMenu.children.length > 1) {
            displayMenu.removeChild(displayMenu.children[1]);
        }
        let personList = await fetchUsers();
        message.data.forEach(group => {
            let id = group.id;
            let person = group.members.find(value => value !== whoIam);
            let messages = group.messages;
            displayHistoryConversations(id, person, messages, personList);
        })
    }
    else if (message.type === 'contact.summary'){
        contactSummary = message;
    }
    else if (message.type === 'group.update'){
        console.log("EVENT GROUP UPDATE");
        createGroup(message);
    }
    else if (message.type === 'message.text') {
    console.log("EVENT MESSAGE TEXT");
        receiveMessage(message);
    }
    // else if (message.type === 'message.fetch') {
    //     const { author, messages } = message.data;
    //     console.log('Fetched messages:', messages);
    //     displayMessages(author, messages);
    // }
}



function initializeWebSocket() {
    socket = new WebSocket('wss://' + host + '/chat/');

    socket.onopen = function() {
        console.log('WebSocket connection established');
    };

    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleMessage(message);
    }

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    socket.onclose = function() {
        console.log('WebSocket connection closed');
        setTimeout(initializeWebSocket, 5000);
    };
}

function displaySearchResults(users) {
    searchResults.innerHTML = '';
    if (users.length > 0) {
        users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.classList.add('result-item');
            userDiv.textContent = user.username;
            userDiv.addEventListener('click', function () {
                addUserToMenu(user.username, user.profile_picture);
                searchResults.style.display = 'none';
                searchbar.value = '';
            });
            searchResults.appendChild(userDiv);
        });
        searchResults.style.display = 'block';
    } else {
        searchResults.style.display = 'none';
    }
}


function fetchMessages(username) {
    const payload = {
        type: 'message.fetch',
        data: {
            author: username,
        }
    };
    socket.send(JSON.stringify(payload));
}

const sendToWebSocket = (username, message) => {
    try {
        const isGroupAlreadyExist = document.querySelector(`.username-${username}`)
        if (!isGroupAlreadyExist){
            console.log("le groupe n'existe pas");
            const createGroup = {
                type: "message.first",
                data: {
                    target: username,
                    body: message,
                }
            };
            socket.send(JSON.stringify(createGroup));
        }
        else {
            const privateMessage = {
                type:"message.text",
                data:
                {
                    group: isGroupAlreadyExist.id,
                    body: message,
                    respond_to: "",
                    date: new Date().toISOString()
                }
            };
            socket.send(JSON.stringify(privateMessage));
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
}


function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    const focusedPerson = document.querySelector('.person.focus');
    if (!focusedPerson) {
        alert('Please select a person to send the message to.');
        return;
    }
    const username = focusedPerson.getAttribute('data-username');
    console.log("sendToWebsocket " + username + " " + message);
    sendToWebSocket(username, message);
}

const searchUsers = async () => {
    const query = searchbar.value.trim();
    if (query.length > 0) {
        const users = await fetchUsers(); 
        const filteredUsers = users.filter(user => user.username.toLowerCase().startsWith(query.toLowerCase())); 
        displaySearchResults(filteredUsers); 
    } else {
        searchResults.style.display = 'none';
    }
};

export const showChat = async () => {
    await isUserAuthenticated();
    const chatElement = document.querySelector(".chatbox");
    chatElement.style.display = "flex";
    initializeWebSocket();
    searchbar.addEventListener('input', searchUsers);
    const sendButton = document.querySelector(".chat-send");
    sendButton.addEventListener("click", sendMessage);
    messageInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
}
