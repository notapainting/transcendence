import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { scene } from './game.js';

const loader = new GLTFLoader();
export var intro;
export var effect;
export var mixer;
export var mixer2;
export var clips;
export var clips2;

export const loadData = {
	mixer2: null
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


loader.load('./models/effect.glb', function ( gltf ) {

    effect = gltf.scene;

    effect.position.set(10,10,0);

    effect.scale.set(2, 2, 2); 

    effect.rotation.x += Math.PI / 2;

    // scene.add(effect);

	loadData.mixer2 = new THREE.AnimationMixer(effect);
    clips2 = gltf.animations;
    if (clips2 && clips2.length) {
        clips2.forEach(function (clip) {
            loadData.mixer2.clipAction(clip).play();
        });
    }
	
}, undefined, function ( error ) {
	console.error( error );
} );

