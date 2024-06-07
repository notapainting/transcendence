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

function displayMessages(username, messages) {
    let messageContainer = document.querySelector(`.message-person.username-${username}`);
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.classList.add('message-person', `username-${username}`);
        document.querySelector('.messages').appendChild(messageContainer);
    }
    messageContainer.innerHTML = '';
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', message.author === username ? 'left-message' : 'right-message');
        messageDiv.innerHTML = `<p>${message.body}</p>`;
        messageContainer.appendChild(messageDiv);
    });
    messageContainer.style.display = "block";
}

let usernamePrivateGroupList = {}


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
        console.log(username);
        // fetchMessages(username);
        document.querySelectorAll('.message-person').forEach(messageElem => {
            if (messageElem.classList.contains(`username-${username}`)) {
                messageElem.style.display = 'flex';
            } else {
                messageElem.style.display = 'none';
            }
        });
    });
}

function handleMessage(message) {
    if (message.type === 'group.summary'){
        groupSummary = message;
        groupSummary.data.forEach(group => {
            if (group.name === '@'){
                group.members.forEach(member=> {
                    // if (member !== whoIam)
                        // addUserToMenu();
                })
            }
        })
        // usernamePrivateGroupList.forEach(user=> {
        //     // addUserToMenu(user)
        // })
    }
    else if (message.type === 'contact.summary'){
        contactSummary = message;
        console.log(contactSummary)
    }
    else if (message.type === 'message.first'){
        console.log("MESSAGE FIRST")
    }
        // handleMessage(message);
    else if (message.type === 'group.update'){
        console.log("GROUP CREEE" + message);
    }
    else if (message.type === 'message.text') {
        // let messageData = message.data;
        // const messageContainer = document.querySelector(`.message-person.username-${data.author}`);
        // if (!messageContainer){
        //     messageContainer = document.createElement('div');
        //     messageContainer.classList.add('message-person', `username-${data.author}`);
        //     document.querySelector('.messages').appendChild(messageContainer);
        // }
        // const newMessageDiv = document.createElement('div');
        // newMessageDiv.classList.add('message', 'right-message');
        // newMessageDiv.innerHTML = `<p>${body}</p>`;
        // messageContainer.appendChild(newMessageDiv);
        // messageContainer.style.display = "block";
    }
    else if (message.type === 'message.fetch') {
        const { author, messages } = message.data;
        console.log('Fetched messages:', messages);
        displayMessages(author, messages);
    }
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
        // Try to reconnect every 5 seconds
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

async function fetchUsers(query) {
    try {
        const response = await fetch(`/user/users_info/`);
        if (response.ok) {
            const users = await response.json();
            // Filtrer les utilisateurs en fonction du query
            const filteredUsers = users.filter(user => user.username.toLowerCase().startsWith(query.toLowerCase()));
            displaySearchResults(filteredUsers);
        } else {
            console.error('Error fetching users:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}



function fetchMessages(username) {
    const payload = {
        type: 'message.fetch',
        data: {
            author: username,
        }
    };
    console.log("je suis rentre dans fetch message")
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
    console.log("username focus :" + username);
    sendToWebSocket(username, message);
    let messageContainer = document.querySelector(`.message-person.username-${username}`);

    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.classList.add('message-person', `username-${username}`);

        document.querySelector('.messages').appendChild(messageContainer);
    }

    const newMessageDiv = document.createElement('div');
    newMessageDiv.classList.add('message', 'left-message');
    newMessageDiv.innerHTML = `<p>${message}</p>`;

    messageContainer.appendChild(newMessageDiv);
    messageContainer.style.display = "block";
    messageInput.value = '';
}

const searchUsers = () => {
    const query = searchbar.value.trim();
    if (query.length > 0) {
        fetchUsers(query);
    } else {
        searchResults.style.display = 'none';
    }
}

export const showChat = async () => {
    clearView();
    let test;
    test = await isUserAuthenticated();
    console.log(test);
    const chatElement = document.querySelector("#chat");
    
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
