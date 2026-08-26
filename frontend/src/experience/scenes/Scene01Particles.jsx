/**
 * Scene 01 — Entrée dans l'univers
 * ─────────────────────────────────────────────────────────────
 * • ~1200 particules profondes (300 sur mobile / low-end)
 * • 1 étoile centrale émissive (sprite additif)
 * • Léger drift des particules avec le temps
 * Volontairement contemplatif — l'utilisateur doit *sentir* la profondeur
 * avant même que le premier mot n'apparaisse.
 */
import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

const STAR_TEXTURE = (() => {
  // Texture de particule générée en canvas — halo gaussien doux
  if (typeof document === 'undefined') return null;
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  grad.addColorStop(0, 'rgba(255, 246, 220, 1)');
  grad.addColorStop(0.25, 'rgba(216, 183, 106, 0.6)');
  grad.addColorStop(0.55, 'rgba(118, 87, 200, 0.15)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
})();

export default function Scene01Particles() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);

  const count = isLowEnd ? 90 : isMobile ? 180 : 380;

  // Génération procédurale des positions (une fois)
  const { positions, sizes, phases } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    const phases = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      // shell sphérique de rayon variable pour créer une vraie profondeur
      const r = 3 + Math.random() * 22;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.8; // aplati
      positions[i * 3 + 2] = r * Math.cos(phi);
      // Sizes distribution — quelques grosses (proches), beaucoup de petites
      sizes[i] = Math.pow(Math.random(), 3) * 0.6 + 0.05;
      phases[i] = Math.random() * Math.PI * 2;
    }
    return { positions, sizes, phases };
  }, [count]);

  const pointsRef = useRef();
  const centerRef = useRef();

  useFrame((state) => {
    if (reducedMotion) return;
    const t = state.clock.getElapsedTime();
    if (pointsRef.current) {
      pointsRef.current.rotation.y = t * 0.008;
      pointsRef.current.rotation.x = Math.sin(t * 0.03) * 0.05;
    }
    if (centerRef.current) {
      // L'étoile centrale "respire" doucement
      const s = 1 + Math.sin(t * 0.6) * 0.06;
      centerRef.current.scale.setScalar(s);
    }
  });

  return (
    <group>
      {/* Étoile centrale */}
      <sprite ref={centerRef} scale={[1.4, 1.4, 1]}>
        <spriteMaterial
          map={STAR_TEXTURE}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.85}
          color="#F4EFE6"
        />
      </sprite>

      {/* Champ de particules profondes */}
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
          <bufferAttribute attach="attributes-size" args={[sizes, 1]} />
          <bufferAttribute attach="attributes-phase" args={[phases, 1]} />
        </bufferGeometry>
        <pointsMaterial
          map={STAR_TEXTURE}
          size={0.28}
          sizeAttenuation
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.9}
          color="#F4EFE6"
        />
      </points>
    </group>
  );
}
