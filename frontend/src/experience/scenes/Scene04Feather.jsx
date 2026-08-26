/**
 * Scene 04 — Apparition de la plume
 * ─────────────────────────────────────────────────────────────
 * Le MOMENT WOW.
 *
 * • ~600 particules démarrent en positions aléatoires (dispersion).
 * • Elles convergent PROGRESSIVEMENT vers un ensemble de positions
 *   cibles qui dessinent une plume calligraphique.
 * • Une fois la formation atteinte, elles respirent doucement.
 *
 * La formation est pilotée par `globalProgress` (0..1 sur les 4 scènes).
 * L'interpolation démarre à progress=0.75 (début scène 4) et se termine
 * à progress=0.95 (avant les derniers 5% qui laissent la plume respirer).
 */
import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

const FEATHER_TEXTURE = (() => {
  if (typeof document === 'undefined') return null;
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  grad.addColorStop(0, 'rgba(255, 246, 220, 1)');
  grad.addColorStop(0.4, 'rgba(216, 183, 106, 0.35)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
})();

/**
 * Génère les positions cibles qui dessinent une plume calligraphique.
 * On sample :
 *   • le rachis (colonne centrale, courbe légère)
 *   • les barbes de gauche et de droite (perpendiculaires au rachis,
 *     de plus en plus longues vers le milieu, plus courtes aux extrémités)
 *   • quelques particules près du calamus (pointe basse) pour l'ancre visuelle
 */
function generateFeatherTargets(count) {
  const targets = new Float32Array(count * 3);
  const barbCount = Math.floor(count * 0.85);
  const rachisCount = count - barbCount;

  // Rachis vertical courbé (~une belle S doux)
  for (let i = 0; i < rachisCount; i++) {
    const t = i / (rachisCount - 1); // 0..1
    const y = (t - 0.5) * 4;         // -2..+2
    const x = Math.sin(t * Math.PI * 0.5) * 0.15; // légère courbure
    const z = 0;
    targets[i * 3 + 0] = x;
    targets[i * 3 + 1] = y;
    targets[i * 3 + 2] = z;
  }

  // Barbes : pour chaque particule barbe, tirer aléatoirement une position le long
  // du rachis (t=0..1) puis un offset perpendiculaire dont l'amplitude dépend de t.
  for (let i = 0; i < barbCount; i++) {
    const t = Math.random();
    const y = (t - 0.5) * 4;
    const rachisX = Math.sin(t * Math.PI * 0.5) * 0.15;

    // Enveloppe de la plume : plus large au milieu, effilée en haut et bas
    // Utilise sinus modulé : envelope(t) = sin(π*t)^1.2
    const envelope = Math.pow(Math.sin(Math.PI * t), 1.2);
    // Amplitude max de la barbe (côté gauche/droit)
    const side = Math.random() < 0.5 ? -1 : 1;
    const barbLen = (0.15 + Math.random() * 0.85) * envelope * 1.4;
    // Angle de la barbe (légèrement incliné vers le bas — plus élégant)
    const angle = -0.25;
    const bx = rachisX + side * barbLen * Math.cos(angle);
    const by = y + barbLen * Math.sin(angle) * side * 0.3;
    const bz = (Math.random() - 0.5) * 0.15;

    // Placement dans le buffer (après le rachis)
    const idx = rachisCount + i;
    targets[idx * 3 + 0] = bx;
    targets[idx * 3 + 1] = by;
    targets[idx * 3 + 2] = bz;
  }

  return targets;
}

export default function Scene04Feather() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);
  const globalProgress = useExperienceStore((s) => s.globalProgress);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);

  const count = isLowEnd ? 160 : isMobile ? 320 : 600;

  const { startPositions, targetPositions, offsets, currentPositions } = useMemo(() => {
    const startPositions = new Float32Array(count * 3);
    const targetPositions = generateFeatherTargets(count);
    const offsets = new Float32Array(count); // pour animation respiration
    const currentPositions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      // Positions de départ : dispersées dans une sphère
      const r = 3 + Math.random() * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      startPositions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      startPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      startPositions[i * 3 + 2] = r * Math.cos(phi) - 2;
      // Copie initiale
      currentPositions[i * 3 + 0] = startPositions[i * 3 + 0];
      currentPositions[i * 3 + 1] = startPositions[i * 3 + 1];
      currentPositions[i * 3 + 2] = startPositions[i * 3 + 2];
      offsets[i] = Math.random() * Math.PI * 2;
    }
    return { startPositions, targetPositions, offsets, currentPositions };
  }, [count]);

  const pointsRef = useRef();
  const geoRef = useRef();

  useFrame((state) => {
    if (!geoRef.current) return;
    const t = state.clock.getElapsedTime();

    // Progress de convergence : monte de 0 à 1 entre globalProgress 0.75 et 0.95
    const convergence = THREE.MathUtils.clamp(
      (globalProgress - 0.75) / 0.20,
      0,
      1
    );
    // Ease out cubic pour un mouvement plus doux à la fin
    const eased = 1 - Math.pow(1 - convergence, 3);

    const posAttr = geoRef.current.attributes.position;
    for (let i = 0; i < count; i++) {
      const sx = startPositions[i * 3 + 0];
      const sy = startPositions[i * 3 + 1];
      const sz = startPositions[i * 3 + 2];
      const tx = targetPositions[i * 3 + 0];
      const ty = targetPositions[i * 3 + 1];
      const tz = targetPositions[i * 3 + 2];

      // Interpolation start → target
      let x = sx + (tx - sx) * eased;
      let y = sy + (ty - sy) * eased;
      let z = sz + (tz - sz) * eased;

      // Respiration une fois formée
      if (!reducedMotion && eased > 0.9) {
        const breath = Math.sin(t * 0.7 + offsets[i]) * 0.02;
        x += breath;
        y += breath * 0.5;
      }

      posAttr.array[i * 3 + 0] = x;
      posAttr.array[i * 3 + 1] = y;
      posAttr.array[i * 3 + 2] = z;
    }
    posAttr.needsUpdate = true;

    // Rotation douce de la plume complète une fois formée
    if (pointsRef.current && eased > 0.85) {
      const rotAmount = (eased - 0.85) / 0.15;
      pointsRef.current.rotation.z = Math.sin(t * 0.3) * 0.06 * rotAmount;
    }
  });

  return (
    <points ref={pointsRef} position={[0, 0, 0]}>
      <bufferGeometry ref={geoRef}>
        <bufferAttribute
          attach="attributes-position"
          args={[currentPositions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        map={FEATHER_TEXTURE}
        size={0.12}
        sizeAttenuation
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        opacity={0.95}
        color="#F4EFE6"
      />
    </points>
  );
}
