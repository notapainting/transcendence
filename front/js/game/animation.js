import * as THREE from 'three';
import * as load from './loader.js';
import * as game from './game.js';
import * as utils from './utils.js';
import { composer } from './game.js';
import { customData } from './custom.js';
import { gameData } from './game.js';
import { loadData } from './loader.js';

let acceleration = 9.8;
let bounce_distance = 40;
let time_step = 0.06;
let time_counter = Math.sqrt(bounce_distance * 2 / acceleration);
let initial_speed = acceleration * time_counter;
let bounce_height_factor = 1;

export const animationData = {
	ballFall: false,
	intro: 0
  };

export async function animate() {
    requestAnimationFrame(animate);

	// models animation
    if (gameData.sceneHandler == 1)
    {
        if (loadData.mixerBonus)
            loadData.mixerBonus.update(0.01);
        if (loadData.mixerMalus)
            loadData.mixerMalus.update(0.01); 
    }

	if (gameData.sceneHandler === 1)
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
				randomIndex = Math.floor(Math.random() * customData.colorPalettes.length);
			} while (customData.colorBall === customData.colorPalettes[randomIndex]);
		
			customData.colorBall = customData.colorPalettes[randomIndex];
			gameData.collisionPaddle = false;
		}
	}

    composer.render();
}