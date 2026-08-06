'use client';

import React, { useRef, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, Float, OrbitControls, RoundedBox, Text3D, Center, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

function ProductModel({ image }: { image: string }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const texture = React.useMemo(() => {
    const loader = new THREE.TextureLoader();
    const tex = loader.load(image);
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }, [image]);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.15 + state.clock.elapsedTime * 0.1;
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.08;
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.3}>
      <mesh ref={meshRef} castShadow receiveShadow>
        <cylinderGeometry args={[0.7, 0.7, 2.2, 64]} />
        <meshStandardMaterial
          map={texture}
          roughness={0.2}
          metalness={0.1}
          envMapIntensity={0.8}
        />
      </mesh>
      {/* Lid */}
      <mesh position={[0, 1.15, 0]} castShadow>
        <cylinderGeometry args={[0.72, 0.72, 0.12, 64]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.3} metalness={0.5} />
      </mesh>
    </Float>
  );
}

function GlowRing() {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.z = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[1.3, 0.02, 16, 100]} />
      <meshStandardMaterial
        color="#FFD700"
        emissive="#FFD700"
        emissiveIntensity={2}
        transparent
        opacity={0.6}
      />
    </mesh>
  );
}

function FloatingParticles() {
  const count = 50;
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = React.useMemo(() => new THREE.Object3D(), []);

  const particles = React.useMemo(() =>
    Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 5,
      y: (Math.random() - 0.5) * 5,
      z: (Math.random() - 0.5) * 5,
      scale: Math.random() * 0.03 + 0.01,
      speed: Math.random() * 0.5 + 0.2,
      offset: Math.random() * Math.PI * 2,
    })), []);

  useFrame((state) => {
    if (!meshRef.current) return;
    particles.forEach((p, i) => {
      const t = state.clock.elapsedTime;
      dummy.position.set(
        p.x + Math.sin(t * p.speed + p.offset) * 0.5,
        p.y + Math.cos(t * p.speed * 0.7 + p.offset) * 0.3,
        p.z + Math.sin(t * p.speed * 0.5) * 0.2
      );
      dummy.scale.setScalar(p.scale * (1 + Math.sin(t * 2 + p.offset) * 0.3));
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[1, 8, 8]} />
      <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={1} transparent opacity={0.4} />
    </instancedMesh>
  );
}

function BackgroundSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      (meshRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity =
        0.3 + Math.sin(state.clock.elapsedTime) * 0.2;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -3]} scale={6}>
      <sphereGeometry args={[1, 32, 32]} />
      <MeshDistortMaterial
        color="#0A0A0B"
        emissive="#FFD700"
        emissiveIntensity={0.3}
        roughness={1}
        distort={0.15}
        speed={2}
      />
    </mesh>
  );
}

interface ProductViewer3DProps {
  image: string;
  className?: string;
}

export default function ProductViewer3D({ image, className = '' }: ProductViewer3DProps) {
  return (
    <div className={`relative ${className}`}>
      <Canvas
        camera={{ position: [0, 1, 4], fov: 40 }}
        shadows
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <Suspense fallback={null}>
          {/* Lighting */}
          <ambientLight intensity={0.4} />
          <directionalLight position={[5, 5, 5]} intensity={1.5} castShadow />
          <directionalLight position={[-3, 3, -3]} intensity={0.5} color="#FFD700" />
          <pointLight position={[0, -2, 2]} intensity={0.8} color="#FFD700" />

          {/* Product */}
          <ProductModel image={image} />

          {/* Effects */}
          <GlowRing />
          <FloatingParticles />
          <BackgroundSphere />

          {/* Environment */}
          <Environment preset="night" />

          {/* Controls */}
          <OrbitControls
            enableZoom={false}
            enablePan={false}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI / 1.8}
            autoRotate
            autoRotateSpeed={0.5}
          />
        </Suspense>
      </Canvas>

      {/* Overlay gradient */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-pure-black/60 via-transparent to-transparent" />
    </div>
  );
}
