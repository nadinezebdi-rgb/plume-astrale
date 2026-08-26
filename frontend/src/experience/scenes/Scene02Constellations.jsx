/**
 * Scene 02 — Quatre constellations lumineuses
 * ─────────────────────────────────────────────────────────────
 * • 4 sets d'étoiles + lignes fines les reliant
 * • Positionnées autour du centre (NE, NW, SE, SW)
 * • Léger flottement, plus lumineuses quand l'intent lit dans le store
 *
 * Le hover/clic UI est géré au niveau HTML (overlay), pas dans le canvas.
 * Ici on écoute juste `intent` pour illuminer la constellation choisie.
 */
import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

// Coordonnées locales de chaque constellation (5 points chacune, relatives au centre)
const CONSTELLATIONS = {
  relationship:   [[-0.3, 0.4], [0.1, 0.6], [0.4, 0.3], [0.2, -0.1], [-0.1, 0.1]],
  clarity:        [[-0.4, 0.2], [-0.1, 0.5], [0.3, 0.4], [0.5, 0.1], [0.2, -0.2]],
  selfDiscovery:  [[0.0, 0.6], [-0.3, 0.3], [-0.2, -0.1], [0.2, 0.0], [0.4, 0.4]],
  question:       [[-0.3, 0.0], [0.0, 0.3], [0.3, 0.1], [0.5, -0.2], [0.1, -0.3]],
};

// Centres des 4 constellations (autour du centre du monde)
const CENTERS = {
  relationship:  new THREE.Vector3(-2.4,  1.1, -2),
  clarity:       new THREE.Vector3( 2.4,  1.1, -2),
  selfDiscovery: new THREE.Vector3(-2.4, -1.1, -2),
  question:      new THREE.Vector3( 2.4, -1.1, -2),
};

function Constellation({ id, points, center, isActive }) {
  const ref = useRef();
  const lineRef = useRef();

  // Positions absolues (points × scale + center)
  const positions = useMemo(() => {
    const arr = new Float32Array(points.length * 3);
    points.forEach(([x, y], i) => {
      arr[i * 3 + 0] = x * 1.4 + center.x;
      arr[i * 3 + 1] = y * 1.4 + center.y;
      arr[i * 3 + 2] = center.z + (Math.random() - 0.5) * 0.4;
    });
    return arr;
  }, [points, center]);

  const lineIndices = useMemo(() => {
    // Ligne reliant les points dans l'ordre
    const arr = [];
    for (let i = 0; i < points.length - 1; i++) arr.push(i, i + 1);
    return new Uint16Array(arr);
  }, [points.length]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (ref.current) {
      ref.current.material.opacity = isActive ? 1 : 0.72;
      // Léger flottement
      ref.current.position.y = Math.sin(t * 0.4 + center.x) * 0.05;
    }
    if (lineRef.current) {
      lineRef.current.material.opacity = isActive ? 0.6 : 0.14;
    }
  });

  return (
    <group>
      {/* Étoiles */}
      <points ref={ref}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          size={0.16}
          sizeAttenuation
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          color={isActive ? '#F4EFE6' : '#D8B76A'}
          opacity={0.85}
        />
      </points>
      {/* Lignes entre les étoiles */}
      <lineSegments ref={lineRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
          <bufferAttribute attach="index" args={[lineIndices, 1]} />
        </bufferGeometry>
        <lineBasicMaterial
          color="#D8B76A"
          transparent
          opacity={0.2}
          depthWrite={false}
        />
      </lineSegments>
    </group>
  );
}

export default function Scene02Constellations() {
  const intent = useExperienceStore((s) => s.intent);
  return (
    <group>
      {Object.entries(CONSTELLATIONS).map(([id, pts]) => (
        <Constellation
          key={id}
          id={id}
          points={pts}
          center={CENTERS[id]}
          isActive={intent === id}
        />
      ))}
    </group>
  );
}
