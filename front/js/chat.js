import { clearView } from "./index.js";
import { isUserAuthenticated } from "./index.js";
import { whoIam } from "./index.js";
import {initGameWebSocket} from "./game/websocket.js"
import * as enu from './game/enums.js'
// enlever le bouton + lorsque la demande damis a ete accepte
// enlever la notif lorsque lautre personne accepte

const searchbar = document.querySelector('.searchbar');
const searchResults = document.querySelector('.search-results');
const displayMenu = document.querySelector('.display-menu');
const messageInput = document.querySelector(".message-input");
let host = window.location.host;
let contactSummary = null;

let socket;

let cpt = 0;

let friendStatus = [];

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

const displayFocusedPerson = (personDiv, target, profile_picture) => {
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
}

const addToFriend = (target) => {
    try{
        const requestFriend = {
            type: "contact.update",
            data: {
                author: "",
                name: target,
                operation: "invitation"
            }
        };
        socket.send(JSON.stringify(requestFriend));
    }
    catch (e) {
        console.log(e);
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
        console.log(friendStatus);
        console.log(contactSummary);
        descriptionPersonDiv.innerHTML = `
            <div class="username-status">
                <h4 class="username-person">${target}</h4>
                <span class="status ${friendStatus.find(elem => elem === target) ? "online" : "offline"}" style="display: ${friendStatus.find(elem => elem === target) || contactSummary.data.contacts.find(elem => elem === target) ? 'inline-block' : 'none'};"><span>
            </div>
            <div class="last-message">Last message</div>
        `;
        personDiv.append(picturePersonDiv, descriptionPersonDiv);
        if (!contactSummary.data.contacts.find(elem => elem === target) && !contactSummary.data.invited_by.find(elem => elem === target) && !contactSummary.data.invitations.find(elem => elem === target)){
            console.log("salut");
            const addFriend = document.createElement('i');
            addFriend.classList.add("fa-solid", "fa-plus", "add-button");
            addFriend.addEventListener("click", event => addToFriend(target));
            personDiv.appendChild(addFriend);
        }
        displayMenu.insertBefore(personDiv, displayMenu.children[1]);
        personDiv.removeEventListener("click", (event) => displayFocusedPerson(personDiv, targe, profile_picture));
        personDiv.addEventListener("click", (event) => displayFocusedPerson(personDiv, target, profile_picture));
    }
}




