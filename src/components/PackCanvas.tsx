'use client';

import React, { useRef, Suspense, useState, useCallback, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import {
  Environment,
  OrbitControls,
  ContactShadows,
  MeshReflectorMaterial,
  Ring,
  Float,
} from '@react-three/drei';
import * as THREE from 'three';

/* ─────────────────────────────────────────────
   LABEL TEXTURES — generated via canvas
   ───────────────────────────────────────────── */

function createLabelTexture(flavour: string): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 2048;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d')!;

  // Background gradient based on flavour
  const gradients: Record<string, [string, string, string]> = {
    Orange: ['#FF8C00', '#FF6B00', '#E85D00'],
    'Fruit Punch': ['#FF1744', '#D50000', '#B71C1C'],
    'Rocket Lollipop': ['#7C4DFF', '#651FFF', '#6200EA'],
  };
  const colors = gradients[flavour] || gradients['Orange'];

  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
  grad.addColorStop(0, colors[0]);
  grad.addColorStop(0.5, colors[1]);
  grad.addColorStop(1, colors[2]);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Diagonal stripe accent
  ctx.save();
  ctx.globalAlpha = 0.15;
  ctx.fillStyle = '#000';
  for (let i = -canvas.height; i < canvas.width + canvas.height; i += 80) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i + 40, 0);
    ctx.lineTo(i + 40 - canvas.height, canvas.height);
    ctx.lineTo(i - canvas.height, canvas.height);
    ctx.fill();
  }
  ctx.restore();

  // Top black band
  ctx.fillStyle = '#0A0A0B';
  ctx.fillRect(0, 0, canvas.width, 180);

  // Brand name
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 72px Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('PURE', canvas.width / 2, 80);

  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 48px Arial, sans-serif';
  ctx.fillText('HEALTH SUPPS', canvas.width / 2, 140);

  // Product name
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 120px Arial, sans-serif';
  ctx.fillText('PRIME X', canvas.width / 2, 380);

  // Flavour
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 64px Arial, sans-serif';
  ctx.fillText(flavour.toUpperCase(), canvas.width / 2, 470);

  // Subtitle
  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  ctx.font = '36px Arial, sans-serif';
  ctx.fillText('PRE-WORKOUT FORMULA', canvas.width / 2, 530);

  // Bottom black band
  ctx.fillStyle = '#0A0A0B';
  ctx.fillRect(0, canvas.height - 200, canvas.width, 200);

  // Stats in bottom band
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 44px Arial, sans-serif';
  ctx.fillText('75 SERVINGS  •  280g  •  FSSAI CERTIFIED', canvas.width / 2, canvas.height - 100);

  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '28px Arial, sans-serif';
  ctx.fillText('Beta-Alanine  •  Arginine HCL  •  L-Citrulline  •  Caffeine', canvas.width / 2, canvas.height - 50);

  // Gold accent lines
  ctx.strokeStyle = '#FFD700';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(0, 185);
  ctx.lineTo(canvas.width, 185);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(0, canvas.height - 200);
  ctx.lineTo(canvas.width, canvas.height - 200);
  ctx.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.needsUpdate = true;
  return texture;
}

/* ─────────────────────────────────────────────
   3D JAR MODEL
   ───────────────────────────────────────────── */

