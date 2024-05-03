
const roomName = "testRoom/";
const host = window.location.host;


var userName = 'anon';
let chatSocket = undefined;

function getCurrentDateTime() {
    let currentDate = new Date();
    let year = currentDate.getFullYear();
    let month = String(currentDate.getMonth() + 1).padStart(2, '0');
    let day = String(currentDate.getDate()).padStart(2, '0');
    let hours = String(currentDate.getHours()).padStart(2, '0');
    let minutes = String(currentDate.getMinutes()).padStart(2, '0');
    let seconds = String(currentDate.getSeconds()).padStart(2, '0');
    let milliseconds = String(currentDate.getMilliseconds()).padStart(6, '0');
    let tzoffsetvalue = -(currentDate.getTimezoneOffset() / 60)
    let offsetOperator = tzoffsetvalue > 0 ? '+' : '-'
    let tzoffset = String(Math.abs(tzoffsetvalue)).padEnd(4, '0');

    let formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}${offsetOperator}${tzoffset}`;
    return formattedDateTime;
}



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
        document.querySelector('#chat-log').value += (data.data + '\n');
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
        "type":"contact.update",
        "data":
        {
            "name":"acheron",
            "relation":"i",
            "operation":"a"
        }
    }));
   messageInputDom.value = '';
};

document.querySelector('#chat-submit-message').onclick = function(e)
{
    console.log(getCurrentDateTime());
    const messageInputDom = document.querySelector('#chat-input');
    const message = messageInputDom.value; 
    const now = getCurrentDateTime();
    chatSocket.send(JSON.stringify(
        {
            'type': 'chat.message',
            'data': 
                {
                    'body':message,
                    'group': '755b83ae-0cb9-461c-8639-b55ec589a6a5',
                    'date': now
                }
        }
    ));
   messageInputDom.value = '';
};


