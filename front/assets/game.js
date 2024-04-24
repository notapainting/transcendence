import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { EffectComposer } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/UnrealBloomPass.js";
import { AfterimagePass } from 'https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/AfterimagePass.js';
import { GlitchPass } from 'https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/GlitchPass.js';

import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 900 / 600, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
scene.background = new THREE.Color(0x333333);
renderer.setSize(900, 600);
camera.position.set( 0, -70, 80 );

var trailPositions = [];

const controls = new OrbitControls(camera, renderer.domElement);

// Light
const light = new THREE.DirectionalLight(0xe5d0ff, 1);
light.position.set(0, 0, 1);

// Activate shadows in the renderer
renderer.shadowMap.enabled = true;

// Composer pour la scène principale
const composer = new EffectComposer(renderer);
const renderScene = new RenderPass(scene, camera);
composer.addPass(renderScene);

var startGame = false;
var start = false;

var colorsBlue = [0x00f9ff, 0x00d2ff, 0x009fff, 0x0078ff, 0x0051ff, 0x0078ff, 0x009fff, 0x00d2ff];
var colorsViolet = [0x4c005a, 0x6a1292, 0x8436a1, 0xa34bb4, 0xde70ec, 0xa34bb4, 0x8436a1, 0x6a1292];
var colorsPink = [0xffc2cd, 0xff93ac, 0xff6289, 0xfc3468, 0xff084a, 0xfc3468, 0xff6289, 0xff93ac];
var colorPalettes = [colorsViolet, colorsBlue, colorsPink];
let colorBall = colorsViolet;

var colorTransitionTime = 2000;
var colorStartTime = Date.now();

let scoreRight = 0
let scoreLeft = 0
let explosion = false;
let collisionX = 0;
let collisionY = 0;
let initialSpeed = 0.8;

let acceleration = 9.8;
let bounce_distance = 40;
let time_step = 0.04;
let time_counter = Math.sqrt(bounce_distance * 2 / acceleration);
let initial_speed = acceleration * time_counter;
let bounce_height_factor = 1;

let light1;
let light2;
let light3;