function JarModel({ flavour }: { flavour: string }) {
  const groupRef = useRef<THREE.Group>(null);
  const labelTexture = React.useMemo(() => createLabelTexture(flavour), [flavour]);

  // Jar body — clear plastic with label
  const bodyMaterial = React.useMemo(() => {
    const mat = new THREE.MeshPhysicalMaterial({
      color: '#ffffff',
      transparent: true,
      opacity: 0.15,
      roughness: 0.05,
      metalness: 0,
      transmission: 0.6,
      thickness: 0.5,
      clearcoat: 1,
      clearcoatRoughness: 0.05,
      ior: 1.5,
    });
    return mat;
  }, []);

  // Label material
  const labelMaterial = React.useMemo(() => {
    return new THREE.MeshStandardMaterial({
      map: labelTexture,
      roughness: 0.3,
      metalness: 0.1,
      side: THREE.FrontSide,
    });
  }, [labelTexture]);

  // Lid material — matte black
  const lidMaterial = React.useMemo(() => {
    return new THREE.MeshPhysicalMaterial({
      color: '#1a1a1a',
      roughness: 0.4,
      metalness: 0.3,
      clearcoat: 0.5,
    });
  }, []);

  // Rim material — gold
  const rimMaterial = React.useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: '#FFD700',
      roughness: 0.2,
      metalness: 0.8,
      emissive: '#FFD700',
      emissiveIntensity: 0.1,
    });
  }, []);

  return (
    <group ref={groupRef}>
      {/* Jar body — transparent outer */}
      <mesh castShadow position={[0, 0, 0]}>
        <cylinderGeometry args={[1.05, 1.05, 2.8, 64, 1, true]} />
        <primitive object={bodyMaterial} attach="material" />
      </mesh>

      {/* Label — wraps around the jar */}
      <mesh castShadow position={[0, 0, 0]}>
        <cylinderGeometry args={[1.06, 1.06, 1.8, 64, 1, true]} />
        <primitive object={labelMaterial} attach="material" />
      </mesh>

      {/* Bottom cap */}
      <mesh castShadow position={[0, -1.4, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[1.05, 64]} />
        <meshStandardMaterial color="#f0f0f0" roughness={0.3} metalness={0.1} />
      </mesh>

      {/* Lid */}
      <mesh castShadow position={[0, 1.5, 0]}>
        <cylinderGeometry args={[1.08, 1.08, 0.25, 64]} />
        <primitive object={lidMaterial} attach="material" />
      </mesh>

      {/* Lid top indentation */}
      <mesh position={[0, 1.63, 0]}>
        <cylinderGeometry args={[0.9, 0.9, 0.02, 64]} />
        <meshStandardMaterial color="#111" roughness={0.5} metalness={0.2} />
      </mesh>

      {/* Gold rim — top */}
      <mesh position={[0, 1.35, 0]}>
        <torusGeometry args={[1.08, 0.015, 16, 64]} />
        <primitive object={rimMaterial} attach="material" />
      </mesh>

      {/* Gold rim — bottom of label */}
      <mesh position={[0, -0.9, 0]}>
        <torusGeometry args={[1.06, 0.01, 16, 64]} />
        <primitive object={rimMaterial} attach="material" />
      </mesh>
    </group>
  );
}

/* ─────────────────────────────────────────────
   HDR STUDIO ENVIRONMENT
   ───────────────────────────────────────────── */

function HDRStudio({ preset }: { preset: 'studio' | 'dramatic' | 'soft' | 'neon' }) {
  const lights = {
    studio: { ambient: 0.4, key: 1.8, fill: 0.6, rim: 1.2, keyColor: '#ffffff', fillColor: '#E8E8FF', rimColor: '#FFD700' },
    dramatic: { ambient: 0.15, key: 2.5, fill: 0.3, rim: 2.0, keyColor: '#FFD700', fillColor: '#1a0a00', rimColor: '#FF6B00' },
    soft: { ambient: 0.6, key: 1.2, fill: 0.8, rim: 0.6, keyColor: '#FFF5E6', fillColor: '#E6F0FF', rimColor: '#FFFFFF' },
    neon: { ambient: 0.2, key: 1.5, fill: 0.5, rim: 1.8, keyColor: '#FF00FF', fillColor: '#00FFFF', rimColor: '#FFD700' },
  };
  const l = lights[preset];

  return (
    <>
      <ambientLight intensity={l.ambient} />
      {/* Key light — main light */}
      <directionalLight
        position={[5, 8, 5]}
        intensity={l.key}
        color={l.keyColor}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      {/* Fill light — softer, opposite side */}
      <directionalLight position={[-4, 4, -2]} intensity={l.fill} color={l.fillColor} />
      {/* Rim light — back edge highlight */}
      <pointLight position={[0, 3, -5]} intensity={l.rim} color={l.rimColor} distance={15} />
      {/* Bottom bounce */}
      <pointLight position={[0, -3, 2]} intensity={0.4} color="#FFD700" distance={10} />
      {/* Environment map for reflections */}
      <Environment preset={preset === 'dramatic' ? 'night' : preset === 'neon' ? 'night' : 'studio'} />
    </>
  );
}

/* ─────────────────────────────────────────────
   GROUND / STAGE
   ───────────────────────────────────────────── */

function StudioGround() {
  return (
    <>
      {/* Reflective floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.5, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <MeshReflectorMaterial
          mirror={0}
          blur={[300, 100]}
          resolution={1024}
          mixBlur={1}
          mixStrength={40}
          roughness={1}
          depthScale={1.2}
          minDepthThreshold={0.4}
          maxDepthThreshold={1.4}
          color="#050505"
          metalness={0.5}
        />
      </mesh>
      {/* Contact shadow */}
      <ContactShadows
        position={[0, -1.49, 0]}
        opacity={0.5}
        scale={10}
        blur={2}
        far={4}
      />
    </>
  );
}

/* ─────────────────────────────────────────────
   CAMERA CONTROLLER — snaps to preset angles
   ───────────────────────────────────────────── */

interface CameraPreset {
  name: string;
  position: [number, number, number];
  target: [number, number, number];
  format: 'website' | 'instagram' | 'all';
}