export async function fetchUsers(username = null) {
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
            return username ? null : [];
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

const notificationContainer = document.querySelector(".notification-container");

const incrDecrNotifNumber = (mode) => {
    const notifSpan =  document.querySelector(".cpt");
    if (mode === "increment"){
        if (cpt > 0){
            notifSpan.style.backgroundColor = "red"
            notifSpan.innerHTML = cpt;
        }
    }
    if (mode === "decrement"){
        if (cpt < 1) {
            notifSpan.style.backgroundColor = "transparent"
            notifSpan.innerHTML = "";
        }
        else
            notifSpan.innerHTML = cpt;
    }   
}

const fillNotification = () => {
    if (contactSummary){
        contactSummary.data.invited_by.forEach(person => {
            cpt++;
            const notifElem = document.createElement("div");
            notifElem.classList.add("notif");
            notifElem.setAttribute("data-user", person);
            notifElem.innerHTML = `
                <p>${person} invited you as friend</p>
            `
            const btnContainer = document.createElement("div");
            const acceptButton = document.createElement("div");
            const declineButton = document.createElement("div");
            btnContainer.classList.add("n-btn-container");
            acceptButton.classList.add("n-btn", "accept-friend");
            declineButton.classList.add("n-btn", "decline-friend");
            acceptButton.innerHTML = "Accept";
            declineButton.innerHTML = "Decline";
            acceptButton.addEventListener("click", () => {
                try{
                    const requestFriend = {
                        type: "contact.update",
                        data: {
                            author: "",
                            name: person,
                            operation: "contact"
                        }
                    };
                    socket.send(JSON.stringify(requestFriend));
                }
                catch (e) {
                    console.log(e);
                }   
            })
            declineButton.addEventListener("click", () => {
                notifElem.remove();
                cpt--;
                incrDecrNotifNumber("decrement");
            })
            btnContainer.append(acceptButton, declineButton);
            notifElem.appendChild(btnContainer);
            notificationContainer.appendChild(notifElem);
        })
        incrDecrNotifNumber("increment");
    }
}

const newFriendRequest = (target) => {
    if (document.querySelector(`.notif[data-user="${target}"]`)) {
        return;
    }
    const notifElem = document.createElement("div");
    notifElem.classList.add("notif");
    notifElem.setAttribute("data-user", target);
    notifElem.innerHTML = `
        <p>${target} invited you as friend</p>
    `
    const btnContainer = document.createElement("div");
    const acceptButton = document.createElement("div");
    const declineButton = document.createElement("div");
    btnContainer.classList.add("n-btn-container");
    acceptButton.classList.add("n-btn", "accept-friend");
    declineButton.classList.add("n-btn", "decline-friend");
    acceptButton.innerHTML = "Accept";
    declineButton.innerHTML = "Decline";
    cpt++;
    incrDecrNotifNumber("increment");
    acceptButton.addEventListener("click", () => {
        try{
            const requestFriend = {
                type: "contact.update",
                data: {
                    author: "",
                    name: target,
                    operation: "contact"
                }
            };
            socket.send(JSON.stringify(requestFriend));
        }
        catch (e) {
            console.log(e);
        }   
    })
    btnContainer.append(acceptButton, declineButton);
    notifElem.appendChild(btnContainer);
    notificationContainer.appendChild(notifElem);
}

const deleteNotif = (target) => {
    document.querySelector(`.notif[data-user="${target}"]`).remove();
    cpt--;
    incrDecrNotifNumber("decrement");
}

const deletePlusIcon = (target) => {
    const personElem = document.querySelector(`.person[data-username="${target}"]`);
    if (personElem){
        const plusElem = personElem.querySelector(".add-button");
        if (plusElem)
            plusElem.remove();
    }
}

let contactSummaryPromiseResolve;
const contactSummaryPromise = new Promise(resolve => {
    contactSummaryPromiseResolve = resolve;
});
let statusPromiseResolve;
const statusPromise = new Promise(resolve => {
    statusPromiseResolve = resolve;
});

const pushToContact = (target) => {
    contactSummary.data.contacts.push(target);
}

const changeExistingStatus = (target, mode) => {
    const personDiv = document.querySelector(`.person[data-username="${target}"]`);
    if (personDiv){
        const statusDiv = personDiv.querySelector(".status");
        statusDiv.style.display = "inline-block"
        mode === "online" ? statusDiv.style.backgroundColor = "green" : statusDiv.style.backgroundColor = "gray"
    }
}

async function handleMessage(message) {
    if (message.type === 'contact.summary'){
        contactSummary = message;
        console.log(message);
        fillNotification();
        contactSummaryPromiseResolve();
    }
    else if (message.type === 'group.summary'){
        console.log(message);
        await contactSummaryPromise;
        await statusPromise;
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
    else if (message.type === 'group.update'){
        console.log("EVENT GROUP UPDATE");
        createGroup(message);
    }
    else if (message.type === 'message.text') {
        console.log("EVENT TEXT");
        console.log("EVENT MESSAGE TEXT");
        receiveMessage(message);
    }
    else if (message.type === "contact.update"){
        if (message.data.operation === "invitation"){
            if (message.data.author !== whoIam){
                newFriendRequest(message.data.author); //si je ne suis celui qui recoit linvit
                deletePlusIcon(message.data.author);
                pushToContact(message.data.author);
            }
            else {
                deletePlusIcon(message.data.name); //si je suis celui qui envoie linvit
                pushToContact(message.data.name);
            }
        }
        if (message.data.author === whoIam && message.data.operation === "contact") //si je suis celui qui accepte
            deleteNotif(message.data.name);
        console.log(message);
    }
    else if (message.type === "status.update"){
        if (message.data.status === "o" || message.data.status === "online"){
            friendStatus.push(message.data.author);
            changeExistingStatus(message.data.author, "online");
        }
        else {
            friendStatus = friendStatus.filter(author => author !== message.data.author);
            changeExistingStatus(message.data.author, "offline");
        }
        statusPromiseResolve();
        console.log(message);
        console.log(friendStatus);
    }
    statusPromiseResolve();
}

let flg = 0;

export function initializeWebSocket() {
    flg = 1;
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

const selectSearchResult = (user) => {
    addUserToMenu(user.username, user.profile_picture);
    searchResults.style.display = 'none';
    searchbar.value = '';
} 

function displaySearchResults(users) {
    searchResults.innerHTML = '';
    if (users.length > 0) {
        users.forEach(user => {
            if (user.username === whoIam)
                return ;
            const userDiv = document.createElement('div');
            userDiv.classList.add('result-item');
            userDiv.textContent = user.username;
            userDiv.removeEventListener('click', (event) => selectSearchResult(user));
            userDiv.addEventListener('click', (event) => selectSearchResult(user));
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
        console.log(username, message);
        const isGroupAlreadyExist = document.querySelector(`.username-${username}`);
        console.log(isGroupAlreadyExist);
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
            console.log("j'envoie message message.text " + isGroupAlreadyExist.id + " " + message);
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

const leftHideElement = document.querySelector(".left-hide");
const leftDisplayElement = document.querySelector(".left-display");
const menuContainerElement = document.querySelector(".menu-container");
const chatElement = document.querySelector(".chatbox");
const bubbleElement = document.querySelector(".bubble");

const displayChat = () => {
    chatElement.style.display = "flex";
    bubbleElement.style.display = "none"
}

const closeChat = () => {
    chatElement.style.display = "none";
    bubbleElement.style.display = "flex"
}

const hideChatLeft = () => {
    menuContainerElement.style.transform = "scale(0)";
    leftHideElement.style.transform = "scale(0)";
    leftDisplayElement.style.display = "flex";
}

const showChatLeft = () => { 
    menuContainerElement.style.transform = "scale(1)";
    leftHideElement.style.transform = "scale(1)";
    leftDisplayElement.style.display = "none";
}

const sendMessageEnter = (event) => {
    if (event.key === "") {
        sendMessage();
    }
}


export const showChat = async () => {
    await isUserAuthenticated();
    if (window.getComputedStyle(chatElement).display === 'none')
        bubbleElement.style.display = "flex"
    bubbleElement.removeEventListener("click", displayChat);
    bubbleElement.addEventListener("click", displayChat);
    document.querySelector(".close-chat").removeEventListener("click", closeChat)
    document.querySelector(".close-chat").addEventListener("click", closeChat)
    leftHideElement.removeEventListener("click", hideChatLeft);
    leftHideElement.addEventListener("click", hideChatLeft);
    document.querySelector(".left-display").removeEventListener("click", showChatLeft)
    document.querySelector(".left-display").addEventListener("click", showChatLeft)
    if (!flg)
        initializeWebSocket();
    initGameWebSocket(enu.backendPath.REMOTE);
    searchbar.addEventListener('input', searchUsers);
    const sendButton = document.querySelector(".chat-send");
    sendButton.addEventListener("click", sendMessage);
    messageInput.removeEventListener("keydown", sendMessageEnter);
    messageInput.addEventListener("keydown", sendMessageEnter);
}
