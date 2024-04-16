import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.117.1/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

// var canvas2 = document.getElementById("canvas");
// var ctx = canvas2.getContext("2d");

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 900 / 600, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
renderer.setSize(900, 600);

// camera.position.z = 50;
camera.position.set( -50, -50, 50 );


const controls = new OrbitControls( camera, renderer.domElement );

// Créer une lumière directionnelle
const light = new THREE.DirectionalLight(0xff0000, 1);
light.position.set(0, 0, 1);


// Activer les ombres dans le renderer
renderer.shadowMap.enabled = false;


function animate(cylinder) {
	requestAnimationFrame( animate );

	cylinder.rotation.x += 0.01;
	cylinder.rotation.z += 0.01;
	cylinder.rotation.y += 0.01;

	renderer.render( scene, camera );
}

function gameRenderer(data) {
	scene.remove(...scene.children);

	// Game limits
	const materialLine = new THREE.LineBasicMaterial( { color: 0xffffff } );
	const points = [];
	points.push( new THREE.Vector3( data.width, -data.height, 0 ) );
	points.push( new THREE.Vector3( data.width, data.height, 0 ) );
	points.push( new THREE.Vector3( -data.width, data.height, 0 ) );
	points.push( new THREE.Vector3( -data.width, -data.height, 0 ) );
	points.push( new THREE.Vector3( data.width, -data.height, 0 ) );
	const geometryLine = new THREE.BufferGeometry().setFromPoints( points );
	const line = new THREE.Line( geometryLine, materialLine );
	scene.add( line );

	//Paddles
	const geometry = new THREE.CylinderGeometry( data.paddleWidth, data.paddleWidth, data.paddleHeight, 20 ); 
	const material = new THREE.MeshPhongMaterial( {color: 0xffffff} ); 
	const cylinderRight = new THREE.Mesh( geometry, material);
	const cylinderLeft = new THREE.Mesh( geometry, material);
    cylinderRight.position.set(data.width - 5, data.rightPaddleY, 0);
    cylinderLeft.position.set(-data.width + 5, data.leftPaddleY, 0);
	scene.add(cylinderRight);
	scene.add(cylinderLeft);

	//Ball
	const geometryBall = new THREE.SphereGeometry( data.ballRadius, 20, 20); 
	const materialBall = new THREE.MeshPhongMaterial( { color: 0xffff00 } ); 
	const sphere = new THREE.Mesh( geometryBall, materialBall); 
	sphere.position.set(data.x, data.y, 0);
	scene.add(sphere);

	renderer.shadowMap.type = THREE.PCFSoftShadowMap;
	scene.add(light);
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

