import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.117.1/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

// var canvas2 = document.getElementById("canvas");
// var ctx = canvas2.getContext("2d");

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 900 / 600, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
renderer.setSize(900, 600);

camera.position.z = 450;

const controls = new OrbitControls( camera, renderer.domElement );

function animate(cylinder) {
	requestAnimationFrame( animate );

	cylinder.rotation.x += 0.01;
	cylinder.rotation.z += 0.01;
	cylinder.rotation.y += 0.01;

	renderer.render( scene, camera );
}

function gameRenderer(data) {
	scene.remove(...scene.children);
	const geometry = new THREE.CylinderGeometry( data.paddleWidth, data.paddleWidth, data.paddleHeight, 20 ); 
	const material = new THREE.MeshBasicMaterial( {color: 0x00ff00} ); 
	const geometryBall = new THREE.SphereGeometry( 15, 32, 16 ); 
	const materialBall = new THREE.MeshBasicMaterial( { color: 0xffff00 } ); 
	
	const sphere = new THREE.Mesh( geometryBall, materialBall); 

	const cylinderRight = new THREE.Mesh( geometry, material);
	const cylinderLeft = new THREE.Mesh( geometry, material);
	const sceneWidth= 900;
    const cylinderWidth = 1; 
    const cylinderPositionX = (sceneWidth / 2) - (cylinderWidth / 2);

	
    cylinderRight.position.set(cylinderPositionX, data.rightPaddleY, 0);
    cylinderLeft.position.set(-cylinderPositionX, data.leftPaddleY, 0);
	sphere.position.set(data.x, data.y, 0);
	
	// console.log(sphere.position.x);
	// console.log(sphere.position.y);
	// console.log(sphere.position.z);
	scene.add(cylinderRight);
	scene.add(cylinderLeft);
	scene.add( sphere );

	
	renderer.render( scene, camera );
}

// animate();

const gameSocket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/ws-game/'
);

let lastPingTime = performance.now();

gameSocket.onmessage = function(e) {
    const message = JSON.parse(e.data);
	// console.log(message);
    // draw(message);
	gameRenderer(message);
    
    const currentTime = performance.now();
    const pingDelay = currentTime - lastPingTime;
    // console.log("Ping delay:", pingDelay, "ms");

	if (message.winner == 'leftWin')
		playerWin('left')
	else if (message.winner == 'rightWin')
		playerWin('right')

    lastPingTime = currentTime;
	// console.log("ping = ", lastPingTime);
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

document.querySelector('#stopButton').onclick = function(e) {
	gameSocket.send(JSON.stringify({
		'message': 'stopButton'
	}));
};

document.addEventListener('keydown', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
            'message': 'wPressed'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'message': 'sPressed'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'message': 'upPressed'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'message': 'downPressed'
		}));
	}
});


document.addEventListener('keyup', function(event) {
    if (event.key === 'w') {
        gameSocket.send(JSON.stringify({
            'message': 'wRelease'
        }));
    }
	else if (event.key === 's') {
		gameSocket.send(JSON.stringify({
			'message': 'sRelease'
		}));
	}
	else if (event.key === 'ArrowUp') {
		gameSocket.send(JSON.stringify({
			'message': 'upRelease'
		}));
	}
	else if (event.key === 'ArrowDown') {
		gameSocket.send(JSON.stringify({
			'message': 'downRelease'
		}));
	}
});


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
  
	ctx.fillRect(0, data.leftPaddleY, data.paddleWidth, data.paddleHeight);
  
	ctx.fillRect(data.width - data.paddleWidth, data.rightPaddleY, data.paddleWidth, data.paddleHeight);
  
	ctx.fillText("Score: " + data.leftPlayerScore, 10, 20);
	ctx.fillText("Score: " + data.rightPlayerScore, data.width - 70, 20);
  }

function playerWin(player) {
	var message = "Congratulations! " + player + " win!";
	// var myParagraph = document.getElementById("scoreMessage");
	// myParagraph.innerText = message; 
}

