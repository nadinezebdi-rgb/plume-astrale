/**
 * Scene 01 V2 — Entrée dans l'univers (profondeur cinématographique)
 * ─────────────────────────────────────────────────────────────
 * 3 couches de profondeur + fog exponentiel + bokeh premier plan rares.
 *
 *  • Fond : ~250 étoiles quasi-immobiles à z:-18..-8, très petites
 *  • Milieu : ~180 étoiles avec drift lent à z:-8..-2
 *  • Premier plan : 25 bokeh flous rares à z:0..4 (grosses particules floues)
 *  • Étoile centrale émissive qui respire
 *  • Fog exponentiel #070713 pour estomper naturellement la profondeur
 */
import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

const STAR_TEX = (() => {
  if (typeof document === 'undefined') return null;
  const s = 64;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255, 246, 220, 1)');
  g.addColorStop(0.25, 'rgba(216, 183, 106, 0.6)');
  g.addColorStop(0.55, 'rgba(118, 87, 200, 0.15)');
  g.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(c);
})();

const BOKEH_TEX = (() => {
  if (typeof document === 'undefined') return null;
  const s = 256;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255, 246, 220, 0.5)');
  g.addColorStop(0.3, 'rgba(216, 183, 106, 0.25)');
  g.addColorStop(0.7, 'rgba(118, 87, 200, 0.08)');
  g.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(c);
})();

function makeShellPositions(count, minR, maxR, zRange) {
  const arr = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const r = minR + Math.random() * (maxR - minR);
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    arr[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
    arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.7;
    arr[i * 3 + 2] = zRange[0] + Math.random() * (zRange[1] - zRange[0]);
  }
  return arr;
}

export default function Scene01Particles() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);

  const bgCount = isLowEnd ? 80 : isMobile ? 150 : 250;
  const midCount = isLowEnd ? 60 : isMobile ? 110 : 180;
  const fgCount = isLowEnd ? 0 : isMobile ? 12 : 25;

  const bgPositions = useMemo(() => makeShellPositions(bgCount, 8, 22, [-18, -8]), [bgCount]);
  const midPositions = useMemo(() => makeShellPositions(midCount, 4, 10, [-8, -2]), [midCount]);
  const fgPositions = useMemo(() => makeShellPositions(fgCount, 1.5, 4, [0, 4]), [fgCount]);

  const bgRef = useRef();
  const midRef = useRef();
  const fgRef = useRef();
  const centerRef = useRef();

  useFrame((state) => {
    if (reducedMotion) return;
    const t = state.clock.getElapsedTime();
    // Fond : quasi-immobile
    if (bgRef.current) bgRef.current.rotation.y = t * 0.003;
    // Milieu : drift lent
    if (midRef.current) {
      midRef.current.rotation.y = t * 0.012;
      midRef.current.rotation.x = Math.sin(t * 0.03) * 0.04;
    }
    // Premier plan bokeh : drift latéral occasionnel
    if (fgRef.current) {
      fgRef.current.position.x = Math.sin(t * 0.08) * 0.3;
      fgRef.current.rotation.z = t * 0.006;
    }
    // Étoile centrale respire
    if (centerRef.current) {
      const s = 1 + Math.sin(t * 0.6) * 0.05;
      centerRef.current.scale.setScalar(s);
    }
  });

  return (
    <group>
      {/* Fog exponentiel — les étoiles lointaines se fondent dans le noir */}
      <fogExp2 attach="fog" args={['#070713', 0.06]} />

      {/* Étoile centrale */}
      <sprite ref={centerRef} scale={[1.4, 1.4, 1]}>
        <spriteMaterial
          map={STAR_TEX}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.85}
          color="#F4EFE6"
        />
      </sprite>

      {/* Couche fond */}
      <points ref={bgRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[bgPositions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          map={STAR_TEX} size={0.15} sizeAttenuation
          transparent depthWrite={false} blending={THREE.AdditiveBlending}
          opacity={0.7} color="#F4EFE6"
        />
      </points>

      {/* Couche milieu */}
      <points ref={midRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[midPositions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          map={STAR_TEX} size={0.28} sizeAttenuation
          transparent depthWrite={false} blending={THREE.AdditiveBlending}
          opacity={0.85} color="#F4EFE6"
        />
      </points>

      {/* Premier plan bokeh — rares grosses particules floues */}
      {fgCount > 0 && (
        <points ref={fgRef}>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" args={[fgPositions, 3]} />
          </bufferGeometry>
          <pointsMaterial
            map={BOKEH_TEX} size={0.9} sizeAttenuation
            transparent depthWrite={false} blending={THREE.AdditiveBlending}
            opacity={0.16} color="#D8B76A"
          />
        </points>
      )}
    </group>
  );
}
