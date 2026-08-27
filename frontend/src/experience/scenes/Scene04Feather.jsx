/**
 * Scene 04 — Apparition de la plume + écriture "Plume Astrale"
 * ─────────────────────────────────────────────────────────────
 * LE MOMENT WOW en 4 phases :
 *   Phase A (0 → 5.0 s)  : dispersion → PLUME calligraphique (rachis courbé,
 *                          barbes asymétriques, pointe wispy)
 *   Phase B (5.0 → 7.0 s): la plume respire immobile (pause d'admiration)
 *   Phase C (7.0 → 10.0 s): morphing PLUME → texte "Plume Astrale"
 *   Phase D (10.0 s → ∞) : texte stable + sweep doré cinématique gauche→droite
 *
 * Le sweep cinématique est un sprite additif discret qui traverse le texte,
 * comme un rayon de lumière sur du velours — pas un flash, une caresse.
 */
import React, { useEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useExperienceStore } from '../useExperienceStore';

// Textures particules (halo doré doux)
const PARTICLE_TEX = (() => {
  if (typeof document === 'undefined') return null;
  const s = 64;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255, 246, 220, 1)');
  g.addColorStop(0.35, 'rgba(216, 183, 106, 0.5)');
  g.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(c);
})();

// Sprite de lumière cinématique (halo large ivoire/or)
const SWEEP_TEX = (() => {
  if (typeof document === 'undefined') return null;
  const s = 256;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255, 246, 220, 0.9)');
  g.addColorStop(0.25, 'rgba(216, 183, 106, 0.4)');
  g.addColorStop(0.6, 'rgba(118, 87, 200, 0.1)');
  g.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(c);
})();

// Sprite de la pointe de plume — halo elliptique doré pour figurer la tête d'écriture
const QUILL_TEX = (() => {
  if (typeof document === 'undefined') return null;
  const s = 128;
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, 'rgba(255, 250, 232, 1)');
  g.addColorStop(0.15, 'rgba(232, 199, 102, 0.8)');
  g.addColorStop(0.45, 'rgba(216, 183, 106, 0.25)');
  g.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(c);
})();

