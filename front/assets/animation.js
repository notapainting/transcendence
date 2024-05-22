import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import * as load from './loader.js';
import { composer } from './game.js';
import * as game from './game.js';
import * as utils from './utils.js';
import { gameData } from './game.js';
import { loadData } from './loader.js';

export var colorsBlue = [0x00f9ff, 0x00d2ff, 0x009fff, 0x0078ff, 0x0051ff, 0x0078ff, 0x009fff, 0x00d2ff];
export var colorsGreen = [0x132A13, 0x31572C, 0x4F772D, 0x90A955, 0xECF39E, 0x90A955, 0x4F772D, 0x31572C];
export var colorsYellow = [0xFCEC5D, 0xFCDC5D, 0xFCCC5D, 0xFCB75D, 0xFCAC5D, 0xFCB75D, 0xFCDC5D, 0xFCDC5D];
export var colorsOrange = [0xFF9E00, 0xFF8500, 0xFF6D00, 0xFF5400, 0xFF4800, 0xFF5400, 0xFF6D00, 0xFF8500];
export var colorPalettes = [colorsBlue, colorsGreen, colorsYellow, colorsOrange];
export let colorBall = colorsBlue;

let acceleration = 9.8;
let bounce_distance = 40;
let time_step = 0.06;
let time_counter = Math.sqrt(bounce_distance * 2 / acceleration);
let initial_speed = acceleration * time_counter;
let bounce_height_factor = 1;
var target = new THREE.Vector3(0, 0, 0);

var p1 = { x: -45, y: -25 };
var p2 = { x: 45, y: -25 };
var p3 = { x: 45, y: 25 };
var p4 = { x: -45, y: 25 };

export var bonusTime = 1;

const startGameButton = document.getElementById('startGame');
const localGameButton = document.getElementById('localGame');
const exitButton = document.getElementById('exit');

export const animationData = {
	ballFall: false,
	intro: 0
  };

localGameButton.addEventListener('click', () => {
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

	// models animation
	if (load.mixer)
		load.mixer.update(0.01);
	if (loadData.mixerBonus)
		loadData.mixerBonus.update(0.01);
	if (loadData.mixerMalus)
		loadData.mixerMalus.update(0.01); 
	if (loadData.mixerBoost)
		loadData.mixerBoost.update(0.01); 

	// if (game.sceneHandler === 1)
	// {
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
				gameData.start = true;
			} else {
				time_counter += time_step;
				game.light3.position.set(game.sphere.position.x, game.sphere.position.y, game.sphere.position.z);
			}
		}
		if (gameData.explosion === true) {
			game.scene.children
				.filter(obj => obj.userData.isTrailSphere)
				.forEach(obj => game.scene.remove(obj));
			for (var i = 0; i < 150; i++) {
				utils.createParticle(game.collisionX, game.collisionY, 0.7, 15, 0);
			}
			gameData.explosion = false;
		} 
		if (gameData.catchBonus === true) {
			game.scene.children
				.filter(obj => obj.userData.isTrailSphere)
				.forEach(obj => game.scene.remove(obj));
			for (var i = 0; i < 100; i++) {
				utils.createParticle(game.sphere.position.x,game.sphere.position.y, 0.5, 10, game.lightBonus.color);
			}
			gameData.catchBonus = false;		
        } 
		if (gameData.catchMalus === true) {
			game.scene.children
				.filter(obj => obj.userData.isTrailSphere)
				.forEach(obj => game.scene.remove(obj));
			for (var i = 0; i < 100; i++) {
				utils.createParticle(game.sphere.position.x,game.sphere.position.y, 0.5, 10, game.lightMalus.color);
			}
			gameData.catchMalus = false;		
        } 
		if (gameData.collisionPaddle === true)
		{
			var randomIndex;
			do {
				randomIndex = Math.floor(Math.random() * colorPalettes.length);
			} while (colorBall === colorPalettes[randomIndex]);
		
			colorBall = colorPalettes[randomIndex];
			gameData.collisionPaddle = false;
		}
	// }

    composer.render();
}