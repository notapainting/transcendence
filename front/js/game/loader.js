import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { scene } from './game.js';

const loader = new GLTFLoader();
export var intro;
export var bonus;
export var malus;
export var clipsBonus;
export var clipsMalus;

export const loadData = {
	mixerBonus: null,
	mixerMalus: null
  };

loader.load('./models/scene.glb', function ( gltf ) {

    intro = gltf.scene;

    intro.position.set(0,0,-20);
    intro.scale.set(10, 10, 10); 
    intro.rotation.x += Math.PI / 2;

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


loader.load('./models/effectBonus.glb', function ( gltf ) {

    bonus = gltf.scene;

    bonus.position.set(10,10,0);
    bonus.scale.set(2, 2, 2); 
    bonus.rotation.x += Math.PI / 2;

	loadData.mixerBonus = new THREE.AnimationMixer(bonus);
    clipsBonus = gltf.animations;
    if (clipsBonus && clipsBonus.length) {
        clipsBonus.forEach(function (clip) {
            loadData.mixerBonus.clipAction(clip).play();
        });
    }
}, undefined, function ( error ) {
	console.error( error );
} );

loader.load('./models/effectMalus.glb', function ( gltf ) {

    malus = gltf.scene;

    malus.position.set(10,10,0);
    malus.scale.set(2, 2, 2); 
    malus.rotation.x += Math.PI / 2;

	loadData.mixerMalus = new THREE.AnimationMixer(malus);
    clipsMalus = gltf.animations;
    if (clipsMalus && clipsMalus.length) {
        clipsMalus.forEach(function (clip) {
            loadData.mixerMalus.clipAction(clip).play();
        });
    }
}, undefined, function ( error ) {
	console.error( error );
} );
