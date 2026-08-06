'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';

interface TubViewerProps {
  labelImage: string;
  width?: number;
  height?: number;
  autoRotate?: boolean;
  className?: string;
}

export default function TubViewer({
  labelImage,
  width = 500,
  height = 500,
  autoRotate = true,
  className = '',
}: TubViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const tubRef = useRef<THREE.Mesh | null>(null);
  const frameRef = useRef<number>(0);
  const isDragging = useRef(false);
  const previousMouse = useRef({ x: 0, y: 0 });
  const rotationVelocity = useRef({ x: 0, y: 0 });
  const targetRotation = useRef({ x: 0, y: 0 });

  const createLabelTexture = useCallback((image: HTMLImageElement) => {
    const canvas = document.createElement('canvas');
    const imgW = image.width;
    const imgH = image.height;
    const labelTop = Math.floor(imgH * 0.12);
    const labelBottom = Math.floor(imgH * 0.78);
    const labelHeight = labelBottom - labelTop;
    canvas.width = imgW;
    canvas.height = labelHeight;
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(image, 0, labelTop, imgW, labelHeight, 0, 0, imgW, labelHeight);
    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;
    texture.repeat.set(1, 1);
    return texture;
  }, []);

  const createTubGeometry = useCallback(() => {
    const radius = 1;
    const height = 1.6;
    const radialSegments = 64;
    const heightSegments = 1;
    const openEnded = false;

    const geometry = new THREE.CylinderGeometry(
      radius, radius, height, radialSegments, heightSegments, openEnded
    );

    return geometry;
  }, []);

  const createLidGeometry = useCallback(() => {
    const geometry = new THREE.CylinderGeometry(1.04, 1.04, 0.18, 64);
    return geometry;
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 100);
    camera.position.set(0, 0.5, 5);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
    mainLight.position.set(3, 4, 5);
    scene.add(mainLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
    fillLight.position.set(-3, 2, -3);
    scene.add(fillLight);

    const rimLight = new THREE.PointLight(0xFFD100, 0.6, 10);
    rimLight.position.set(0, 3, -3);
    scene.add(rimLight);

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = labelImage;
    img.onload = () => {
      const labelTexture = createLabelTexture(img);

      const tubGroup = new THREE.Group();

      const tubGeometry = createTubGeometry();
      const tubMaterial = new THREE.MeshStandardMaterial({
        map: labelTexture,
        roughness: 0.3,
        metalness: 0.1,
      });
      const tub = new THREE.Mesh(tubGeometry, tubMaterial);
      tubGroup.add(tub);
      tubRef.current = tub;

      const lidGeometry = createLidGeometry();
      const lidMaterial = new THREE.MeshStandardMaterial({
        color: 0xf5f5f5,
        roughness: 0.4,
        metalness: 0.05,
      });
      const lid = new THREE.Mesh(lidGeometry, lidMaterial);
      lid.position.y = 0.88;
      tubGroup.add(lid);

      const rimGeometry = new THREE.TorusGeometry(1.04, 0.025, 16, 64);
      const rimMaterial = new THREE.MeshStandardMaterial({
        color: 0xf5f5f5,
        roughness: 0.3,
        metalness: 0.1,
      });
      const rim = new THREE.Mesh(rimGeometry, rimMaterial);
      rim.rotation.x = Math.PI / 2;
      rim.position.y = 0.78;
      tubGroup.add(rim);

      scene.add(tubGroup);

      const animate = () => {
        frameRef.current = requestAnimationFrame(animate);

        if (!isDragging.current && autoRotate) {
          tubGroup.rotation.y += 0.005;
        }

        if (isDragging.current) {
          tubGroup.rotation.y += rotationVelocity.current.x;
          tubGroup.rotation.x += rotationVelocity.current.y;
          tubGroup.rotation.x = Math.max(-0.3, Math.min(0.3, tubGroup.rotation.x));
          rotationVelocity.current.x *= 0.95;
          rotationVelocity.current.y *= 0.95;
        }

        renderer.render(scene, camera);
      };
      animate();
    };

    return () => {
      cancelAnimationFrame(frameRef.current);
      renderer.dispose();
      if (containerRef.current && renderer.domElement.parentNode === containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, [labelImage, width, height, autoRotate, createLabelTexture, createTubGeometry, createLidGeometry]);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    isDragging.current = true;
    previousMouse.current = { x: e.clientX, y: e.clientY };
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  }, []);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging.current) return;
    const deltaX = e.clientX - previousMouse.current.x;
    const deltaY = e.clientY - previousMouse.current.y;
    rotationVelocity.current = {
      x: deltaX * 0.008,
      y: deltaY * 0.004,
    };
    previousMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const handlePointerUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  return (
    <div
      ref={containerRef}
      className={className}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
      style={{
        width,
        height,
        cursor: 'grab',
        touchAction: 'none',
      }}
    />
  );
}
