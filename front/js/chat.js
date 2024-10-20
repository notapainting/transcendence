import { clearView, navigateTo } from "./index.js";
import { isUserAuthenticated } from "./index.js";
import { whoIam } from "./index.js";
import {initGameWebSocket} from "./game/websocket.js"
import * as enu from './game/enums.js'
import { fastmatch, fastmatchOK } from "./game/menu.js";



const searchbar = document.querySelector('.searchbar');
const searchResults = document.querySelector('.search-results');
const displayMenu = document.querySelector('.display-menu');
const messageInput = document.querySelector(".message-input");
let host = window.location.host;
let contactSummary = null;

export let socket;
export let cs_timemout;

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

const targetProfileDisplay = document.querySelector(".target-profile-display");
const profileTargetInfo = document.querySelector(".profile-target-info");
const targetMatchHistory = document.querySelector(".target-match-history");

const displayTargetProfile = (data, matchHistory) => {
    const profilePicture = document.querySelector(".target-picture");
    profilePicture.style.backgroundImage = `url("${data.profile_picture}")`;
    const targetInfo = document.querySelector(".target-info");
    targetInfo.innerHTML = "";
    targetMatchHistory.innerHTML = "";
    Object.entries(data).forEach(([key, value]) => {
        if (key === "profile_picture" || key === "date_of_birth")
            return ;
        const infoItem = document.createElement("p");
        infoItem.classList.add("info-item");
        infoItem.innerHTML = `<span>${key}:</span> ${value || "None"}`;
        targetInfo.appendChild(infoItem);
    });
    if (matchHistory){
        matchHistory.forEach(object => {
            const newMatch = document.createElement("div");
            let otherPerson;
            let amItheWinner;
            if (object.winner === data.username){
                newMatch.classList.add("match-target", "target-win");
                otherPerson = object.loser;
                amItheWinner = true;
            } else {
                newMatch.classList.add("match-target", "target-lose");
                otherPerson = object.winner;
                amItheWinner = false;
            }
            newMatch.innerHTML = `  <div class="score target-score">${amItheWinner ? object.score_w : object.score_l}</div>
                                    <div class='vs-text'><span>${data.username}</span><span>VS</span><span>${otherPerson}</span></div>
                                    <div class="score opponent-score">${amItheWinner ? object.score_l : object.score_w}</div>`
            targetMatchHistory.appendChild(newMatch);
        })
    }
    targetProfileDisplay.style.display = "flex";
    setTimeout(()=> {
        profileTargetInfo.style.transform = "scale(1)"
    }, 100)
}

let currentPictureChatClickHandler;
let currentTarget = null;
const inviteButton =  document.querySelector(".invite-button");

