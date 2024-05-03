import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { EffectComposer } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/RenderPass.js";

import { animationData } from './animation.js';
import { animate } from './animation.js';
import * as utils from './utils.js';
import * as load from './loader.js';

import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(45, 1920/1080, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
scene.background = new THREE.Color(0x0d3452);
renderer.setSize(1920, 1080);
camera.position.set( 0, 0, 500 ); 
camera.rotation.set( -Math.PI / 6, 0, 0 ); 
// camera.position.set( 0, -155, 80 ); // position de la camera pour le jeu

var trailPositions = [];

const controls = new OrbitControls(camera, renderer.domElement);

// Light
// const light = new THREE.DirectionalLight(0x0096c7, 1.5);
const light = new THREE.DirectionalLight(0xFF85FB, 2);
light.position.set(0, 0, 10);

const geometryBall1 = new THREE.SphereGeometry(0, 10, 10);
const materialBall1 = new THREE.MeshToonMaterial({ color: 0xfcca46});
let spotLight = new THREE.Mesh(geometryBall1, materialBall1);
spotLight.position.set(20, 50, -15);
scene.add(spotLight);

const spotLight1 = new THREE.DirectionalLight(0xffcb77, 1);
spotLight1.position.set(100, 0, 60);

const spotLight2 = new THREE.AmbientLight(0x00b4d8, 0.1);
spotLight2.position.set(0, 50, -400);

// Activate shadows in the renderer
renderer.shadowMap.enabled = true;

// Composer pour la scène principale
export const composer = new EffectComposer(renderer);
const renderScene = new RenderPass(scene, camera);
composer.addPass(renderScene);

export var sphere;
export var cylinderRight;
export var cylinderLeft;

export var colorsBlue = [0x00f9ff, 0x00d2ff, 0x009fff, 0x0078ff, 0x0051ff, 0x0078ff, 0x009fff, 0x00d2ff];
export var colorsGreen = [0x132A13, 0x31572C, 0x4F772D, 0x90A955, 0xECF39E, 0x90A955, 0x4F772D, 0x31572C];
export var colorsYellow = [0xFCEC5D, 0xFCDC5D, 0xFCCC5D, 0xFCB75D, 0xFCAC5D, 0xFCB75D, 0xFCDC5D, 0xFCDC5D];
export var colorsOrange = [0xFF9E00, 0xFF8500, 0xFF6D00, 0xFF5400, 0xFF4800, 0xFF5400, 0xFF6D00, 0xFF8500];
export var colorPalettes = [colorsBlue, colorsGreen, colorsYellow, colorsOrange];
export let colorBall = colorsBlue;

export let scoreRight = 0
export let scoreLeft = 0
export let explosion = false;
export let collisionX = 0;
export let collisionY = 0;
export let initialSpeed = 0.8;
export let collisionPaddle = false;

export let light1;
export let light2;
export let light3;

export var sceneHeight = 70;

// scenes
export var start = true; // A REMETTRE A FALSE
export var sceneHandler = 0;

animate();

export function gameRenderer(data) {
	utils.clearScene(); 
    animationData.ballFall = true;
    scene.add(load.tree);
    scene.add(spotLight);
	scene.add(light);
	scene.add(spotLight1);
	scene.add(spotLight2);

    // console.log(camera.position.x);
    // ballFall = true;console.log(camera.position.y);
    // console.log(camera.position.z);

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
	
	// Background plane
	const geometryPlane = new THREE.PlaneGeometry(data.width * 2, data.height * 2);
	const materialPlane = new THREE.MeshStandardMaterial({ color: 0x333333, side: THREE.DoubleSide, metalness: 0.5, roughness: 0.5 });
	const plane = new THREE.Mesh(geometryPlane, materialPlane);
	plane.position.z = -2;
	plane.receiveShadow = true;
	// scene.add(plane);
	
	// Paddles
	const geometry = new THREE.CapsuleGeometry(data.paddleWidth, data.paddleHeight, 20);
	const material = new THREE.MeshToonMaterial({ color: 0xffffff}); 
	cylinderRight = new THREE.Mesh(geometry, material);
	cylinderLeft = new THREE.Mesh(geometry, material);
	cylinderRight.position.set(data.rightPaddleX, data.rightPaddleY + sceneHeight, 0);
	cylinderLeft.position.set(data.leftPaddleX, data.leftPaddleY + sceneHeight, 0);
	cylinderRight.castShadow = true; 
	cylinderLeft.castShadow = true; 
	
	// Ball
	const geometryBall = new THREE.SphereGeometry(data.ballRadius, 20, 20);
	const materialBall = new THREE.MeshToonMaterial({ color: 0xffffff});
	sphere = new THREE.Mesh(geometryBall, materialBall);
	sphere.position.set(data.x, data.y + sceneHeight, 0);
	// sphere.position.set(20, 50, -15);

	// if (start) {
	// 	sphere.position.set(data.x, data.y, 0);
	// 	scene.add(sphere);
	// } else {
	// 	sphere.position.set(data.x, data.y, 40);
	// }
	
	// const materialTrail = new THREE.MeshToonMaterial({ color: 0xffffff, transparent:true});
	// if (start)
	// {
	// 	trailPositions.push(sphere.position.clone());
	// 	if (trailPositions.length > 15 || explosion === true) {
	// 		trailPositions.shift();
	// 	}
	// }

	// scene.children
	// 	.filter(obj => obj.userData.isTrailSphere)
	// 	.forEach(obj => scene.remove(obj));

	// var size = 0.1;
	// trailPositions.forEach(position => {
	// 	const trailSphere = new THREE.Mesh(geometryBall, materialTrail);
	// 	trailSphere.position.copy(position);
	// 	trailSphere.scale.multiplyScalar(size);
	// 	if (size < 1)
	// 		size += 0.08;
	// 	trailSphere.userData.isTrailSphere = true;
	// 	materialTrail.opacity = 0.5;
	// 	scene.add(trailSphere);
	// });

	// if (explosion) {
	// 	scene.children
	// 		.filter(obj => obj.userData.isTrailSphere)
	// 		.forEach(obj => scene.remove(obj));
	// } else {
	// 	trailPositions.push(sphere.position.clone());
	// 	if (trailPositions.length > 15) {
	// 		trailPositions.shift();
	// 	}
	
	// 	scene.children
	// 		.filter(obj => obj.userData.isTrailSphere)
	// 		.forEach(obj => scene.remove(obj));
	
	// 	var size = 0.1;
	// 	trailPositions.forEach(position => {
	// 		const trailSphere = new THREE.Mesh(geometryBall, materialTrail);
	// 		trailSphere.position.copy(position);
	// 		trailSphere.scale.multiplyScalar(size);
	// 		if (size < 1)
	// 			size += 0.08;
	// 		trailSphere.userData.isTrailSphere = true;
	// 		materialTrail.opacity = 0.5;
	// 		scene.add(trailSphere);
	// 	});
	// }

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

	if (animationData.intro === 4){
		scene.add(light2);
		scene.add(light1);
		scene.add(light3);

		scene.add(line);
		scene.add(cylinderRight);
		scene.add(cylinderLeft);
		scene.add(sphere);
	}
	

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