function createParticle() {
    var geometry = new THREE.BufferGeometry();
    var vertices = new Float32Array([collisionX, collisionY, 0]);

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

    var randomColor = colorBall[Math.floor(Math.random() * colorBall.length)];
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

    if(startGame === true)
    {
        scene.add(sphere);
        if (sphere.position.z < 0) {
            time_counter = 0;
            bounce_height_factor *= 0.5;
        }
        let adjusted_initial_speed = initial_speed * bounce_height_factor;
        sphere.position.z = 0 + adjusted_initial_speed * time_counter - 0.5 * acceleration * time_counter * time_counter;
        if (sphere.position.z <= 0 && adjusted_initial_speed <= 0.5) {
            startGame = false;
            start = true;
        } else {
            time_counter += time_step;
            light3.position.set(sphere.position.x, sphere.position.y, sphere.position.z);
        }
    }
    if (explosion === true) {
        scene.children
            .filter(obj => obj.userData.isTrailSphere)
            .forEach(obj => scene.remove(obj));
        for (var i = 0; i < 100; i++) {
			createParticle();
        }
        explosion = false;
    } 
	if (collisionPaddle === true)
	{
		var randomIndex;
		do {
			randomIndex = Math.floor(Math.random() * colorPalettes.length);
		} while (colorBall === colorPalettes[randomIndex]);
	
		colorBall = colorPalettes[randomIndex];
		collisionPaddle = false;
	}

    composer.render();
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

function interpolateColor(color) {
    const now = Date.now();
    const elapsedTime = now - colorStartTime;
    const timePerColor = colorTransitionTime / color.length;
    const colorIndexStart = Math.floor(elapsedTime / timePerColor) % color.length;
    const colorIndexEnd = (colorIndexStart + 1) % color.length;
    const ratio = (elapsedTime % timePerColor) / timePerColor;

    const colorStart = new THREE.Color(color[colorIndexStart]);
    const colorEnd = new THREE.Color(color[colorIndexEnd]);

    const interpolatedColor = new THREE.Color().copy(colorStart).lerp(colorEnd, ratio);
    return interpolatedColor.getHex();
}

function createTrailParticles(position, color) {
    const numParticles = 5; 
    const particleSize = 0.5;
    const trailSpeed = 0.1;

    for (let i = 0; i < numParticles; i++) {
        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array([position.x, position.y, position.z]);

        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

        const material = new THREE.PointsMaterial({ color: color, size: particleSize, opacity: 1.0, transparent: true });

        const particle = new THREE.Points(geometry, material);
        scene.add(particle);

        const direction = new THREE.Vector3(
            Math.random() - 0.5,
            Math.random() - 0.5,
            Math.random() - 0.5
        ).normalize();

        const speed = trailSpeed * Math.random(); 
        var distance = 10;

        const update = function () {
            const positionAttribute = particle.geometry.getAttribute('position');
            const currentPosition = new THREE.Vector3().fromBufferAttribute(positionAttribute, 0);
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
}

function gameRenderer(data) {
	clearScene(); 
    startGame = true;

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
    const material = new THREE.MeshToonMaterial({ color: 0xffffff}); 
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
    const materialBall = new THREE.MeshToonMaterial({ color: 0xffffff});
    sphere = new THREE.Mesh(geometryBall, materialBall);
    sphere.position.set(data.x, data.y, 0);
    scene.add(sphere);

    if (start) {
        sphere.position.set(data.x, data.y, 0);
        scene.add(sphere);
    } else {
        sphere.position.set(data.x, data.y, 40);
    }
    
    const materialTrail = new THREE.MeshToonMaterial({ color: 0xffffff, transparent:true});
    if (start)
    {
        trailPositions.push(sphere.position.clone());
        if (trailPositions.length > 15 || explosion === true) {
            trailPositions.shift();
        }
    }

    scene.children
        .filter(obj => obj.userData.isTrailSphere)
        .forEach(obj => scene.remove(obj));

    var size = 0.1;
    trailPositions.forEach(position => {
        const trailSphere = new THREE.Mesh(geometryBall, materialTrail);
        trailSphere.position.copy(position);
        trailSphere.scale.multiplyScalar(size);
        if (size < 1)
            size += 0.08;
        trailSphere.userData.isTrailSphere = true;
        materialTrail.opacity = 0.5;
        scene.add(trailSphere);
    });

	if (explosion) {
		scene.children
			.filter(obj => obj.userData.isTrailSphere)
			.forEach(obj => scene.remove(obj));
	} else {
		trailPositions.push(sphere.position.clone());
		if (trailPositions.length > 15) {
			trailPositions.shift();
		}
	
		scene.children
			.filter(obj => obj.userData.isTrailSphere)
			.forEach(obj => scene.remove(obj));
	
		var size = 0.1;
		trailPositions.forEach(position => {
			const trailSphere = new THREE.Mesh(geometryBall, materialTrail);
			trailSphere.position.copy(position);
			trailSphere.scale.multiplyScalar(size);
			if (size < 1)
				size += 0.08;
			trailSphere.userData.isTrailSphere = true;
			materialTrail.opacity = 0.5;
			scene.add(trailSphere);
		});
	}
    // const trailColor = new THREE.Color(0xffffff);
    // createTrailParticles(sphere.position, trailColor);
    
    // Lights
	const lightColor = interpolateColor(colorBall); 
    const lightIntensity = 300;
    const lightDistance = 50;
    light1 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
    light1.position.set(data.width - 5, data.rightPaddleY, cylinderRight.position.z + 5);
    light2 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
    light2.position.set(-data.width + 5, data.leftPaddleY, cylinderLeft.position.z + 5);
    light3 = new THREE.PointLight(lightColor, lightIntensity, lightDistance);
    light3.position.set(data.x, data.y, sphere.position.z);
    scene.add(light);
    scene.add(light1);
    scene.add(light2);
    scene.add(light3);

	// Explosion collision
    if (data.leftPlayerScore > scoreLeft) {
        
        collisionX = data.collisionX;
        collisionY = data.collisionY;
        scoreLeft++;
        trailPositions = [];
		explosion = true;
		trailPositions = [];
    }
    if (data.rightPlayerScore > scoreRight) {
        collisionX = data.collisionX;
        collisionY = data.collisionY;
        scoreRight++;
        trailPositions = [];
		explosion = true;
		trailPositions = [];
    }
    if (data.speed != initialSpeed)
    {
		collisionPaddle = true;
        initialSpeed = data.speed;
    }
    
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    composer.render();
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
    if (start)
    {
        gameSocket.send(JSON.stringify({
            'message': 'startButton'
        }));
    }
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

