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

// Centres des 4 constellations — plus profondes (z:-4..-1) pour créer l'immersion "au milieu"
const CENTERS = {
  relationship:  new THREE.Vector3(-3.0,  1.5, -3.2),
  clarity:       new THREE.Vector3( 3.0,  1.5, -1.8),
  selfDiscovery: new THREE.Vector3(-3.0, -1.5, -1.8),
  question:      new THREE.Vector3( 3.0, -1.5, -3.2),
};

function Constellation({ id, points, center, isActive, isHovered, isDimmed }) {
  const groupRef = useRef();
  const pointsMatRef = useRef();
  const lineMatRef = useRef();

  const positions = useMemo(() => {
    const arr = new Float32Array(points.length * 3);
    points.forEach(([x, y], i) => {
      arr[i * 3 + 0] = x * 1.4;
      arr[i * 3 + 1] = y * 1.4;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 0.4;
    });
    return arr;
  }, [points]);

  const lineIndices = useMemo(() => {
    const arr = [];
    for (let i = 0; i < points.length - 1; i++) arr.push(i, i + 1);
    return new Uint16Array(arr);
  }, [points.length]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (!groupRef.current) return;

    // Cible Z : hover ou active = avance vers la caméra (+0.6)
    const zTarget = center.z + (isHovered || isActive ? 0.6 : 0);
    groupRef.current.position.x = center.x;
    groupRef.current.position.y = center.y + Math.sin(t * 0.4 + center.x) * 0.05;
    groupRef.current.position.z = THREE.MathUtils.lerp(
      groupRef.current.position.z, zTarget, 0.08
    );

    // Opacités : dimmed = fade, active/hover = brillant
    if (pointsMatRef.current) {
      const targetOpacity = isDimmed ? 0.15 : (isHovered || isActive ? 1.0 : 0.72);
      pointsMatRef.current.opacity = THREE.MathUtils.lerp(
        pointsMatRef.current.opacity, targetOpacity, 0.1
      );
    }
    if (lineMatRef.current) {
      const targetOpacity = isDimmed ? 0.02 : (isHovered || isActive ? 0.75 : 0.16);
      lineMatRef.current.opacity = THREE.MathUtils.lerp(
        lineMatRef.current.opacity, targetOpacity, 0.1
      );
    }
  });

  return (
    <group ref={groupRef}>
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          ref={pointsMatRef}
          size={0.18}
          sizeAttenuation
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          color={isHovered || isActive ? '#F4EFE6' : '#D8B76A'}
          opacity={0.72}
        />
      </points>
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
          <bufferAttribute attach="index" args={[lineIndices, 1]} />
        </bufferGeometry>
        <lineBasicMaterial
          ref={lineMatRef}
          color="#D8B76A"
          transparent
          opacity={0.16}
          depthWrite={false}
        />
      </lineSegments>
    </group>
  );
}

export default function Scene02Constellations() {
  const intent = useExperienceStore((s) => s.intent);
  const hoveredIntent = useExperienceStore((s) => s.hoveredIntent);

  return (
    <group>
      {Object.entries(CONSTELLATIONS).map(([id, pts]) => {
        const isActive = intent === id;
        const isHovered = hoveredIntent === id;
        const isDimmed = (intent !== null && !isActive) || (hoveredIntent !== null && !isHovered);
        return (
          <Constellation
            key={id}
            id={id}
            points={pts}
            center={CENTERS[id]}
            isActive={isActive}
            isHovered={isHovered}
            isDimmed={isDimmed}
          />
        );
      })}
    </group>
  );
}
