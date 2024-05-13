import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { scene } from './game.js';

const loader = new GLTFLoader();
export var intro;
export var round1;
export var sky;
export var clouds;
export var mixer;
export var clips;

loader.load('./scene3.glb', function ( gltf ) {

    intro = gltf.scene;

    intro.position.set(0,0,-20);

    intro.scale.set(10, 10, 10); 

    intro.rotation.x += Math.PI / 2;

    scene.add(intro);

	mixer = new THREE.AnimationMixer(intro);
    clips = gltf.animations;
    if (clips && clips.length) {
        clips.forEach(function (clip) {
            mixer.clipAction(clip).play();
        });
    }

	gltf.scene.traverse( function ( child ) {
		if ( child.isMesh ) {
			child.material = new THREE.MeshStandardMaterial({
				color: child.material.color,
				map: child.material.map
			});
		}
	});
	
}, undefined, function ( error ) {
	console.error( error );
} );

// loader.load('./round1/scene.gltf', function ( gltf ) {

//     round1 = gltf.scene;

//     round1.position.set(-600, 0, -200);

//     round1.scale.set(10, 10, 10); 

//     scene.add(round1);

// }, undefined, function ( error ) {
// 	console.error( error );
// } );

// loader.load('./nightSky/scene.glb', function ( gltf ) {

//     sky = gltf.scene;

//     sky.position.set(0, 0, 200);

//     sky.scale.set(25, 25, 25); 

//     scene.add(sky);

// }, undefined, function ( error ) {
// 	console.error( error );
// } );