// ─── Génération des positions cibles PLUME ─────────────────────
// Design : vraie plume d'écrivain calligraphique.
//   • rachis vertical courbé légèrement (S doux)
//   • barbes ASYMÉTRIQUES : plus longues et incurvées d'un côté, plus courtes de l'autre
//   • pointe (haut) wispy — barbes plus rares, plus courtes
//   • base (bas) : quelques particules pour la pointe/calamus fine
function generateFeatherTargets(count) {
  const targets = new Float32Array(count * 3);
  const rachisCount = Math.floor(count * 0.14);       // 14% pour la colonne
  const rightBarbCount = Math.floor(count * 0.52);    // 52% côté long (droit)
  const leftBarbCount = Math.floor(count * 0.30);     // 30% côté court (gauche)
  const wispCount = count - rachisCount - rightBarbCount - leftBarbCount; // pointe

  // Utilitaire : position du rachis pour un paramètre t (0 = base, 1 = pointe)
  const rachisAt = (t) => {
    // Courbe S : rachis passe légèrement à droite au milieu, puis revient
    const y = (t - 0.5) * 3.4;                          // -1.7 → +1.7
    const x = Math.sin(t * Math.PI) * 0.18 - 0.05;      // courbure douce
    return [x, y];
  };

  let idx = 0;

  // 1. Rachis
  for (let i = 0; i < rachisCount; i++) {
    const t = i / (rachisCount - 1);
    const [rx, ry] = rachisAt(t);
    targets[idx * 3 + 0] = rx;
    targets[idx * 3 + 1] = ry;
    targets[idx * 3 + 2] = (Math.random() - 0.5) * 0.05;
    idx++;
  }

  // 2. Barbes côté DROIT (longues, incurvées vers la pointe)
  for (let i = 0; i < rightBarbCount; i++) {
    const t = 0.05 + Math.random() * 0.92; // évite base et pointe extrêmes
    const [rx, ry] = rachisAt(t);

    // Enveloppe : la plume est plus large vers 40% de sa hauteur
    // Bell-shape asymétrique, culminant vers t=0.35
    const envelope = Math.pow(Math.sin(Math.PI * t), 1.4) * 1.1;
    // Longueur de la barbe
    const barbLen = (0.35 + Math.random() * 0.75) * envelope;
    // Angle : les barbes s'inclinent vers la pointe (haut)
    // Plus t est grand (près de la pointe), plus l'angle monte
    const angle = -0.10 + t * 0.35; // -0.1 rad (léger descendant) → +0.25 rad (montant)

    // Position finale = rachis + vecteur perpendiculaire modifié
    const bx = rx + Math.cos(angle) * barbLen;
    const by = ry + Math.sin(angle) * barbLen;
    // Léger décalage aléatoire pour organicité
    const bz = (Math.random() - 0.5) * 0.14;
    const jitter = (Math.random() - 0.5) * 0.04;

    targets[idx * 3 + 0] = bx + jitter;
    targets[idx * 3 + 1] = by + jitter;
    targets[idx * 3 + 2] = bz;
    idx++;
  }

  // 3. Barbes côté GAUCHE (plus courtes — plume "d'un côté")
  for (let i = 0; i < leftBarbCount; i++) {
    const t = 0.08 + Math.random() * 0.88;
    const [rx, ry] = rachisAt(t);
    const envelope = Math.pow(Math.sin(Math.PI * t), 1.5) * 0.7; // enveloppe réduite
    const barbLen = (0.25 + Math.random() * 0.55) * envelope;
    const angle = Math.PI - 0.05 + t * 0.30; // ~PI (gauche), légère montée vers pointe

    const bx = rx + Math.cos(angle) * barbLen;
    const by = ry + Math.sin(angle) * barbLen;
    const bz = (Math.random() - 0.5) * 0.14;
    const jitter = (Math.random() - 0.5) * 0.04;

    targets[idx * 3 + 0] = bx + jitter;
    targets[idx * 3 + 1] = by + jitter;
    targets[idx * 3 + 2] = bz;
    idx++;
  }

  // 4. Wisps de pointe — quelques particules libres au bout, effet plume légère
  for (let i = 0; i < wispCount; i++) {
    const t = 0.88 + Math.random() * 0.14; // très haut
    const [rx, ry] = rachisAt(Math.min(1, t));
    const side = Math.random() < 0.65 ? 1 : -1; // majoritairement à droite
    const wispLen = Math.random() * 0.55 * (1 - (t - 0.88) / 0.14 * 0.6);
    const angle = side > 0 ? (0.15 + Math.random() * 0.35) : (Math.PI - 0.15 - Math.random() * 0.35);
    const bx = rx + Math.cos(angle) * wispLen;
    const by = ry + Math.sin(angle) * wispLen + Math.random() * 0.4;
    const bz = (Math.random() - 0.5) * 0.2;

    targets[idx * 3 + 0] = bx;
    targets[idx * 3 + 1] = by;
    targets[idx * 3 + 2] = bz;
    idx++;
  }

  return targets;
}

// ─── Génération des positions cibles TEXTE (via canvas 2D) ─────
// On dessine "Plume Astrale" en italique sur un canvas offscreen,
// puis on échantillonne les pixels opaques comme positions cibles.
function generateTextTargets(text, count, ctxOpts = {}) {
  if (typeof document === 'undefined') return new Float32Array(count * 3);

  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 220;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  // Font stack robuste : Playfair/Cormorant si chargés, sinon Georgia italic
  ctx.font = ctxOpts.font || 'italic 500 130px "Cormorant Garamond", "Playfair Display", Georgia, serif';
  ctx.fillText(text, canvas.width / 2, canvas.height / 2);

  const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const pixels = imgData.data;

  // Collecte des pixels opaques (une passe sur 3 pour économiser)
  const opaquePoints = [];
  for (let py = 0; py < canvas.height; py += 2) {
    for (let px = 0; px < canvas.width; px += 2) {
      const alpha = pixels[(py * canvas.width + px) * 4 + 3];
      if (alpha > 128) opaquePoints.push([px, py]);
    }
  }

  const targets = new Float32Array(count * 3);
  if (opaquePoints.length === 0) return targets; // fallback silencieux

  // Cadrage : occupe ~5.0 unités de large, ~1.0 de haut, centré sur (0, 0)
  const worldW = 5.2;
  const worldH = 1.1;
  for (let i = 0; i < count; i++) {
    const pt = opaquePoints[Math.floor(Math.random() * opaquePoints.length)];
    const nx = (pt[0] / canvas.width - 0.5) * worldW;
    const ny = -(pt[1] / canvas.height - 0.5) * worldH; // flip Y (canvas: top→down)
    targets[i * 3 + 0] = nx;
    targets[i * 3 + 1] = ny;
    targets[i * 3 + 2] = (Math.random() - 0.5) * 0.06;
  }
  return targets;
}

