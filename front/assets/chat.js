
const roomName = "testRoom/";
const host = window.location.host;


var userName = 'anon';
let chatSocket = undefined;




document.querySelector('#chat-input').focus();
document.querySelector('#chat-input').onkeyup = function(e)
{
    if (e.keyCode === 13)
    {
        document.querySelector('#chat-submit-message').click();
    }
};


document.querySelector('#chat-submit-user').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-input');
    userName = messageInputDom.value;

    document.cookie = 'userName=' + userName + ';';
    messageInputDom.value = '';
    chatSocket = new WebSocket('wss://' + host  + '/chat/');

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
    const messageInputDom = document.querySelector('#chat-input').value;
    const room  = messageInputDom; 
    chatSocket.send(JSON.stringify({
        'type': 'room',
        'room': room
    }));
   messageInputDom.value = '';
};

document.querySelector('#chat-submit-message').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-input');
    const message = messageInputDom.value; 
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': message
    }));
   messageInputDom.value = '';
};


