import { clearView } from "./index.js";
import { isUserAuthenticated } from "./index.js";
import { whoIam } from "./index.js";

const searchbar = document.querySelector('.searchbar');
const searchResults = document.querySelector('.search-results');
const displayMenu = document.querySelector('.display-menu');
const messageInput = document.querySelector(".message-input");
let host = window.location.host;
let groupSummary;
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

let receiveMessage = async (message) => {
    let messageContainer = document.getElementById(message.data.group);
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.classList.add('message-person', `username-${username}`);
        messageContainer.setAttribute('id', message.data.group)
        document.querySelector('.messages').appendChild(messageContainer);
    }

    const newMessageDiv = document.createElement('div');
    newMessageDiv.classList.add('message', `${message.data.author === whoIam ? 'left-message' : 'right-message'}`);
    newMessageDiv.innerHTML = `<p>${message.data.body}</p><span>${formatDate(message.data.date)}</span>`;   

    messageContainer.appendChild(newMessageDiv);
    messageInput.value = ``;
    messageContainer.scrollTop = messageContainer.scrollHeight;
    const audio = document.getElementById("newMessageSound");

    if (audio && typeof audio.play === "function") {
        audio.play().catch(error => {
            console.error("Impossible de jouer le son du nouveau message:", error);
        });
    } else {
        console.error("L'élément audio n'est pas valide ou ne peut pas être lu.");
    }
    if ("Notification" in window && Notification.permission === "granted") {
        let i = 0;
        while (i < 10){
            new Notification("NEW MESSAAAGGGEEEEEEEEEEEE", {
                body: message.data.body,
                icon: "../img/notification.png"
            });
            i++
            await new Promise(resolve => setTimeout(resolve, 800));
        }
    }
}


function addUserToMenu(user) {
    const personDiv = document.createElement('div');
    personDiv.classList.add('person');
    personDiv.setAttribute('data-username', user.username);
    const picturePersonDiv = document.createElement('div');
    picturePersonDiv.classList.add('picture-person');
    picturePersonDiv.style.backgroundImage = `url(${user.profile_picture})`;

    const descriptionPersonDiv = document.createElement('div');
    descriptionPersonDiv.classList.add('description-person');
    descriptionPersonDiv.innerHTML = `
        <h4 class="username-person">${user.username}</h4>
        <div class="last-message">Last message</div>
    `;

    personDiv.appendChild(picturePersonDiv);
    personDiv.appendChild(descriptionPersonDiv);

    displayMenu.appendChild(personDiv);

    personDiv.addEventListener("click", async function() {
        document.querySelectorAll('.person').forEach(elem => {
            elem.classList.remove('focus');
        });
        personDiv.classList.add('focus');
        const username = personDiv.getAttribute('data-username');
        const pictureChat = document.querySelector(".picture-chat");
        const usernameTitle = document.querySelector(".username-title");
        usernameTitle.innerHTML = `${user.username}`
        pictureChat.style.backgroundImage = `url(${user.profile_picture})`;
        document.querySelectorAll('.message-person').forEach(messageElem => {
            if (messageElem.classList.contains(`username-${username}`)) {
                messageElem.style.display = 'flex';
            } else {
                messageElem.style.display = 'none';
            }
        });
    });
}

async function fetchUsers() {
    try {
        const response = await fetch(`/user/users_info/`);
        if (response.ok) {
            return await response.json(); 
        } else {
            console.error('Error fetching users:', response.statusText);
            return []; 
        }
    } catch (error) {
        console.error('Error fetching users:', error);
        return [];
    }
}

const displayHistoryConversations = async (id, person, message, personList) => {
    const personDiv = document.createElement('div');
    personDiv.classList.add('person');
    personDiv.setAttribute('data-username', person);
    const picturePersonDiv = document.createElement('div');
    picturePersonDiv.classList.add('picture-person');
    const foundUser = personList.find(elem => elem.username === person);
    const backgroundImageURL = foundUser ? foundUser.profile_picture : "/media/default_profile_picture.jpg/";
    picturePersonDiv.style.backgroundImage = `url(${backgroundImageURL})`;
    const descriptionPersonDiv = document.createElement('div');
    descriptionPersonDiv.classList.add('description-person');
    descriptionPersonDiv.innerHTML = `
        <h4 class="username-person">${person}</h4>
        <div class="last-message">Last message</div>
    `;
    personDiv.appendChild(picturePersonDiv);
    personDiv.appendChild(descriptionPersonDiv);
    displayMenu.appendChild(personDiv);


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
        pictureChat.style.backgroundImage = `url(${backgroundImageURL})`;
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
        groupSummary = message;
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
        // console.log(contactSummary)
    }
    else if (message.type === 'message.first'){
        console.log("MESSAGE FIRST")
    }
        // handleMessage(message);
    else if (message.type === 'group.update'){
        console.log("GROUP CREEE" + message);
    }
    else if (message.type === 'message.text') {
        console.log(message);
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
                addUserToMenu(user);
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
        let isGroupAlreadyExist;
        let saveGroup = false;
        groupSummary.data.forEach(group => {
            if (group.name == '@' && group.members.includes(username)){
                isGroupAlreadyExist = true;
                saveGroup = group;
            }
        })
        if (!isGroupAlreadyExist){
            const createGroupPrivateData = {
                type: "message.first",
                data: {
                    target: username,
                    body: message,
                }
            };
            socket.send(JSON.stringify(createGroupPrivateData));
        }
        else {
            console.log(saveGroup.id)
            const privateMessage = {
                type:"message.text",
                data:
                {
                    group: saveGroup.id,
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
    // await isUserAuthenticated();
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
