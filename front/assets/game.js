import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

// var canvas2 = document.getElementById("canvas");
// var ctx = canvas2.getContext("2d");

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 900 / 600, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
scene.background = new THREE.Color(0x333333);
renderer.setSize(900, 600);

camera.position.set( 0, -70, 80 );

const controls = new OrbitControls( camera, renderer.domElement );

// Light
const light = new THREE.DirectionalLight(0xe5d0ff, 1);
light.position.set(0, 0, 1);

// Activer les ombres dans le renderer
renderer.shadowMap.enabled = false;

var colors = [0x7F00FF, 0xe5d0ff, 0xbf8bff, 0x5b00ba, 0x6900a3, 0x51007e, 0x9700cc];

let scoreRight = 0
let scoreLeft = 0
let explosion = false;
let collisionX = 0;
let collisionY = 0;

function createParticle() {
    var geometry = new THREE.BufferGeometry();
    var vertices = new Float32Array([collisionX, collisionY, 0]);

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

    var randomColor = colors[Math.floor(Math.random() * colors.length)];

    var material = new THREE.PointsMaterial({ color: randomColor, size: 1.5 });


    var particle = new THREE.Points(geometry, material);
    scene.add(particle);

    var direction = new THREE.Vector3(
        Math.random() - 0.5,
        Math.random() - 0.5,
        Math.random() - 0.5
    ).normalize();

    var speed = 0.6; 
    var distance = 10;

    var update = function () {
        var positionAttribute = particle.geometry.getAttribute('position');
        var currentPosition = new THREE.Vector3().fromBufferAttribute(positionAttribute, 0);
        currentPosition.addScaledVector(direction, speed);
        positionAttribute.setXYZ(0, currentPosition.x, currentPosition.y, currentPosition.z);
        positionAttribute.needsUpdate = true;
        distance -= speed;
        if (distance <= 0) {
            scene.remove(particle);
            cancelAnimationFrame(animationId);
        }
    };

    var animationId = requestAnimationFrame(function animate() {
        update();
        animationId = requestAnimationFrame(animate);
    });
}

function animate() {
    requestAnimationFrame(animate);

    if (explosion === true) {
        for (var i = 0; i < 100; i++) {
            createParticle();
        }
        explosion = false;
    }
    renderer.render(scene, camera);

}

animate();

function clearScene() {
    let toRemove = [];
    scene.children.forEach((child) => {
        if (child.type !== 'Points') {
            toRemove.push(child);
        }
    });
    toRemove.forEach((child) => {
        scene.remove(child);
    });
}

function gameRenderer(data) {
	clearScene(); 
	
    // Game limits
    const materialLine = new THREE.LineBasicMaterial({ color: 0xdabcff });
    const points = [];
    points.push(new THREE.Vector3(data.width, -data.height, 0));
    points.push(new THREE.Vector3(data.width, data.height, 0));
    points.push(new THREE.Vector3(-data.width, data.height, 0));
    points.push(new THREE.Vector3(-data.width, -data.height, 0));
    points.push(new THREE.Vector3(data.width, -data.height, 0));
    points.push(new THREE.Vector3(0, -data.height, 0));
    points.push(new THREE.Vector3(data.heigt, 0, 0));
    points.push(new THREE.Vector3(0, data.height, 0));
    const geometryLine = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometryLine, materialLine);
	const geometryCircle = new THREE.CircleGeometry(7, 32);
	const edges = new THREE.EdgesGeometry(geometryCircle);
	const materialEdges = new THREE.LineBasicMaterial({ color: 0xdabcff });
	const circleEdges = new THREE.LineSegments(edges, materialEdges);
	scene.add(circleEdges);
    scene.add(line);
	
    // Background plane
    const geometryPlane = new THREE.PlaneGeometry(data.width * 2, data.height * 2);
    const materialPlane = new THREE.MeshStandardMaterial({ color: 0x333333, side: THREE.DoubleSide, metalness: 0.5, roughness: 0.5 });
    const plane = new THREE.Mesh(geometryPlane, materialPlane);
    plane.position.z = -2;
    plane.receiveShadow = true;
    scene.add(plane);
	
    // Paddles
    const geometry = new THREE.CapsuleGeometry(data.paddleWidth, data.paddleHeight, 20);
    const material = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x7F00FF, emissiveIntensity: 10 }); 
    let cylinderRight = new THREE.Mesh(geometry, material);
    let cylinderLeft = new THREE.Mesh(geometry, material);
    cylinderRight.position.set(data.width - 5, data.rightPaddleY, 0);
    cylinderLeft.position.set(-data.width + 5, data.leftPaddleY, 0);
    cylinderRight.castShadow = true; 
    cylinderLeft.castShadow = true; 
    scene.add(cylinderRight);
    scene.add(cylinderLeft);
	
    // Ball
    const geometryBall = new THREE.SphereGeometry(data.ballRadius, 20, 20);
    const materialBall = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x7F00FF, emissiveIntensity: 20 });
    let sphere = new THREE.Mesh(geometryBall, materialBall);
    sphere.position.set(data.x, data.y, 0);
    scene.add(sphere);

    // Lights
    const light1 = new THREE.PointLight(0x7F00FF, 400, 50); 
    light1.position.set(data.width - 5, data.rightPaddleY, 10);
    const light2 = new THREE.PointLight(0x7F00FF, 400, 50); 
    light2.position.set(-data.width + 5, data.leftPaddleY, 10);
    const light3 = new THREE.PointLight(0x7F00FF, 400, 50); 
    light3.position.set(data.x, data.y, 10);
    scene.add(light);
    scene.add(light1);
    scene.add(light2);
    scene.add(light3);


	// Explosion collision
    if (data.leftPlayerScore > scoreLeft) {
        collisionX = data.collisionX;
        collisionY = data.collisionY;
        scoreLeft++;
		explosion = true;
    }
    if (data.rightPlayerScore > scoreRight) {
        collisionX = data.collisionX;
        collisionY = data.collisionY;
        scoreRight++;
		explosion = true;
    }

    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.render(scene, camera);
}


const gameSocket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/ws-game/'
);

let lastPingTime = performance.now();

gameSocket.onmessage = function(e) {
    const message = JSON.parse(e.data);
    // explosion(message);
	
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

function playerWin(player) {
	var message = "Congratulations! " + player + " win!";
	// var myParagraph = document.getElementById("scoreMessage");
	// myParagraph.innerText = message; 
}

