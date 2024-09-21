import * as THREE from 'three';
import { EffectComposer } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/postprocessing/RenderPass.js";
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.117.1/examples/jsm/controls/OrbitControls.js';

import { animationData } from './animation.js';
import { animate } from './animation.js';
import { customData } from './custom.js';
import * as utils from './utils.js';

var width = window.innerWidth;
var height = window.innerHeight

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(45, width/height, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
scene.background = new THREE.Color(0x031d44);
renderer.setSize(width, height);
camera.position.set( 0, -100, 85 );

var canvas = document.createElement('canvas');
var context = canvas.getContext('2d');
canvas.width = 512;
canvas.height = 512;

// Dessiner du texte sur le canvas
context.fillStyle = 'white';
context.fillRect(0, 0, canvas.width, canvas.height);
context.font = '48px sans-serif';
context.fillStyle = 'black';
context.fillText('Bonjour, monde !', 50, 256);

// Créer une texture à partir du canvas
var texture = new THREE.CanvasTexture(canvas);

var material = new THREE.MeshBasicMaterial({ map: texture });
var geometry = new THREE.PlaneGeometry(50, 50);
var mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

export const clearThree = () => {renderer.clear();};

import * as load from './loader.js';

var trailPositions = [];

const controls = new OrbitControls(camera, renderer.domElement);

const geometryBall1 = new THREE.SphereGeometry(0, 10, 10);
const materialBall1 = new THREE.MeshToonMaterial({ color: 0xfcca46});
let spotLight = new THREE.Mesh(geometryBall1, materialBall1);
spotLight.position.set(-90, 60, 1);

// Light
const light = new THREE.AmbientLight(0x3a86ff, 4);
light.position.set(0, 0, 0);
const lightWall = new THREE.DirectionalLight(0x3a86ff, 0);
lightWall.position.set(0, -400, 50);
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
export var plane;
export var line = null;
var geometryBall;

export let scoreRight = 0
export let scoreLeft = 0
export let collisionX = 0;
export let collisionY = 0;
export let initialSpeed = 0.8;

export let light1;
export let light2;
export let light3;
export let lightBonus;
export let lightMalus;

export const gameData = {
	explosion: false,
	catchBonus: false,
	catchMalus: false,
	collisionPaddle: false,
	start: false,
	elapsedTime: 0,
	timerInterval: null,
	width: 0,
	height: 0,
	bonus: null,
	malus: null,
	effect: null,
	sceneHandler: 0
};

function clearTrail() {
    scene.children
        .filter(obj => obj.userData.isTrailSphere)
        .forEach(obj => scene.remove(obj));

    trailPositions = []; 
}

export function gameRenderer(data) {
    animationData.ballFall = true;
    if (data)
    {
        utils.clearScene(); 
		scene.add(load.intro);
		scene.add(spotLight);
		scene.add(light);
		scene.add(lightWall);
		scene.add(spotLight1);
		scene.add(spotLight2);
	
		gameData.width = data.width;
		gameData.height = data.height;
	
		// Game limits
		const materialLine = new THREE.LineBasicMaterial({ color: 0xdabcff });
		if (line === null)
		{
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
			line = new THREE.Line(geometryLine, materialLine);

			// Background plane
			const geometryPlane = new THREE.PlaneGeometry((data.width + 5) * 2, data.height * 2);
			const materialPlane = new THREE.MeshStandardMaterial({ color: 0x333333, side: THREE.DoubleSide, metalness: 0.5, roughness: 0.5, transparent: true, opacity: 0.5 });
			plane = new THREE.Mesh(geometryPlane, materialPlane);
			plane.position.z = -2;
			plane.receiveShadow = true;

			// Ball
			geometryBall = new THREE.SphereGeometry(data.ballRadius, 20, 10);
			const materialBall = new THREE.MeshToonMaterial({ color: 0xffffff});
			sphere = new THREE.Mesh(geometryBall, materialBall);
		}
	
		
		// Paddles
		const geometryR = new THREE.CapsuleGeometry(data.paddleWidth, data.paddleHeightR - 1, 20);
		const geometryL = new THREE.CapsuleGeometry(data.paddleWidth, data.paddleHeightL - 1, 20);
		const material = new THREE.MeshToonMaterial({ color: 0xffffff}); 
		cylinderRight = new THREE.Mesh(geometryR, material);
		cylinderLeft = new THREE.Mesh(geometryL, material);
		cylinderRight.position.set(data.rightPaddleX, data.rightPaddleY, 0);
		cylinderLeft.position.set(data.leftPaddleX, data.leftPaddleY, 0);
		cylinderRight.castShadow = true; 
		cylinderLeft.castShadow = true; 
		
		sphere.position.set(data.x, data.y, 0);
		
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

	
		// Lights
		const lightColor = utils.interpolateColor(customData.colorBall); 
		const lightIntensity = 100;
		const lightDistance = 80;
		light1 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
		light1.position.set(data.width - 5, data.rightPaddleY, cylinderRight.position.z + 5);
		light2 = new THREE.PointLight(lightColor, lightIntensity, lightDistance); 
		light2.position.set(-data.width + 5, data.leftPaddleY, cylinderLeft.position.z + 5);
		light3 = new THREE.PointLight(lightColor, lightIntensity, lightDistance);
		light3.position.set(data.x, data.y, sphere.position.z);
		lightBonus = new THREE.PointLight(0x90e0ef, 20, 0);	
		lightMalus = new THREE.PointLight(0xd62828, 20, 0);

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

		if (data.randomPointB && load.bonus){
			load.bonus.position.set(data.randomPointB.x, data.randomPointB.y, 0);
			lightBonus.position.set(data.randomPointB.x, data.randomPointB.y, 0);
			scene.add(load.bonus);
			scene.add(lightBonus);
		} 
		if (data.hitB === true)
			gameData.catchBonus = true;

		if (data.randomPointM && load.malus){
			load.malus.position.set(data.randomPointM.x, data.randomPointM.y, 0);
			lightMalus.position.set(data.randomPointM.x, data.randomPointM.y, 0);
			scene.add(load.malus);
			scene.add(lightMalus);
		} 
		if (data.hitM === true)
			gameData.catchMalus = true;

        if (data.x === 0 && data.y === 0)
            clearTrail();
	}

	if (gameData.sceneHandler === 1)
    {
		if (data) {
			if (gameData.start) {
				sphere.position.set(data.x, data.y, 0);
				scene.add(sphere);
			} else {
                console.log("SPHERE 40 SET");
				sphere.position.set(data.x, data.y, 40);
			}
		}

		scene.add(light2);
		scene.add(light1);
		scene.add(light3);

		scene.add(line);
		scene.add(cylinderRight);
		scene.add(cylinderLeft);
		scene.add(sphere);
		scene.add(plane);
	}

    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    composer.render();
}

animate();

