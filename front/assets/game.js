var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

var start = document.getElementById("startButton");
var stop = document.getElementById("stopButton");
var back = document.getElementById("backButton");

var gameRunning = false;

// ball properties
var ballRadius = 10;
var ballX = canvas.width / 2;
var ballY = canvas.height / 2;
var ballSpeedX = 7;
var ballSpeedY = 7;

// paddle properties
var paddleHeight = 80;
var paddleWidth = 10;
var leftPaddleY = canvas.height / 2 - paddleHeight / 2;
var rightPaddleY = canvas.height / 2 - paddleHeight / 2;
var paddleSpeed = 10;

// score properties
var leftPlayerScore = 0;
var rightPlayerScore = 0;
var maxScore = 5;

// Listen for keyboard events
document.addEventListener("keydown", keyDownHandler);
document.addEventListener("keyup", keyUpHandler);

// Listen for button events
start.addEventListener('click', startGame);
stop.addEventListener('click', stopGame);

// Handle key press
var upPressed = false;
var downPressed = false;
let wPressed = false;
let sPressed = false;

const gameSocket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/ws-game/'
);

gameSocket.onmessage = function(e) {
	console.log(e);
};

gameSocket.onclose = function(e) {
	console.error('Game socket closed unexpectedly');
};

document.querySelector('#backButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'back button click !'
	}));
};

document.querySelector('#startButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'startButton'
	}));
};

	
// Start game
function startGame() 
{
    // fetch('https://127.0.0.1:8443/start-game/', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({"gameRunning": true})
    // })
    // .then(response => {
    //     return response.json();
    // })
    // .then(data => {
    //     console.log(data);
    // })
    // .catch(error => {
    //     console.error('Error:', error);
    // });
	// gameRunning = true; // a enlever
}

// Stop game
function stopGame()
{
    fetch('https://127.0.0.1:8443/start-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"gameRunning": false})
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });

	// gameRunning = false; // a enlever
}

// Pong Functions
function keyDownHandler(e) {
	var formData
	if (e.key === "ArrowUp") {
		formData = {"keyPressed": "up"};
	} else if (e.key === "ArrowDown") {
		formData = {"keyPressed": "down"};
	} else if (e.key === "w") {
		formData = {"keyPressed": "w"};
	} else if (e.key === "s") {
		formData = {"keyPressed": "s"};
	} else {
		formData = {"keyPressed": "none"};
	}

	var formDataJSON = JSON.stringify(formData);
	fetch('https://127.0.0.1:8443/api-game/paddle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: formDataJSON
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('error:',  );
    });


	// if (e.key === "ArrowUp") {
	// 	upPressed = true;
	// } else if (e.key === "ArrowDown") {
	// 	downPressed = true;
	// } else if (e.key === "w") {
	// 	wPressed = true;
	// } else if (e.key === "s") {
	// 	sPressed = true;
	// } // a enlever 
}

function keyUpHandler(e) {
	var formData
	if (e.key === "ArrowUp") {
		formData = {"keyRelease": "up"};
	} else if (e.key === "ArrowDown") {
		formData = {"keyRelease": "down"};
	} else if (e.key === "w") {
		formData = {"keyRelease": "w"};
	} else if (e.key === "s") {
		formData = {"keyRelease": "s"};
	} else {
		formData = {"keyRelease": "none"};
	}

	var formDataJSON = JSON.stringify(formData);
	fetch('https://127.0.0.1:8443/api-game/paddle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: formDataJSON
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('error:',  );
    });

	// if (e.key === "ArrowUp") {
	// 	upPressed = false;
	// } else if (e.key === "ArrowDown") {
	// 	downPressed = false;
	// } else if (e.key === "w") {
	// 	wPressed = false;
	// } else if (e.key === "s") {
	// 	sPressed = false;
	// } // a enlever
}

function update() {
	if (upPressed && rightPaddleY > 0) {
	  rightPaddleY -= paddleSpeed;
	} else if (downPressed && rightPaddleY + paddleHeight < canvas.height) {
	  rightPaddleY += paddleSpeed;
	}

	if (wPressed && leftPaddleY > 0) {
	  leftPaddleY -= paddleSpeed;
	} else if (sPressed && leftPaddleY + paddleHeight < canvas.height) {
	  leftPaddleY += paddleSpeed;
	}

	ballX += ballSpeedX;
	ballY += ballSpeedY;

	if (ballY - ballRadius < 0 || ballY + ballRadius > canvas.height) {
	  ballSpeedY = -ballSpeedY;
	}
  
	if (
	  ballX - ballRadius < paddleWidth &&
	  ballY > leftPaddleY &&
	  ballY < leftPaddleY + paddleHeight
	) {
	  ballSpeedX = -ballSpeedX;
	}
  
	if (
	  ballX + ballRadius > canvas.width - paddleWidth &&
	  ballY > rightPaddleY &&
	  ballY < rightPaddleY + paddleHeight
	) {
	  ballSpeedX = -ballSpeedX;
	}
  
	if (ballX < 0) {
	  rightPlayerScore++;
	  reset();
	} else if (ballX > canvas.width) {
	  leftPlayerScore++;
	  reset();
	}
  
	if (leftPlayerScore === maxScore) {
	  playerWin("Left player");
	} else if (rightPlayerScore === maxScore) {
	  playerWin("Right player");
	}
  }

function getBallInfo() {
    fetch('https://127.0.0.1:8443/api-game/ball-info/')
        .then(response => response.json())
        .then(data => {
            draw(data);
        })
        .catch(error => {
            console.error('Error fetching ball info:', error);
			data = null;
        });
}


// getBallInfo();
console.log("gameRunning = ", gameRunning);

if (gameRunning === true)
	setInterval(getBallInfo, 100);


function playerWin(player) {
	var message = "Congratulations! " + player + " win!";
	var myParagraph = document.getElementById("scoreMessage");
	myParagraph.innerText = message; 
	reset();
}
  
function reset() {
	ballX = canvas.width / 2;
	ballY = canvas.height / 2;
	ballSpeedX = -ballSpeedX;
	ballSpeedY = Math.random() * 10 - 5;
}

function draw(data) {
	ctx.clearRect(0, 0, data.width, data.height);
  
	ctx.fillStyle = "#FFF";
	ctx.font = "15px Arial";
  
	ctx.beginPath();
	ctx.moveTo(data.width / 2, 0);
	ctx.lineTo(data.width / 2, data.height);
	ctx.strokeStyle = "#FFF";
	ctx.stroke();
	ctx.closePath();
  
	ctx.beginPath();
	ctx.arc(data.x, data.y, data.radius, 0, Math.PI * 2);
	ctx.fill();
	ctx.closePath();
  
	// ctx.fillRect(0, leftPaddleY, paddleWidth, paddleHeight);
  
	// ctx.fillRect(data.width - paddleWidth, rightPaddleY, paddleWidth, paddleHeight);
  
	// ctx.fillText("Score: " + leftPlayerScore, 10, 20);
	// ctx.fillText("Score: " + rightPlayerScore, data.width - 70, 20);
  }
  

function loop() {
	if (gameRunning == true)
		update();
	draw();
	animationId = requestAnimationFrame(loop);
}

// loop();