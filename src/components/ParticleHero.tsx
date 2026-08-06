'use client';

import React, { useRef, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function ParticleCloud() {
  const count = 200;
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = React.useMemo(() => new THREE.Object3D(), []);

  const particles = React.useMemo(() =>
    Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 10,
      y: (Math.random() - 0.5) * 6,
      z: (Math.random() - 0.5) * 8,
      scale: Math.random() * 0.04 + 0.01,
      speed: Math.random() * 0.3 + 0.1,
      offset: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.5,
    })), []);

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;
    particles.forEach((p, i) => {
      dummy.position.set(
        p.x + Math.sin(t * p.speed + p.offset) * 1.5,
        p.y + Math.cos(t * p.speed * 0.7 + p.offset) * 0.8,
        p.z + Math.sin(t * p.speed * 0.3) * 0.5
      );
      dummy.rotation.set(
        t * p.rotSpeed,
        t * p.rotSpeed * 0.7,
        0
      );
      const s = p.scale * (1 + Math.sin(t * 1.5 + p.offset) * 0.4);
      dummy.scale.setScalar(s);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <octahedronGeometry args={[1, 0]} />
      <meshStandardMaterial
        color="#FFD700"
        emissive="#FFD700"
        emissiveIntensity={1.5}
        transparent
        opacity={0.35}
        roughness={0.3}
        metalness={0.8}
      />
    </instancedMesh>
  );
}

function FloatingRings() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = state.clock.elapsedTime * 0.05;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.08;
    }
  });

  return (
    <group ref={groupRef}>
      {[1.5, 2.2, 3].map((radius, i) => (
        <mesh key={i} rotation={[Math.PI / 2 + i * 0.3, i * 0.5, 0]}>
          <torusGeometry args={[radius, 0.008, 16, 100]} />
          <meshStandardMaterial
            color="#FFD700"
            emissive="#FFD700"
            emissiveIntensity={1 + i * 0.3}
            transparent
            opacity={0.15 - i * 0.03}
          />
        </mesh>
      ))}
    </group>
  );
}

function EnergyWave() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 0.8) * 0.3;
      meshRef.current.scale.setScalar(scale);
      (meshRef.current.material as THREE.MeshStandardMaterial).opacity =
        0.05 + Math.sin(state.clock.elapsedTime * 0.8) * 0.03;
    }
  });

  return (
    <mesh ref={meshRef} rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[2, 2.02, 64]} />
      <meshStandardMaterial
        color="#FFD700"
        emissive="#FFD700"
        emissiveIntensity={3}
        transparent
        opacity={0.05}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

interface ParticleHeroProps {
  className?: string;
}

export default function ParticleHero({ className = '' }: ParticleHeroProps) {
  return (
    <div className={`absolute inset-0 ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.3} />
          <pointLight position={[3, 3, 3]} intensity={1} color="#FFD700" />
          <pointLight position={[-3, -2, 2]} intensity={0.5} color="#FFD700" />

          <ParticleCloud />
          <FloatingRings />
          <EnergyWave />
        </Suspense>
      </Canvas>
    </div>
  );
}
