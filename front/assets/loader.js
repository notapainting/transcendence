import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { scene } from './game.js';

const loader = new GLTFLoader();
export var intro;
export var bonus;
export var malus;
export var boost;
export var mixer;
export var clips;
export var clipsBonus;
export var clipsMalus;
export var clipsBoost;

export const loadData = {
	mixerBonus: null,
	mixerMalus: null,
	mixerBoost: null
  };

loader.load('./models/scene.glb', function ( gltf ) {

    intro = gltf.scene;

    intro.position.set(0,0,-20);

    intro.scale.set(10, 10, 10); 

    intro.rotation.x += Math.PI / 2;

    // scene.add(intro);

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


loader.load('./models/effectBonus.glb', function ( gltf ) {

    bonus = gltf.scene;

    bonus.position.set(10,10,0);

    bonus.scale.set(2, 2, 2); 

    bonus.rotation.x += Math.PI / 2;

    // scene.add(bonus);

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

    // scene.add(malus);

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

loader.load('./models/boost.glb', function ( gltf ) {

    boost = gltf.scene;

    boost.position.set(10,10,0);

    boost.scale.set(7, 7, 7); 

    // boost.rotation.x += Math.PI / 2;

    // scene.add(boost);

	loadData.mixerBoost = new THREE.AnimationMixer(boost);
    clipsBoost = gltf.animations;
    if (clipsBoost && clipsBoost.length) {
        clipsBoost.forEach(function (clip) {
            loadData.mixerBoost.clipAction(clip).play();
        });
    }
}, undefined, function ( error ) {
	console.error( error );
} );