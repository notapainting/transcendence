
const roomName = "testRoom/";
const host = window.location.host;
const MESSAGE = 'message.text'

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
    // let tzoffsetvalue = -(currentDate.getTimezoneOffset() / 60)
    // let offsetOperator = tzoffsetvalue > 0 ? '+' : '-'
    // let tzoffset = String(Math.abs(tzoffsetvalue)).padEnd(2, '0'); ;${offsetOperator}${tzoffset}

    let formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}`;
    
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
        const data = JSON.parse(e.data);
        console.log(data);
        if (data.type == MESSAGE)
            document.querySelector('#chat-log').value += (data.data.author + ": " + data.data.body + '\n');
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
        "type":"message.fetch",
        "data":
        {
            "group":"bff768c5-de7c-42e7-ac2b-b4dd2760ffc4",
            "date":"2024-05-13T13:29:26.000447",
        }
    }));
   messageInputDom.value = '';
};

// c/b/i

// c/i
// + c/i -> nop
// +r rem
// + b -> r + block

// b
// b -> nop
// r/c/i -> remove



// name -> target
// update : c/i/b/r
document.querySelector('#chat-submit-message').onclick = function(e)
{
    const messageInputDom = document.querySelector('#chat-input');
    const message = messageInputDom.value; 
    const now = getCurrentDateTime();
    console.log(now)
    chatSocket.send(JSON.stringify(
        {
            'type': MESSAGE,
            'data': 
                {
                    'body':message,
                    'group': 'bff768c5-de7c-42e7-ac2b-b4dd2760ffc4',
                    'date': now
                }
        }
    ));
   messageInputDom.value = '';
};