const displayFocusedPerson = (personDiv, target, profile_picture, flg = null) => {
    document.querySelectorAll('.person').forEach(elem => {
        elem.classList.remove('focus');
    });
    if (!flg)
        inviteButton.style.display = "flex";
    personDiv.classList.add('focus');

    if (currentTarget && !flg){
        inviteButton.removeEventListener("click", currentTarget);
    }
    currentTarget = () => {
        if (fastmatchOK()){
            if (window.location.pathname !== "/play")
                navigateTo("/play");
            setTimeout(() => {
                fastmatch(target);
            }, 3000)   
        }
    };
    if (!flg){
        inviteButton.addEventListener('click', currentTarget);
    }
    const username = personDiv.getAttribute('data-username');
    const pictureChat = document.querySelector(".picture-chat");
    const usernameTitle = document.querySelector(".username-title");
    usernameTitle.innerHTML = `${target}`
    pictureChat.style.backgroundImage = `url(${profile_picture})`;
    document.querySelectorAll('.message-person').forEach(messageElem => {
        if (messageElem.classList.contains(`username-${username}`)) {
            messageElem.style.display = 'flex';
            setTimeout(() => {
                messageElem.scrollTop = messageElem.scrollHeight; 
            }, 0)
        } else {
            messageElem.style.display = 'none';
        }
    });
    if (contactSummary.data.blockeds.find(elem => elem === target) || contactSummary.data.blocked_by.find(elem => elem === target)){
        messageInput.disabled = true;
    }
    else {
        messageInput.disabled = false;
    }
    if (currentPictureChatClickHandler) {
        pictureChat.removeEventListener('click', currentPictureChatClickHandler);
    }

    currentPictureChatClickHandler = async () => {
        try {
            const userInfoResponse = await fetch(`/user/users_info/?username=${encodeURIComponent(target)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
    
            if (!userInfoResponse.ok) {
                throw new Error('Network response was not ok when fetching user info');
            }
    
            const userInfo = userInfoResponse.status !== 204 ? await userInfoResponse.json() : {};
    
            const matchHistoryResponse = await fetch(`/user/match_history/${encodeURIComponent(target)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
    
            if (!matchHistoryResponse.ok) {
                throw new Error('Network response was not ok when fetching match history');
            }
            const matchHistoryText = await matchHistoryResponse.text();
            if (matchHistoryText) {
                const matchHistory = JSON.parse(matchHistoryText); 
                displayTargetProfile(userInfo, matchHistory);
            } else {
                displayTargetProfile(userInfo, null); 
            }
    
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
    };
    pictureChat.addEventListener('click', currentPictureChatClickHandler);
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
            }
}

const blockUser = (target) => {
        try{
        const requestBlock = {
            type: "contact.update",
            data: {
                author: "",
                name: target,
                operation: "block"
            }
        };
        socket.send(JSON.stringify(requestBlock));
    }
    catch (e) {
            }
}

const unblockUser = (target) => {
    try{
        const requestBlock = {
            type: "contact.update",
            data: {
                author: "",
                name: target,
                operation: "remove"
            }
        };
        socket.send(JSON.stringify(requestBlock));
    }
    catch (e) {
            }
}


const addTournamentToMenu = (target, profile_picture, id = null) => {
    const displayMenu = document.querySelector('.display-menu');
    const personDiv = document.createElement('div');
    personDiv.classList.add('person');
    personDiv.setAttribute('data-username', target);
    if (id){
        personDiv.classList.add(id);
    }
    const picturePersonDiv = document.createElement('div');
    picturePersonDiv.classList.add('picture-person');
    picturePersonDiv.style.backgroundImage = `url(${profile_picture})`;
    const descriptionPersonDiv = document.createElement('div');
    descriptionPersonDiv.classList.add('description-person');
    descriptionPersonDiv.innerHTML = `
                                        <div class="username-status">
                                            <h4 class="username-person">${target}</h4>
                                        </div>
                                     `;
    personDiv.append(picturePersonDiv, descriptionPersonDiv);
    displayMenu.insertBefore(personDiv, displayMenu.children[1]);
    personDiv.removeEventListener("click", (event) => displayFocusedPerson(personDiv, target, profile_picture, true));
    personDiv.addEventListener("click", (event) => displayFocusedPerson(personDiv, target, profile_picture, true));
}


function addUserToMenu(target, profile_picture, id = null) {
    const displayMenu = document.querySelector('.display-menu');
    const existingPersonDiv = displayMenu.querySelector(`[data-username="${target}"]`);
    if (existingPersonDiv) {

        displayMenu.insertBefore(existingPersonDiv, displayMenu.children[1]);
    } else {

        const personDiv = document.createElement('div');
        personDiv.classList.add('person');
        personDiv.setAttribute('data-username', target);
        if (id){
            personDiv.classList.add(id);
        }
        const picturePersonDiv = document.createElement('div');
        picturePersonDiv.classList.add('picture-person');
        picturePersonDiv.style.backgroundImage = `url(${profile_picture})`;
        const descriptionPersonDiv = document.createElement('div');
        descriptionPersonDiv.classList.add('description-person');
                        descriptionPersonDiv.innerHTML = `
            <div class="username-status">
                <h4 class="username-person">${target}</h4>
                <span class="status ${friendStatus.find(elem => elem === target) ? "online" : "offline"}" style="display: ${friendStatus.find(elem => elem === target) || contactSummary.data.contacts.find(elem => elem === target) ? 'inline-block' : 'none'};"><span>
            </div>
            <div class="last-message">Last message</div>
        `;
        personDiv.append(picturePersonDiv, descriptionPersonDiv);
        const addOrBlockDiv = document.createElement("div");
        addOrBlockDiv.classList.add("add-or-block")
        if (!contactSummary.data.contacts.find(elem => elem === target) && !contactSummary.data.invited_by.find(elem => elem === target) && !contactSummary.data.invitations.find(elem => elem === target) && !contactSummary.data.blockeds.find(elem => elem === target) && !contactSummary.data.blocked_by.find(elem => elem === target)){
                        const addFriend = document.createElement('i');
            addFriend.classList.add("fa-solid", "fa-plus", "add-button");
            addFriend.addEventListener("click", event => addToFriend(target));
            addOrBlockDiv.appendChild(addFriend);
        }
        const blockButton = document.createElement('i');
        blockButton.classList.add("fa-solid", "fa-ban", "block-button");
        blockButton.addEventListener("click", event => blockUser(target));
        addOrBlockDiv.appendChild(blockButton);
        const unblockButton = document.createElement('i');
        unblockButton.classList.add("fa-solid", "fa-handshake", "unblock-button");
        unblockButton.addEventListener("click", event => unblockUser(target));
        addOrBlockDiv.appendChild(unblockButton);
        if (!contactSummary.data.blockeds.find(elem => elem === target)){
            blockButton.style.display = "inline-block";
            unblockButton.style.display = "none";
        }
        else {
            blockButton.style.display = "none";
            unblockButton.style.display = "inline-block";
        }
        personDiv.appendChild(addOrBlockDiv);
        displayMenu.insertBefore(personDiv, displayMenu.children[1]);
        personDiv.removeEventListener("click", (event) => displayFocusedPerson(personDiv, target, profile_picture));
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
    if (message.data.name === '@'){
        const target = message.data.members.find(person => person != whoIam);
        const personData = await fetchUsers(target);
        const profile_picture = personData.profile_picture;
        addUserToMenu(target, profile_picture, message.data.id);
        let messageContainer = document.getElementById(message.data.group);

        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.classList.add('message-person', `username-${target}`);
            messageContainer.setAttribute('id', message.data.id);
            document.querySelector('.messages').appendChild(messageContainer);
        }

        const newMessageDiv = document.createElement('div');
        const newMessageHour = document.createElement('span');
        const newMessageContainer = document.createElement('div');

        newMessageContainer.classList.add('message-container', `${message.data.messages[0].author === whoIam ? 'left-container' : 'right-container'}`);

        newMessageDiv.classList.add('message', `${message.data.messages[0].author === whoIam ? 'left-message' : 'right-message'}`);
        newMessageDiv.innerHTML = `<p>${message.data.messages[0].body}</p>`
        newMessageContainer.appendChild(newMessageDiv);
         
        newMessageHour.classList.add(`${message.data.messages[0].author === whoIam ? 'left-hour' : 'right-hour'}`);
        newMessageHour.textContent = formatDate(message.data.messages[0].date);
        newMessageContainer.appendChild(newMessageHour);

        messageContainer.appendChild(newMessageContainer);
        
        const focusedPerson = document.querySelector('.person.focus');
        messageContainer.scrollTop = messageContainer.scrollHeight;
        if (focusedPerson.getAttribute('data-username') === target){
            messageContainer.style.display = 'flex';
        }
        messageInput.value = ``;
    }
    else {
        const target = message.data.name;
        const sanitizedTarget = target.replace(/\s+/g, '');
        const profile_picture = "/media/default_profile_picture.jpg";
        addTournamentToMenu(sanitizedTarget, profile_picture, message.data.id);
        let messageContainer = document.getElementById(message.data.group);
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.classList.add('message-person', `username-${sanitizedTarget}`);
            messageContainer.setAttribute('id', message.data.id);
            document.querySelector('.messages').appendChild(messageContainer);
        }
        if (message.data.messages.length !== 0) {
            const newMessageDiv = document.createElement('div');
            const classMessage = `${!message.data.messages[0].author || message.data.messages[0].author !== whoIam ? 'right-message' : 'left-message'}`
            newMessageDiv.classList.add('message', classMessage);
            newMessageDiv.innerHTML = `<p>${message.data.messages[0].body}</p><span>${formatDate(message.data.messages[0].date)}</span>`;   
            messageContainer.appendChild(newMessageDiv);
        }
        const focusedPerson = document.querySelector('.person.focus');
        if (focusedPerson !== null) {
            messageContainer.scrollTop = messageContainer.scrollHeight;
            if (focusedPerson.getAttribute('data-username') === sanitizedTarget){
                messageContainer.style.display = 'flex';
            }
            messageInput.value = ``;
        }
        if (Notification.permission === 'granted') {
            const notification = new Notification("Tournament", {
                body: `${message.data.name}`,
              });
        }  
    }
}

let notifChatCpt = 0;
let notifChat = document.querySelector(".chatcpt");

import { permissionNotification } from "./index.js";

let receiveMessage = async (message) => {
    let messageContainer = document.getElementById(message.data.group);
    const newMessageDiv = document.createElement('div');
    const newMessageHour = document.createElement('span');
    const newMessageContainer = document.createElement('div');
    
    newMessageContainer.classList.add('message-container', `${message.data.author === whoIam ? 'left-container' : 'right-container'}`);

    newMessageDiv.classList.add('message', `${message.data.author === whoIam ? 'left-message' : 'right-message'}`);
    newMessageDiv.innerHTML = `<p>${message.data.body}</p>`
    newMessageContainer.appendChild(newMessageDiv);

    newMessageHour.classList.add(`${message.data.author === whoIam ? 'left-hour' : 'right-hour'}`);
    newMessageHour.textContent = formatDate(message.data.date);
    newMessageContainer.appendChild(newMessageHour);

    messageContainer.appendChild(newMessageContainer);
    messageContainer.scrollTop = messageContainer.scrollHeight;

}


const displayHistoryConversations = async (id, person, message, personList) => {
    addUserToMenu(person, personList.find(elem => elem.username===person).profile_picture, id);
    const personDiv = displayMenu.querySelector(`[data-username="${person}"]`);
    let messageContainer = document.createElement('div');
    messageContainer.classList.add('message-person', `username-${person}`);
    messageContainer.setAttribute('id', id);
    document.querySelector('.messages').appendChild(messageContainer);
    message.forEach(bullet => {
        const newMessageDiv = document.createElement('div');
        const newMessageHour = document.createElement('span');
        const newMessageContainer = document.createElement('div');

        newMessageContainer.classList.add('message-container', `${bullet.author === whoIam ? 'left-container' : 'right-container'}`);

        newMessageDiv.classList.add('message', `${bullet.author === whoIam ? 'left-message' : 'right-message'}`);
        newMessageDiv.setAttribute('id', bullet.id);
        newMessageDiv.innerHTML = `<p>${bullet.body}</p>`;
        newMessageContainer.appendChild(newMessageDiv);
        
        newMessageHour.classList.add(`${bullet.author === whoIam ? 'left-hour' : 'right-hour'}`);
        newMessageHour.textContent = formatDate(bullet.date);
        newMessageContainer.appendChild(newMessageHour);

        messageContainer.insertBefore(newMessageContainer, messageContainer.firstChild);
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

export const incrDecrNotifNumber = (mode, num) => {
    const notifSpan =  document.querySelector(".cpt");
    if (num === 1)
        cpt++;
    if (num === -1)
        cpt--;
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
                                    }   
            })
            declineButton.addEventListener("click", () => {
                notifElem.remove();
                cpt--;
                incrDecrNotifNumber("decrement", 0);
            })
            btnContainer.append(acceptButton, declineButton);
            notifElem.appendChild(btnContainer);
            notificationContainer.appendChild(notifElem);
        })
        incrDecrNotifNumber("increment", 0);
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

