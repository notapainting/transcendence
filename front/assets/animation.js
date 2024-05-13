import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import * as load from './loader.js';
import { composer } from './game.js';
import * as game from './game.js';
import * as utils from './utils.js';

let acceleration = 9.8;
let bounce_distance = 40;
let time_step = 0.06;
let time_counter = Math.sqrt(bounce_distance * 2 / acceleration);
let initial_speed = acceleration * time_counter;
let bounce_height_factor = 1;
var target = new THREE.Vector3(0, 0, 0);

const startGameButton = document.getElementById('startGame');
const localGameButton = document.getElementById('localGame');
const exitButton = document.getElementById('exit');

export const animationData = {
	ballFall: false,
	intro: 0
  }; // A REMETTRE A FALSE

localGameButton.addEventListener('click', () => {
	animationData.intro = 1;
	// startGameButton.style.display = 'none';
	localGameButton.style.display = 'none';
	exitButton.style.display = 'none';
});

startGameButton.addEventListener('click', () => {
	console.log("position:");
	console.log(game.camera.position.x);
	console.log(game.camera.position.y);
	console.log(game.camera.position.z);
	console.log("rotation:");
	console.log(game.camera.rotation.x);
	console.log(game.camera.rotation.y);
	console.log(game.camera.rotation.z);

	var cameraDirection = new THREE.Vector3();
	game.camera.getWorldDirection(cameraDirection);
	console.log('getWorldDirection:', cameraDirection);

	var lookAtPoint = new THREE.Vector3();
	lookAtPoint.copy(game.camera.position).add(cameraDirection);
	console.log('La caméra regarde vers le point :', lookAtPoint);
});

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
  }

export async function animate() {
    requestAnimationFrame(animate);

	// animation balançoire
	if (load.mixer)
		load.mixer.update(0.01);

	if (load.sky)
		load.sky.rotation.y += 0.001;

	// animation rotation arbre premiere scene
	// if (load.tree && animationData.intro === 0) {
	// 	var initialPos = new THREE.Vector3(0, 0, 0);
	// 	var finalPos = new THREE.Vector3(20, -60, 400);
		
	// 	var initialAng = new THREE.Vector3(0, Math.PI / 2, 0);
	// 	var finalAng = new THREE.Vector3(Math.PI / 16, -Math.PI / 8, 0);
		
	// 	utils.transRot3D(load.tree, initialPos, finalPos, initialAng, finalAng, 75, 1);
	// }
	
	// afficher les boutons
	if (animationData.intro === 0) {
		startGameButton.style.display = 'block';
		localGameButton.style.display = 'none';
		exitButton.style.display = 'none';
	}

	// entrer en jeu
	if (animationData.intro === 1) {
		if (load.intro.position.z < 10)
		load.intro.position.z += 0.05;
	}

	// if (animationData.intro === 3) {
	// 	await sleep(1000);

	// 	var initialPosCam = new THREE.Vector3(-400, 115, 269);
	// 	var finalPosCam = new THREE.Vector3(-100, 160, 75);

	// 	var initialTarget = new THREE.Vector3(0, 0, 0);
	// 	var finalTarget = new THREE.Vector3(20, 50, -15);

	// 	utils.translationTargetXYZ(target, initialTarget, finalTarget, 100, 3);
	// 	utils.translationCameraXYZ(game.camera, target, initialPosCam, finalPosCam, 130, 4);
	// }

	if (animationData.intro === 4){
		game.scene.add(game.sphere);
		game.scene.add(game.cylinderLeft);
		game.scene.add(game.cylinderRight);
	}

	if (game.sceneHandler === 1)
	{
		if(animationData.ballFall === true)
		{
			game.scene.add(game.sphere);
			if (game.sphere.position.z < 0) {
				time_counter = 0;
				bounce_height_factor *= 0.5;
			}
			let adjusted_initial_speed = initial_speed * bounce_height_factor;
			game.sphere.position.z = 0 + adjusted_initial_speed * time_counter - 0.5 * acceleration * time_counter * time_counter;
			if (game.sphere.position.z <= 0 && adjusted_initial_speed <= 0.5) {
				animationData.ballFall = false;
				game.start = true;
			} else {
				time_counter += time_step;
				gamelight3.position.set(game.sphere.position.x, game.sphere.position.y, game.sphere.position.z);
			}
		}
		if (game.explosion === true) {
			game.scene.children
				.filter(obj => obj.userData.isTrailSphere)
				.forEach(obj => game.scene.remove(obj));
			for (var i = 0; i < 100; i++) {
				createParticle();
			}
			game.explosion = false;
		} 
		if (game.collisionPaddle === true)
		{
			var randomIndex;
			do {
				randomIndex = Math.floor(Math.random() * game.colorPalettes.length);
			} while (game.colorBall === colorPalettes[randomIndex]);
		
			game.colorBall = game.colorPalettes[randomIndex];
			game.collisionPaddle = false;
		}
	}


    composer.render();
}