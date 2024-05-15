import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';
import { scene } from "./game.js";
import { animationData } from './animation.js';
import * as anim from './animation.js';
import { camera } from './game.js';
import * as game from './game.js';

export var colorTransitionTime = 3000;
export var colorStartTime = Date.now();

export function interpolateColor(color) {
    const now = Date.now();
    const elapsedTime = now - colorStartTime;
    const timePerColor = colorTransitionTime / color.length;
    const colorIndexStart = Math.floor(elapsedTime / timePerColor) % color.length;
    const colorIndexEnd = (colorIndexStart + 1) % color.length;
    const ratio = (elapsedTime % timePerColor) / timePerColor;

    const colorStart = new THREE.Color(color[colorIndexStart]);
    const colorEnd = new THREE.Color(color[colorIndexEnd]);

    const interpolatedColor = new THREE.Color().copy(colorStart).lerp(colorEnd, ratio);
    return interpolatedColor.getHex();
}

export function transRot3D(object, initialPos, finalPos, initialAng, finalAng, speed, intro)
{
	var first;
	var second;

	var delta = initialPos.x - finalPos.x;
	first = object.position.x;
	second = finalPos.x
	if (delta === 0){
		first = object.position.y;
		second = finalPos.y
		var delta = initialPos.y - finalPos.y;	
	}
	if (delta === 0){
		first = object.position.z;
		second = finalPos.z
		var delta = initialPos.z - finalPos.z;	
	}

	if (delta < 0)
	{
		if (first < second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
	
			object.rotation.x -= (initialAng.x - finalAng.x) / speed ;
			object.rotation.y -= (initialAng.y - finalAng.y) / speed ;
			object.rotation.z -= (initialAng.z - finalAng.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	} else {
		if (first > second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
	
			object.rotation.x -= (initialAng.x - finalAng.x) / speed ;
			object.rotation.y -= (initialAng.y - finalAng.y) / speed ;
			object.rotation.z -= (initialAng.z - finalAng.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	}
}

export function translationXYZ(object, initialPos, finalPos, speed, intro)
{
	var first;
	var second;

	var delta = initialPos.x - finalPos.x;
	first = object.position.x;
	second = finalPos.x
	if (delta === 0){
		first = object.position.y;
		second = finalPos.y
		var delta = initialPos.y - finalPos.y;	
	}
	if (delta === 0){
		first = object.position.z;
		second = finalPos.z
		var delta = initialPos.z - finalPos.z;	
	}

	if (delta < 0)
	{
		if (first < second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	} else {
		if (first > second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	}
}

export function translationTargetXYZ(object, initialPos, finalPos, speed, intro)
{
	var first;
	var second;

	var delta = initialPos.x - finalPos.x;
	first = object.x;
	second = finalPos.x
	if (delta === 0){
		first = object.y;
		second = finalPos.y
		var delta = initialPos.y - finalPos.y;	
	}
	if (delta === 0){
		first = object.z;
		second = finalPos.z
		var delta = initialPos.z - finalPos.z;	
	}

	if (delta < 0)
	{
		if (first < second)
		{
			object.x -= (initialPos.x - finalPos.x) / speed ;
			object.y -= (initialPos.y - finalPos.y) / speed ;
			object.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	} else {
		if (first > second)
		{
			object.x -= (initialPos.x - finalPos.x) / speed ;
			object.y -= (initialPos.y - finalPos.y) / speed ;
			object.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	}
}

export function translationCameraXYZ(object, lookAt, initialPos, finalPos, speed, intro)
{
	var first;
	var second;

	var delta = initialPos.x - finalPos.x;
	first = object.position.x;
	second = finalPos.x
	if (delta === 0){
		first = object.position.y;
		second = finalPos.y
		var delta = initialPos.y - finalPos.y;	
	}
	if (delta === 0){
		first = object.position.z;
		second = finalPos.z
		var delta = initialPos.z - finalPos.z;	
	}

	if (delta < 0)
	{
		if (first < second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	} else {
		if (first > second)
		{
			object.position.x -= (initialPos.x - finalPos.x) / speed ;
			object.position.y -= (initialPos.y - finalPos.y) / speed ;
			object.position.z -= (initialPos.z - finalPos.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	}

	camera.lookAt(lookAt.x,lookAt.y,lookAt.z);
}

export function rotationXYZ(object, initialRot, finalRot, speed, intro)
{
	var first;
	var second;

	var delta = initialRot.x - finalRot.x;
	first = object.rotation.x;
	second = finalRot.x
	if (delta === 0){
		first = object.rotation.y;
		second = finalRot.y
		var delta = initialRot.y - finalRot.y;	
	}
	if (delta === 0){
		first = object.rotation.z;
		second = finalRot.z
		var delta = initialRot.z - finalRot.z;	
	}

	if (delta < 0)
	{
		if (first < second)
		{
			object.rotation.x -= (initialRot.x - finalRot.x) / speed ;
			object.rotation.y -= (initialRot.y - finalRot.y) / speed ;
			object.rotation.z -= (initialRot.z - finalRot.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	} else {
		if (first > second)
		{
			object.rotation.x -= (initialRot.x - finalRot.x) / speed ;
			object.rotation.y -= (initialRot.y - finalRot.y) / speed ;
			object.rotation.z -= (initialRot.z - finalRot.z) / speed ;
		} else {
			animationData.intro = intro;
		}
	}
}

const clock=new THREE.Clock();
var time=0;

export function rotationAroundXYZ(camera, object, camera_offset, camera_speed, intro)
{
	clock.getDelta();
	time = clock.elapsedTime.toFixed(2);
	var target={x:2,y:2,z:2};

	target.x = object.x;
	// target.y=object.y
	// target.y = 2
	target.z = object.z;
	camera.position.x = target.x + camera_offset.x * (Math.sin(time * camera_speed));
	camera.position.z = target.z + camera_offset.z * (Math.cos(time * camera_speed));
	camera.position.y = target.y + camera_offset.y;


	camera.lookAt(target.x, target.y, target.z);
}

export function clearScene() {
    let toRemove = [];
    scene.children.forEach((child) => {
        if (child.type !== 'Points') {
            toRemove.push(child);
        }
    });
    toRemove.forEach((child) => {
        scene.remove(child);
    });
}

export function createParticle(positionX, positionY, particuleSize, distance) {
    var geometry = new THREE.BufferGeometry();
    var vertices = new Float32Array([positionX, positionY, 0]);

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

    var randomColor = anim.colorBall[Math.floor(Math.random() * anim.colorBall.length)];
    var material = new THREE.PointsMaterial({ color: randomColor, size: particuleSize });

    var particle = new THREE.Points(geometry, material);
    scene.add(particle);

    var direction = new THREE.Vector3(
        Math.random() - 0.5,
        Math.random() - 0.5,
        Math.random() - 0.5
    ).normalize();

    var speed = 0.6;
    var update = function () {
        var positionAttribute = particle.geometry.getAttribute('position');
        var currentPosition = new THREE.Vector3().fromBufferAttribute(positionAttribute, 0);
        currentPosition.addScaledVector(direction, speed);
        positionAttribute.setXYZ(0, currentPosition.x, currentPosition.y, currentPosition.z);
        positionAttribute.needsUpdate = true;
        distance -= speed;
        if (distance <= 0) {
            scene.remove(particle);
            cancelAnimationFrame(animationId);
        }
    };

    var animationId = requestAnimationFrame(function animate() {
        update();
        animationId = requestAnimationFrame(animate);
    });
}

export function getRandomPointInRectangle(p1, p2, p3, p4) {
    const r1 = Math.random();
    const r2 = Math.random();

    const points = [p1, p2, p3, p4];
    if (isClockwise(points)) {
        points.reverse();
    }

    const [a, b, c, d] = points;

    const x1 = a.x + r1 * (b.x - a.x);
    const y1 = a.y + r1 * (b.y - a.y);
    const x2 = d.x + r1 * (c.x - d.x);
    const y2 = d.y + r1 * (c.y - d.y);

    const x = x1 + r2 * (x2 - x1);
    const y = y1 + r2 * (y2 - y1);

    return { x, y };
}

export function isClockwise(points) {
    const [p1, p2, p3, p4] = points;
    const sum = (p2.x - p1.x) * (p2.y + p1.y) +
                (p3.x - p2.x) * (p3.y + p2.y) +
                (p4.x - p3.x) * (p4.y + p3.y) +
                (p1.x - p4.x) * (p1.y + p4.y);
    return sum > 0;
}