const blockUnblockSwitch = (target, type) => {
    const personElem = document.querySelector(`.person[data-username="${target}"]`);
    if (personElem){
        if (type === "unblock") {
            personElem.querySelector(".block-button").style.display = "none";
            personElem.querySelector(".unblock-button").style.display = "inline-block";
        }
        else {
            personElem.querySelector(".block-button").style.display = "inline-block";
            personElem.querySelector(".unblock-button").style.display = "none";
        }
    }
}

const deletePlusIcon = (target) => {
    const personElem = document.querySelector(`.person[data-username="${target}"]`);
        if (personElem){
        const plusElem = personElem.querySelector(".add-button");
        if (plusElem)
            plusElem.style.display = "none";
    }
}

const addPlusIcon = (target) => {
    const personElem = document.querySelector(`.person[data-username="${target}"]`);
        if (personElem){
        const plusElem = personElem.querySelector(".add-button");
        if (plusElem)
            plusElem.style.display = "inline-block";
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

const disableEnableInput = (target, mode) => {
    const focusedPerson = document.querySelector(".focus");
    if (focusedPerson) {
        const username = focusedPerson.dataset.username;
                if (target === username){
            if (mode === "disable" && contactSummary.data.blockeds.find(elem => elem === target) || contactSummary.data.blocked_by.find(elem => elem === target))
                messageInput.disabled = true;
            else if (mode === "enable" && !contactSummary.data.blockeds.find(elem => elem === target) && !contactSummary.data.blocked_by.find(elem => elem === target))
                messageInput.disabled = false;
        }
    }
}

const deleteGroup = (data) => {
    const groupId = data;
    console.log(`ID DU GROUP A DELETE: ${groupId}`)
    const chatContainer = document.getElementById(`${groupId}`);
    const personDiv = document.querySelector(`.${groupId}`);
    console.log('AHhHHHHHH')
    console.log(personDiv);
    console.log(chatContainer);
    if (chatContainer)
        chatContainer.remove();
    if (personDiv)
        personDiv.remove(); // parenteleemnt??
}

async function handleMessage(message) {
    console.log(message)
    if (message.type === 'contact.summary'){
        contactSummary = message;
                fillNotification();
        contactSummaryPromiseResolve();
    }
    else if (message.type === 'group.summary'){
        await contactSummaryPromise;
        await statusPromise;
        console.log(message);
        while (displayMenu.children.length > 1) {
            displayMenu.removeChild(displayMenu.children[1]);
        }
        let personList = await fetchUsers();
        message.data.forEach(group => {
            let id = group.id;
            let person = null
            if (group.members.length > 0) {
                person = group.members.find(value => value !== whoIam);
            }
            else {
                person = group.restricts.find(value => value !== whoIam);
            }
            let messages = group.messages;
            displayHistoryConversations(id, person, messages, personList);
        })
    }
    else if (message.type === 'group.update'){
        
        createGroup(message);
    }
    else if (message.type === 'message.text') {
        receiveMessage(message);
    }
    else if (message.type === "contact.update"){
        if (message.data.operation === "invitation"){
            if (message.data.author !== whoIam){
                newFriendRequest(message.data.author); 
                deletePlusIcon(message.data.author);
                pushToContact(message.data.author);
            } else {
                deletePlusIcon(message.data.name); 
                pushToContact(message.data.name);
            }
        }
        if (message.data.author === whoIam && message.data.operation === "contact") 
            deleteNotif(message.data.name);
        if (message.data.operation === "block"){
            if (message.data.author === whoIam) {
                contactSummary.data.blockeds.push(message.data.name);
                blockUnblockSwitch(message.data.name, "unblock");
                deletePlusIcon(message.data.name);
                disableEnableInput(message.data.name, "disable");
            } else {  
                contactSummary.data.blocked_by.push(message.data.author);
                deletePlusIcon(message.data.author);
                disableEnableInput(message.data.author, "disable");
            }
        }
        if (message.data.operation === "remove") {
            if (message.data.author === whoIam) {
                let index = contactSummary.data.blockeds.indexOf(message.data.name);
                contactSummary.data.blockeds.splice(index, 1);
                blockUnblockSwitch(message.data.name, "block");
                const amIblocked = contactSummary.data.blocked_by.find(elem => elem === message.data.name);
                if (!amIblocked)
                    addPlusIcon(message.data.name);
                disableEnableInput(message.data.name, "enable");
                
            } else {
                let index = contactSummary.data.blocked_by.indexOf(message.data.author);
                contactSummary.data.blocked_by.splice(index, 1);
                const didIblocked = contactSummary.data.blockeds.find(elem => elem === message.data.author);
                if (!didIblocked)
                    addPlusIcon(message.data.author);
                disableEnableInput(message.data.author, "enable");
            }
        }
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
    }
    else if (message.type === "group.delete"){
        deleteGroup(message.data);
    }
    statusPromiseResolve();
}

let flg = 0;

export async function initializeWebSocket() {
    flg = 1;
    if (await isUserAuthenticated() === false) return ;
    socket = new WebSocket('wss://' + host + '/chat/');

    socket.onopen = function() {
            };

    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleMessage(message);
    }

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    socket.onclose = function() {
        cs_timemout = setTimeout(initializeWebSocket, 5000);
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
            if (user.username === whoIam || user.username === "admin")
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
                const isGroupAlreadyExist = document.querySelector(`.username-${username}`);
                if (!isGroupAlreadyExist){
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
    const inputField = document.getElementById('message-box');

    inputField.value = '';

    if (message.length > 512)
    {
        inputField.classList.add('input-error');
        document.getElementById("messageInput").placeholder = "Message too long (512 max)";

        setTimeout(() => {
            document.getElementById("messageInput").placeholder = "Message...";
        }, 1500);

        setTimeout(() => {
            inputField.classList.remove('input-error');
        }, 500);
    }
    if (!message) return;
    const focusedPerson = document.querySelector('.person.focus');
    if (!focusedPerson) {
        inputField.classList.add('input-error');
        document.getElementById("messageInput").placeholder = "Select a person first";

        setTimeout(() => {
            document.getElementById("messageInput").placeholder = "Message...";
        }, 1500);

        setTimeout(() => {
            inputField.classList.remove('input-error');
        }, 500);
        messageInput.value = '';
        return;
    }
    const username = focusedPerson.getAttribute('data-username');
        sendToWebSocket(username, message);
    messageInput.value = '';
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
    if (event.key === "Enter") {
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


