import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { EffectComposer } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/RenderPass.js";

import { animationData } from './animation.js';
import { animate, colorBall } from './animation.js';
import * as utils from './utils.js';

import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

var width = window.innerWidth;
var height = window.innerHeight

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(45, width/height, 0.1, 1000);
// export const camera = new THREE.PerspectiveCamera(45, 600/900, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
scene.background = new THREE.Color(0x031d44);
renderer.setSize(width, height);
// renderer.setSize(600, 900);
camera.position.set( 0, -200, 115);
// camera.position.set( 0, -100, 85 ); // position de la camera pour le jeu

import * as load from './loader.js';

var trailPositions = [];

const controls = new OrbitControls(camera, renderer.domElement);

// Light
// const light = new THREE.DirectionalLight(0x0096c7, 1.5);
const light = new THREE.AmbientLight(0x3a86ff, 4);
light.position.set(0, 0, 0);
const lightWall = new THREE.DirectionalLight(0x3a86ff, 0);
lightWall.position.set(0, -400, 50);

const geometryBall1 = new THREE.SphereGeometry(0, 10, 10);
const materialBall1 = new THREE.MeshToonMaterial({ color: 0xfcca46});
let spotLight = new THREE.Mesh(geometryBall1, materialBall1);
spotLight.position.set(-90, 60, 1);

const spotLight1 = new THREE.DirectionalLight(0x0e7b7f, 7);
spotLight1.position.set(90, 60, 5);

const spotLight2 = new THREE.DirectionalLight(0x0e7b7f, 7);
spotLight2.position.set(-90, 60, 1);

// Activate shadows in the renderer
renderer.shadowMap.enabled = true;

// Composer pour la scène principale
export const composer = new EffectComposer(renderer);
const renderScene = new RenderPass(scene, camera);
composer.addPass(renderScene);

export var sphere;
export var cylinderRight;
export var cylinderLeft;

export let scoreRight = 0
export let scoreLeft = 0
export let collisionX = 0;
export let collisionY = 0;
export let initialSpeed = 0.8;

export let light1;
export let light2;
export let light3;

export var sceneHeight = 70;

// scenes
export var sceneHandler = 1;

export var randBonus = ['longPaddle'];
// export var randBonus = ['longPaddle', 'boost'];
export var randMalus = ['slow', 'shortPaddle', 'invertedKey'];
export var randEffect = ['hurricane', 'earthquake', 'glitch'];

var p1 = { x: -45, y: -25 };
var p2 = { x: 45, y: -25 };
var p3 = { x: 45, y: 25 };
var p4 = { x: -45, y: 25 };

export const gameData = {
	explosion: false,
	collisionPaddle: false,
	start: false,
	elapsedTime: 0,
	timerInterval: null,
	width: 0,
	height: 0,
	randomPoint: utils.getRandomPointInRectangle(p1, p2, p3, p4),
	bonus: null,
	malus: null,
	effect: null
};

export function gameRenderer(data) {
	utils.clearScene(); 
    animationData.ballFall = true;
    // scene.add(load.intro);
    // scene.add(spotLight);
	// scene.add(light);
	// scene.add(lightWall);
	// scene.add(spotLight1);
	// scene.add(spotLight2);

	gameData.width = data.width;
	gameData.height = data.height;

	// Game limits
	const materialLine = new THREE.LineBasicMaterial({ color: 0xdabcff });
	const points = [];
	points.push(new THREE.Vector3(data.width + 5, -data.height, 0));
	points.push(new THREE.Vector3(data.width + 5, data.height, 0));
	points.push(new THREE.Vector3(-data.width - 5, data.height, 0));
	points.push(new THREE.Vector3(-data.width - 5, -data.height, 0));
	points.push(new THREE.Vector3(data.width + 5, -data.height, 0));
	points.push(new THREE.Vector3(0, -data.height, 0));
	points.push(new THREE.Vector3(data.heigt, 0, 0));
	points.push(new THREE.Vector3(0, data.height, 0));
	const geometryLine = new THREE.BufferGeometry().setFromPoints(points);
	const line = new THREE.Line(geometryLine, materialLine);

	// Background plane
	const geometryPlane = new THREE.PlaneGeometry((data.width + 5) * 2, data.height * 2);
	const materialPlane = new THREE.MeshStandardMaterial({ color: 0x333333, side: THREE.DoubleSide, metalness: 0.5, roughness: 0.5 });
	const plane = new THREE.Mesh(geometryPlane, materialPlane);
	plane.position.z = -2;
	plane.receiveShadow = true;
	scene.add(plane);
	
	// Paddles
	const geometry = new THREE.CapsuleGeometry(data.paddleWidth, data.paddleHeight - 1, 20);
	const material = new THREE.MeshToonMaterial({ color: 0xffffff}); 
	cylinderRight = new THREE.Mesh(geometry, material);
	cylinderLeft = new THREE.Mesh(geometry, material);
	cylinderRight.position.set(data.rightPaddleX, data.rightPaddleY, 0);
	cylinderLeft.position.set(data.leftPaddleX, data.leftPaddleY, 0);
	cylinderRight.castShadow = true; 
	cylinderLeft.castShadow = true; 
	
	// Ball
	const geometryBall = new THREE.SphereGeometry(data.ballRadius, 20, 10);
	const materialBall = new THREE.MeshToonMaterial({ color: 0xffffff});
	sphere = new THREE.Mesh(geometryBall, materialBall);
	sphere.position.set(data.x, data.y, 0);

	if (gameData.start) {
		sphere.position.set(data.x, data.y, 0);
		scene.add(sphere);
	} else {
		sphere.position.set(data.x, data.y, 40);
	}
	
	const materialTrail = new THREE.MeshToonMaterial({ color: 0xffffff, transparent:true});
	if (gameData.start)
	{
		trailPositions.push(sphere.position.clone());
		if (trailPositions.length > 15 || gameData.explosion === true) {
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

	if (gameData.explosion) {
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

	// Lights
	const lightColor = utils.interpolateColor(colorBall); 
	const lightIntensity = 100;
	const lightDistance = 80;
	light1 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
	light1.position.set(data.width - 5, data.rightPaddleY, cylinderRight.position.z + 5);
	light2 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
	light2.position.set(-data.width + 5, data.leftPaddleY, cylinderLeft.position.z + 5);
	light3 = new THREE.PointLight(lightColor, lightIntensity, lightDistance);
	light3.position.set(data.x, data.y, sphere.position.z);

	// if (animationData.intro === 4){
		scene.add(light2);
		scene.add(light1);
		scene.add(light3);

		scene.add(line);
		scene.add(cylinderRight);
		scene.add(cylinderLeft);
		scene.add(sphere);
	// }

	// Explosion collision
	if (data.leftPlayerScore > scoreLeft) {
		collisionX = data.collisionX;
		collisionY = data.collisionY;
		scoreLeft++;
		trailPositions = [];
		gameData.explosion = true;
		trailPositions = [];
	}
	if (data.rightPlayerScore > scoreRight) {
		collisionX = data.collisionX;
		collisionY = data.collisionY;
		scoreRight++;
		trailPositions = [];
		gameData.explosion = true;
		trailPositions = [];
	}
	if (data.speed != initialSpeed)
	{
		gameData.collisionPaddle = true;
		initialSpeed = data.speed;
	}
    
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    composer.render();
}

animate();