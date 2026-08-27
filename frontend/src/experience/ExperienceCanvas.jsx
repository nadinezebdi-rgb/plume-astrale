/**
 * ExperienceCanvas — un unique <Canvas> R3F qui traverse les 4 scènes.
 * ─────────────────────────────────────────────────────────────────────
 * • La caméra glisse de z=6 (scène 1, on part de très près de l'étoile)
 *   jusqu'à z=-8 (scène 4, on recule pour découvrir la plume).
 * • Chaque scène 3D est un <group> positionné le long de l'axe Z, à des
 *   distances calculées. Le scroll pilote la position Y de la caméra (ou
 *   la caméra reste fixe et on translate les groups — plus stable ici).
 * • Aucun postprocessing (bundle plus léger, meilleure compat mobile).
 *   Le bloom est faux : sprites additifs sur les particules.
 */
import React, { Suspense, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from './useExperienceStore';
import Scene01Particles from './scenes/Scene01Particles';
import Scene02Constellations from './scenes/Scene02Constellations';
import Scene03Velvet from './scenes/Scene03Velvet';
import Scene04Feather from './scenes/Scene04Feather';

// ─── Contrôleur caméra + scènes ────────────────────────────────
function StageController() {
  const groupRef = useRef();
  const globalProgress = useExperienceStore((s) => s.globalProgress);
  const isMobile = useExperienceStore((s) => s.isMobile);

  useFrame((state) => {
    if (!groupRef.current) return;
    // Le "stage" translate en Y en fonction du scroll global (0..1 sur 4 scènes)
    const targetY = globalProgress * -18; // amplitude
    groupRef.current.position.y = THREE.MathUtils.lerp(
      groupRef.current.position.y,
      targetY,
      0.06
    );

    // Léger drift caméra sur l'axe X selon la souris (desktop uniquement)
    if (!isMobile) {
      const { x, y } = state.pointer;
      state.camera.position.x = THREE.MathUtils.lerp(state.camera.position.x, x * 0.4, 0.04);
      state.camera.position.y = THREE.MathUtils.lerp(state.camera.position.y, y * 0.3, 0.04);
      state.camera.lookAt(0, groupRef.current.position.y * -0.02, 0);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Scène 1 — origine (autour de y=0) */}
      <group position={[0, 0, 0]}>
        <Scene01Particles />
      </group>
      {/* Scène 2 — constellations (y=+6, donc apparaît quand stage descend) */}
      <group position={[0, 6, 0]}>
        <Scene02Constellations />
      </group>
      {/* Scène 3 — velours + cartes (y=+12) */}
      <group position={[0, 12, 0]}>
        <Scene03Velvet />
      </group>
      {/* Scène 4 — plume (y=+18) */}
      <group position={[0, 18, 0]}>
        <Scene04Feather />
      </group>
    </group>
  );
}

export default function ExperienceCanvas() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);

  return (
    <div className="exp-canvas-layer" data-testid="experience-canvas">
      <Canvas
        camera={{ position: [0, 0, 6], fov: 55, near: 0.1, far: 100 }}
        dpr={isMobile ? [1, 1.25] : [1, 1.5]}
        gl={{
          antialias: !isLowEnd,
          alpha: false,
          powerPreference: 'high-performance',
        }}
        style={{ background: '#070713' }}
      >
        <color attach="background" args={['#070713']} />
        <ambientLight intensity={0.15} color="#7657C8" />
        <Suspense fallback={null}>
          <StageController />
        </Suspense>
      </Canvas>
    </div>
  );
}
