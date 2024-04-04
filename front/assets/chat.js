
const roomName = "testRoom/";
const host = window.location.host;


var userName = 'anon';
let chatSocket = undefined;




document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e)
{
    console.log(e.keyCode)
    if (e.keyCode === 13)
    {
        document.querySelector('#chat-message-submit').click();
    }
};


document.querySelector('#chat-submit-user').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-message-input');
    userName = messageInputDom.value;

    document.cookie = 'userName=' + userName + ';';
    messageInputDom.value = '';
    chatSocket = new WebSocket('wss://' + host  + '/ws/chat/' + roomName);

    chatSocket.onmessage = function(e)
    {
        console.log('msg')
        const data = JSON.parse(e.data);
        console.log(data);
        document.querySelector('#chat-log').value += (data.message + '\n');
    };

    chatSocket.onclose = function(e)
    {
        console.error('Chat socket closed unexpectedly');
    };

};

document.querySelector('#chat-enter-room').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-message-input').value;
    const room  = messageInputDom; 
    chatSocket.send(JSON.stringify({
        'type': 'room',
        'room': room
    }));
   messageInputDom.value = '';
};

document.querySelector('#chat-submit-message').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value; 
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': message
    }));
   messageInputDom.value = '';
};


