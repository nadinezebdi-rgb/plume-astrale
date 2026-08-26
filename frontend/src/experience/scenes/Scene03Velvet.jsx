/**
 * Scene 03 — Velours + lumière du dessus
 * ─────────────────────────────────────────────────────────────
 * Les cartes elles-mêmes sont en HTML/CSS (retournement 3D natif,
 * beaucoup plus stable que de créer 3 <PlaneGeometry> avec textures
 * dynamiques). Cette scène 3D fournit seulement L'AMBIANCE :
 *   • plan horizontal texturé (velours sombre + poussière lumineuse)
 *   • spot light chaud venant du dessus
 *   • quelques particules de poussière qui flottent
 */
import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

const DUST_TEXTURE = (() => {
  if (typeof document === 'undefined') return null;
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  grad.addColorStop(0, 'rgba(255, 236, 196, 1)');
  grad.addColorStop(0.5, 'rgba(216, 183, 106, 0.2)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
})();

export default function Scene03Velvet() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);

  const dustCount = isLowEnd ? 80 : isMobile ? 150 : 300;

  const dustPositions = useMemo(() => {
    const arr = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount; i++) {
      arr[i * 3 + 0] = (Math.random() - 0.5) * 6;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 3;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 4 - 1;
    }
    return arr;
  }, [dustCount]);

  const dustRef = useRef();

  useFrame((state) => {
    if (reducedMotion || !dustRef.current) return;
    const t = state.clock.getElapsedTime();
    dustRef.current.rotation.y = t * 0.02;
    dustRef.current.position.y = Math.sin(t * 0.3) * 0.1;
  });

  return (
    <group>
      {/* Plan velours horizontal (léger reflet vers l'observateur) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.4, 0]}>
        <planeGeometry args={[14, 10, 1, 1]} />
        <meshBasicMaterial
          color="#0A0818"
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Halo lumineux au centre (comme un spot venant du dessus) */}
      <sprite scale={[6, 3.5, 1]} position={[0, 0.2, -0.5]}>
        <spriteMaterial
          map={DUST_TEXTURE}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          color="#D8B76A"
          opacity={0.28}
        />
      </sprite>

      {/* Poussière suspendue dans le rayon */}
      <points ref={dustRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[dustPositions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          map={DUST_TEXTURE}
          size={0.08}
          sizeAttenuation
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.6}
          color="#F4EFE6"
        />
      </points>
    </group>
  );
}
