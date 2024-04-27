
const roomName = "testRoom/";
const host = window.location.host;


var userName = 'anon';
let chatSocket = undefined;

function getCurrentDateTime() {
    // Obtenez la date et l'heure actuelles
    let currentDate = new Date();

    // Obtenez les composants de la date et de l'heure
    let year = currentDate.getFullYear();
    let month = String(currentDate.getMonth() + 1).padStart(2, '0');
    let day = String(currentDate.getDate()).padStart(2, '0');
    let hours = String(currentDate.getHours()).padStart(2, '0');
    let minutes = String(currentDate.getMinutes()).padStart(2, '0');
    let seconds = String(currentDate.getSeconds()).padStart(2, '0');
    let milliseconds = String(currentDate.getMilliseconds()).padStart(6, '0');
    let tzoffsetvalue = -(currentDate.getTimezoneOffset() / 60)
    let tzoffset = String((tzoffsetvalue)).padEnd(4, '0');

    // Formatte la date et l'heure
    let formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}${tzoffset}`;

    // Renvoie la date et l'heure formatées
    return formattedDateTime;
}
// 2024-04-27T23:35:48.000949Z+0300
// 2024-04-27T20:17:30.958838Z+0000
// Exemple d'utilisation de la fonction
console.log(getCurrentDateTime());



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
    console.log(getCurrentDateTime());
    const messageInputDom = document.querySelector('#chat-input');
    const message = messageInputDom.value; 
    const now = getCurrentDateTime();
    chatSocket.send(JSON.stringify({
        'type': 'chat.message',
        'data': 
        {
            "body":message,
            "group": "755b83ae-0cb9-461c-8639-b55ec589a6a5",
            "date": now
            // "date": "2024-04-27T23:55:05.000432Z"
            
        }
    }));
   messageInputDom.value = '';
};


