import { clearView } from "./index.js";
import { isUserAuthenticated } from "./index.js";

export const showChat = async () => {
    clearView();
    await isUserAuthenticated();
    const chatElement = document.querySelector("#chat");
    chatElement.style.display = "flex";
    const host = window.location.host;
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    const socket = new WebSocket('wss://' + host  + '/chat/');
    socket.onopen = () => {
        console.log('WebSocket is connected');
    };
}