
const roomName = "testRoom/";
const host = "localhost";
const port = ":8443";
const userName = "Borys";
document.cookie = 'Username=' + userName + ';';
document.cookie = 'Room=' + roomName + ';';

const chatSocket = new WebSocket('wss://' + host + port + '/ws/chat/' + roomName);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#chat-log').value += (data.message + '\n');
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
   messageInputDom.value = '';
};

// var authToken = 'R3YKZFKBVi';

// document.cookie = 'X-Authorization=' + authToken + '; path=/';

// var ws = new WebSocket(
//     'wss://localhost:9000/wss/'
// );