export const CAMERA_PRESETS: CameraPreset[] = [
  // Website presets
  { name: 'Hero Front', position: [0, 0.5, 5], target: [0, 0, 0], format: 'website' },
  { name: 'Hero 3/4 Left', position: [-3, 0.8, 3.5], target: [0, 0, 0], format: 'website' },
  { name: 'Hero 3/4 Right', position: [3, 0.8, 3.5], target: [0, 0, 0], format: 'website' },
  { name: 'Side Profile', position: [5, 0, 0], target: [0, 0, 0], format: 'website' },
  { name: 'Top Down', position: [0, 6, 0.5], target: [0, 0, 0], format: 'website' },
  { name: 'Low Angle', position: [2, -1, 4], target: [0, 0.5, 0], format: 'website' },
  { name: 'Close Up', position: [1.5, 0.3, 2.5], target: [0, 0, 0], format: 'website' },
  { name: 'Detail Label', position: [2, 0, 1.5], target: [0, -0.2, 0], format: 'website' },
  { name: 'Wide Shot', position: [0, 1, 8], target: [0, 0, 0], format: 'website' },
  { name: 'Dutch Angle', position: [3, 2, 3], target: [0, 0, 0], format: 'website' },
  // Instagram presets (tighter, more dramatic)
  { name: 'IG Square Hero', position: [0, 0.3, 4.5], target: [0, 0, 0], format: 'instagram' },
  { name: 'IG Dramatic Low', position: [1.5, -0.5, 3], target: [0, 0.5, 0], format: 'instagram' },
  { name: 'IG Overhead', position: [0, 5, 1], target: [0, 0, 0], format: 'instagram' },
  { name: 'IG Side Hero', position: [4, 0.3, 2], target: [0, 0, 0], format: 'instagram' },
  { name: 'IG Close Detail', position: [1.2, 0.1, 2], target: [0, -0.1, 0], format: 'instagram' },
  { name: 'IG Moody 3/4', position: [-2.5, 0.5, 3], target: [0, 0, 0], format: 'instagram' },
  // Reels / Story (vertical)
  { name: 'Reels Hero', position: [0, 0.5, 4], target: [0, 0, 0], format: 'instagram' },
  { name: 'Reels Dramatic', position: [2, -0.8, 2.5], target: [0, 0.8, 0], format: 'instagram' },
];

function CameraController({ preset }: { preset: CameraPreset | null }) {
  const { camera } = useThree();
  const targetPos = useRef(new THREE.Vector3(...(preset?.position || [0, 0.5, 5])));
  const targetLookAt = useRef(new THREE.Vector3(...(preset?.target || [0, 0, 0])));

  useEffect(() => {
    if (preset) {
      targetPos.current.set(...preset.position);
      targetLookAt.current.set(...preset.target);
    }
  }, [preset]);

  useFrame(() => {
    camera.position.lerp(targetPos.current, 0.05);
    const lookAt = new THREE.Vector3();
    lookAt.copy(camera.position).add(
      targetLookAt.current.clone().sub(camera.position).normalize().multiplyScalar(10)
    );
    camera.lookAt(targetLookAt.current);
  });

  return null;
}

/* ─────────────────────────────────────────────
   MAIN SCENE
   ───────────────────────────────────────────── */

interface PackSceneProps {
  flavour: string;
  lightPreset: 'studio' | 'dramatic' | 'soft' | 'neon';
  cameraPreset: CameraPreset | null;
  autoRotate: boolean;
}

function PackScene({ flavour, lightPreset, cameraPreset, autoRotate }: PackSceneProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current && autoRotate && !cameraPreset) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
    }
  });

  return (
    <>
      <HDRStudio preset={lightPreset} />
      <CameraController preset={cameraPreset} />

      <group ref={groupRef}>
        <Float speed={1.2} rotationIntensity={0.05} floatIntensity={0.15}>
          <JarModel flavour={flavour} />
        </Float>
      </group>

      <StudioGround />
    </>
  );
}

/* ─────────────────────────────────────────────
   EXPORTED CANVAS WRAPPER
   ───────────────────────────────────────────── */

interface PackCanvasProps {
  flavour: string;
  lightPreset: 'studio' | 'dramatic' | 'soft' | 'neon';
  cameraPreset: CameraPreset | null;
  autoRotate: boolean;
  className?: string;
}

export default React.forwardRef<HTMLCanvasElement, PackCanvasProps>(function PackCanvas({
  flavour,
  lightPreset,
  cameraPreset,
  autoRotate,
  className = '',
}: PackCanvasProps, ref) {
  return (
    <div className={`relative ${className}`}>
      <Canvas
        ref={ref}
        camera={{ position: [0, 0.5, 5], fov: 35 }}
        shadows
        gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
        dpr={[1, 2]}
        style={{ background: '#0A0A0B' }}
      >
        <Suspense fallback={null}>
          <PackScene
            flavour={flavour}
            lightPreset={lightPreset}
            cameraPreset={cameraPreset}
            autoRotate={autoRotate}
          />
        </Suspense>
      </Canvas>
    </div>
  );
});