// ─── Composant ─────────────────────────────────────────────────

export default function Scene04Feather() {
  const isLowEnd = useExperienceStore((s) => s.isLowEnd);
  const isMobile = useExperienceStore((s) => s.isMobile);
  const currentScene = useExperienceStore((s) => s.currentScene);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);

  const count = isLowEnd ? 200 : isMobile ? 340 : 580;

  // Positions cibles : plume + texte (générées une fois)
  const {
    startPositions, featherTargets, textTargets,
    offsets, currentPositions, writeThresholds,
    chaosOffsets,
  } = useMemo(() => {
    const startPositions = new Float32Array(count * 3);
    const featherTargets = generateFeatherTargets(count);
    const textTargets = generateTextTargets('Plume Astrale', count);
    const offsets = new Float32Array(count);
    const currentPositions = new Float32Array(count * 3);
    // writeThreshold[i] = position X du texte normalisée sur [0..1]
    //   → détermine QUAND cette particule commence à se placer pendant l'écriture
    const writeThresholds = new Float32Array(count);
    // Chaos : bruit local propre à chaque particule
    const chaosOffsets = new Float32Array(count * 2);

    // Bornes X du texte pour normaliser
    let minX = Infinity, maxX = -Infinity;
    for (let i = 0; i < count; i++) {
      const tx = textTargets[i * 3 + 0];
      if (tx < minX) minX = tx;
      if (tx > maxX) maxX = tx;
    }
    const textWidth = Math.max(0.001, maxX - minX);

    for (let i = 0; i < count; i++) {
      const r = 3 + Math.random() * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      startPositions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      startPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      startPositions[i * 3 + 2] = r * Math.cos(phi) - 2;
      currentPositions[i * 3 + 0] = startPositions[i * 3 + 0];
      currentPositions[i * 3 + 1] = startPositions[i * 3 + 1];
      currentPositions[i * 3 + 2] = startPositions[i * 3 + 2];
      offsets[i] = Math.random() * Math.PI * 2;
      // WriteThreshold: 0 pour particule extrême gauche, 1 pour extrême droite
      writeThresholds[i] = (textTargets[i * 3 + 0] - minX) / textWidth;
      // Chaos offsets (petit vecteur perturbateur pour chaos phase)
      chaosOffsets[i * 2 + 0] = (Math.random() - 0.5) * 0.15;
      chaosOffsets[i * 2 + 1] = (Math.random() - 0.5) * 0.15;
    }
    return {
      startPositions, featherTargets, textTargets, offsets,
      currentPositions, writeThresholds, chaosOffsets,
    };
  }, [count]);

  // Timings des phases (en secondes)
  const T_CHAOS = reducedMotion ? 0.2 : 0.8;         // chaos initial
  const T_ATTRACTION = reducedMotion ? 0.2 : 0.8;    // attraction subtile
  const T_FORMATION = reducedMotion ? 0.4 : 4.4;     // formation complète plume
  const T_PAUSE = reducedMotion ? 0.2 : 2.0;         // silence visuel
  const T_WRITING = reducedMotion ? 0.4 : 4.0;       // écriture synchronisée gauche→droite

  // Cumulatifs
  const T_END_CHAOS = T_CHAOS;
  const T_END_ATTRACTION = T_END_CHAOS + T_ATTRACTION;
  const T_END_FORMATION = T_END_ATTRACTION + T_FORMATION;
  const T_END_PAUSE = T_END_FORMATION + T_PAUSE;
  const T_END_WRITING = T_END_PAUSE + T_WRITING;

  const pointsRef = useRef();
  const geoRef = useRef();
  const sweepRef = useRef();
  const quillRef = useRef();
  const startTimeRef = useRef(null);

  // Démarre le chronomètre dès que la scène 4 devient active
  useEffect(() => {
    if (currentScene === 4 && startTimeRef.current === null) {
      startTimeRef.current = performance.now();
    }
    if (currentScene < 4) {
      startTimeRef.current = null;
    }
  }, [currentScene]);

  // ─── Régénère les positions cibles texte quand les fonts sont chargées ──
  const textTargetsRef = useRef(textTargets);
  useEffect(() => {
    if (typeof document === 'undefined' || !document.fonts) return;
    document.fonts.ready.then(() => {
      textTargetsRef.current = generateTextTargets('Plume Astrale', count);
    });
  }, [count]);

  useFrame((state) => {
    if (!geoRef.current) return;
    const t = state.clock.getElapsedTime();

    let elapsed = 0;
    if (startTimeRef.current !== null) {
      elapsed = (performance.now() - startTimeRef.current) / 1000;
    }

    const posAttr = geoRef.current.attributes.position;
    const activeTextTargets = textTargetsRef.current;

    // Détermine la phase courante
    // Phase A CHAOS         [0, T_END_CHAOS]         particules oscillent en place à leur position de départ
    // Phase B ATTRACTION    [T_END_CHAOS, T_END_ATTRACTION]   drift subtil vers plume (10%)
    // Phase C FORMATION     [T_END_ATTRACTION, T_END_FORMATION]  interpolation start → plume
    // Phase D PAUSE         [T_END_FORMATION, T_END_PAUSE]    plume respire
    // Phase E WRITING       [T_END_PAUSE, T_END_WRITING]     écriture synchronisée gauche→droite
    // Phase F STABLE        [T_END_WRITING, ∞)             texte stable + sweep

    // writeProgress (0..1) sur toute la phase E
    let writeProgress = 0;
    if (elapsed >= T_END_PAUSE) {
      writeProgress = Math.min(1, (elapsed - T_END_PAUSE) / T_WRITING);
    }

    for (let i = 0; i < count; i++) {
      const sx = startPositions[i * 3 + 0];
      const sy = startPositions[i * 3 + 1];
      const sz = startPositions[i * 3 + 2];
      const fx = featherTargets[i * 3 + 0];
      const fy = featherTargets[i * 3 + 1];
      const fz = featherTargets[i * 3 + 2];
      const tx = activeTextTargets[i * 3 + 0];
      const ty = activeTextTargets[i * 3 + 1];
      const tz = activeTextTargets[i * 3 + 2];

      let x, y, z;

      if (elapsed < T_END_CHAOS) {
        // Phase A CHAOS — oscillation locale, aucun mouvement vers cible
        const cx = chaosOffsets[i * 2 + 0];
        const cy = chaosOffsets[i * 2 + 1];
        x = sx + Math.sin(t * 1.5 + offsets[i]) * cx;
        y = sy + Math.cos(t * 1.5 + offsets[i]) * cy;
        z = sz;
      } else if (elapsed < T_END_ATTRACTION) {
        // Phase B ATTRACTION — dérive subtile vers plume (0 → 10%)
        const p = (elapsed - T_END_CHAOS) / T_ATTRACTION;
        const eased = p * p; // ease-in
        const drift = eased * 0.10;
        x = sx + (fx - sx) * drift;
        y = sy + (fy - sy) * drift;
        z = sz + (fz - sz) * drift;
      } else if (elapsed < T_END_FORMATION) {
        // Phase C FORMATION — dispersion → plume complète (10% → 100%)
        const p = (elapsed - T_END_ATTRACTION) / T_FORMATION;
        const p2 = 0.10 + p * 0.90;
        const eased = 1 - Math.pow(1 - p2, 3);
        x = sx + (fx - sx) * eased;
        y = sy + (fy - sy) * eased;
        z = sz + (fz - sz) * eased;
      } else if (elapsed < T_END_PAUSE) {
        // Phase D PAUSE — plume respire
        x = fx; y = fy; z = fz;
        if (!reducedMotion) {
          const breath = Math.sin(t * 0.6 + offsets[i]) * 0.015;
          x += breath;
          y += breath * 0.5;
        }
      } else if (elapsed < T_END_WRITING) {
        // Phase E WRITING — synchronisée gauche → droite
        // Chaque particule ne bouge vers son texte QUE lorsque writeProgress dépasse son seuil
        const FADE_WINDOW = 0.14;
        const threshold = writeThresholds[i];
        const local = Math.max(0, Math.min(1,
          (writeProgress - threshold) / FADE_WINDOW
        ));
        // ease-out cubic
        const eased = 1 - Math.pow(1 - local, 3);
        x = fx + (tx - fx) * eased;
        y = fy + (ty - fy) * eased;
        z = fz + (tz - fz) * eased;
      } else {
        // Phase F STABLE — texte + micro-respiration
        x = tx; y = ty; z = tz;
        if (!reducedMotion) {
          const breath = Math.sin(t * 0.5 + offsets[i]) * 0.008;
          x += breath;
        }
      }

      posAttr.array[i * 3 + 0] = x;
      posAttr.array[i * 3 + 1] = y;
      posAttr.array[i * 3 + 2] = z;
    }
    posAttr.needsUpdate = true;

    // ─── QUILL sprite : suit la tête d'écriture pendant phase E ────
    if (quillRef.current) {
      const inWriting = elapsed >= T_END_PAUSE && elapsed < T_END_WRITING + 0.5;
      quillRef.current.visible = inWriting;
      if (inWriting && !reducedMotion) {
        // Bornes X du texte pour la position de la pointe
        const TEXT_HALF_W = 2.6; // aligne avec generateTextTargets worldW/2
        const headX = -TEXT_HALF_W + writeProgress * (TEXT_HALF_W * 2);
        quillRef.current.position.x = headX;
        quillRef.current.position.y = 0.4;
        quillRef.current.position.z = 0.05;
        // Fade in au début, fade out à la fin
        const fadeIn = Math.min(1, (elapsed - T_END_PAUSE) / 0.4);
        const fadeOut = Math.min(1, Math.max(0, (T_END_WRITING + 0.5 - elapsed) / 0.5));
        quillRef.current.material.opacity = 0.7 * fadeIn * fadeOut;
      }
    }

    // ─── SWEEP cinématique : uniquement en phase F ────
    if (sweepRef.current) {
      const inPhaseF = elapsed >= T_END_WRITING;
      if (inPhaseF && !reducedMotion) {
        const sweepT = ((elapsed - T_END_WRITING) % 8) / 8;
        const inSweep = sweepT > 0.10 && sweepT < 0.90;
        sweepRef.current.visible = inSweep;
        if (inSweep) {
          const local = (sweepT - 0.10) / 0.80;
          sweepRef.current.position.x = -3.5 + local * 7.0;
          sweepRef.current.position.y = 0.4;
          const fade = Math.sin(local * Math.PI);
          sweepRef.current.material.opacity = 0.55 * fade;
        }
      } else {
        sweepRef.current.visible = false;
      }
    }

    // Rotation douce plume en phase D
    if (pointsRef.current) {
      const inBreathing = elapsed >= T_END_FORMATION && elapsed < T_END_PAUSE;
      const rotTarget = inBreathing ? Math.sin(t * 0.3) * 0.05 : 0;
      pointsRef.current.rotation.z = THREE.MathUtils.lerp(
        pointsRef.current.rotation.z, rotTarget, 0.03
      );
    }
  });

  return (
    <group>
      <points ref={pointsRef} position={[0, 0.4, 0]}>
        <bufferGeometry ref={geoRef}>
          <bufferAttribute
            attach="attributes-position"
            args={[currentPositions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          map={PARTICLE_TEX}
          size={0.1}
          sizeAttenuation
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.95}
          color="#F4EFE6"
        />
      </points>

      {/* Sweep cinématique — halo doré large qui traverse le texte */}
      <sprite ref={sweepRef} scale={[2.2, 1.6, 1]} position={[0, 0.4, 0]} visible={false}>
        <spriteMaterial
          map={SWEEP_TEX}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0}
          color="#F4EFE6"
        />
      </sprite>

      {/* Quill — pointe de plume qui trace le texte pendant la phase E */}
      <sprite ref={quillRef} scale={[0.5, 0.35, 1]} position={[-2.6, 0.4, 0.05]} visible={false}>
        <spriteMaterial
          map={QUILL_TEX}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0}
          color="#F4EFE6"
        />
      </sprite>
    </group>
  );
}
