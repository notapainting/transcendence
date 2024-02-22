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
back.addEventListener('click', backTest);

// Handle key press
var upPressed = false;
var downPressed = false;
let wPressed = false;
let sPressed = false;

//test backend connexion
function backTest() {
	console.log("click");
    fetch('http://127.0.0.1:8000/game/')
        .then(response => response.json())
        .then(data => console.log(data.message))
        .catch(error => {
            console.error('Error response:', error);
        });
	}
	
// Start game
function startGame() {
    fetch('http://127.0.0.1:8000/start-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"gameRunning": true})
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

	gameRunning = true; // a enlever
}

// Stop game
function stopGame()
{
    fetch('http://127.0.0.1:8000/start-game/', {
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

	gameRunning = false; // a enlever
}

// Pong Functions
function keyDownHandler(e) {
	if (e.key === "ArrowUp") {
		upPressed = true;
	} else if (e.key === "ArrowDown") {
		downPressed = true;
	} else if (e.key === "w") {
		wPressed = true;
	} else if (e.key === "s") {
		sPressed = true;
	}
}

function keyUpHandler(e) {
	if (e.key === "ArrowUp") {
		upPressed = false;
	} else if (e.key === "ArrowDown") {
		downPressed = false;
	} else if (e.key === "w") {
		wPressed = false;
	} else if (e.key === "s") {
		sPressed = false;
	}
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

function draw() {
	ctx.clearRect(0, 0, canvas.width, canvas.height);
  
	ctx.fillStyle = "#FFF";
	ctx.font = "15px Arial";
  
	ctx.beginPath();
	ctx.moveTo(canvas.width / 2, 0);
	ctx.lineTo(canvas.width / 2, canvas.height);
	ctx.strokeStyle = "#FFF";
	ctx.stroke();
	ctx.closePath();
  
	ctx.beginPath();
	ctx.arc(ballX, ballY, ballRadius, 0, Math.PI * 2);
	ctx.fill();
	ctx.closePath();
  
	ctx.fillRect(0, leftPaddleY, paddleWidth, paddleHeight);
  
	ctx.fillRect(canvas.width - paddleWidth, rightPaddleY, paddleWidth, paddleHeight);
  
	ctx.fillText("Score: " + leftPlayerScore, 10, 20);
	ctx.fillText("Score: " + rightPlayerScore, canvas.width - 70, 20);
  }
  

function loop() {
	if (gameRunning == true)
		update();
	draw();
	animationId = requestAnimationFrame(loop);
}

loop();