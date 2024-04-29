import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { scene } from './game.js';

const loader = new GLTFLoader();
export var tree;
export var round1;
export var sky;
export var mixer;
export var clips;

loader.load('./tree/scene.gltf', function ( gltf ) {

    tree = gltf.scene;

    tree.position.set(0, 0, 0);

    tree.scale.set(1, 1, 1); 

    tree.rotation.y = Math.PI / 2; 

    scene.add(tree);

	mixer = new THREE.AnimationMixer(tree);
    clips = gltf.animations;
    if (clips && clips.length) {
        clips.forEach(function (clip) {
            mixer.clipAction(clip).play();
        });
    }
}, undefined, function ( error ) {
	console.error( error );
} );

loader.load('./round1/scene.gltf', function ( gltf ) {

    round1 = gltf.scene;

    round1.position.set(-600, 0, -200);

    round1.scale.set(10, 10, 10); 

    scene.add(round1);

}, undefined, function ( error ) {
	console.error( error );
} );

loader.load('./background/scene.gltf', function ( gltf ) {

    sky = gltf.scene;

    sky.position.set(0, 0, 0);

    sky.scale.set(150, 150, 150); 

    scene.add(sky);

}, undefined, function ( error ) {
	console.error( error );
} );

loader.load('./clouds/scene.gltf', function ( gltf ) {

    sky = gltf.scene;

    sky.position.set(0, -100, 0);

    sky.scale.set(20, 20, 20); 

    scene.add(sky);

}, undefined, function ( error ) {
	console.error( error );
} );