import {useRef, useEffect, useState} from 'react';
import * as THREE from 'three';

/**
 * Moon3D — Vraie lune 3D en WebGL avec Three.js pur (pas de R3F JSX pour éviter
 * les conflits avec le plugin babel-metadata qui injecte des props debug).
 * - Shader procédural fBm (cratères, mers lunaires)
 * - Aura fluide Perlin dorée + halo indigo derrière
 * - Rotation continue + parallax souris/gyroscope
 * - Réagit aux étapes du form (rotation, phase d'éclairage, zoom)
 */

// ═══════════════ Shaders ═══════════════
// Note : moonVertexShader/moonFragmentShader historiques retirés — Moon3D utilise
// désormais MeshStandardMaterial (voir ligne ~270). Seuls auraVertex/Fragment
// restent en service pour le halo additif.

const auraVertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const auraFragmentShader = `
  precision highp float;
  varying vec2 vUv;
  uniform float uTime;

  vec3 mod289(vec3 x) { return x - floor(x * (1.0/289.0)) * 289.0; }
  vec2 mod289(vec2 x) { return x - floor(x * (1.0/289.0)) * 289.0; }
  vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

  float snoise(vec2 v) {
    const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                        -0.577350269189626, 0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy));
    vec2 x0 = v - i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod289(i);
    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
                    + i.x + vec3(0.0, i1.x, 1.0 ));
    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
                            dot(x12.zw,x12.zw)), 0.0);
    m = m*m; m = m*m;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
  }

  float fbm2(vec2 p) {
    float f = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
      f += a * snoise(p);
      p *= 2.03;
      a *= 0.5;
    }
    return f;
  }

  void main() {
    vec2 uv = vUv - 0.5;
    float d = length(uv);
    float n = fbm2(uv * 2.6 + vec2(uTime * 0.05, uTime * 0.03));
    float glow = smoothstep(0.55, 0.05, d + n * 0.10);

    // Palette Nuit Douce harmonisée — or brossé + bleu profond (fini les violets vifs)
    vec3 gold = vec3(0.83, 0.68, 0.22);
    vec3 midnight = vec3(0.10, 0.13, 0.24);
    vec3 deepBlue = vec3(0.07, 0.09, 0.16);

    // Coeur : lueur dorée douce ; halo : bleu nuit qui se fond dans la page
    vec3 col = mix(deepBlue, midnight, smoothstep(0.45, 0.10, d));
    col = mix(col, gold, smoothstep(0.28, 0.06, d) * 0.45);
    col += vec3(0.08, 0.07, 0.11) * n * 0.5;

    float intensity = glow * (0.42 + 0.10 * sin(uTime * 0.4));
    gl_FragColor = vec4(col * intensity, intensity * 0.70);
  }
`;

// ═══════════════ Composant principal ═══════════════
export default function Moon3D({ step = 1 }) {
  const containerRef = useRef(null);
  const [ready, setReady] = useState(false);
  const stateRef = useRef({
    mouseX: 0, mouseY: 0,
    targetRot: 0, targetZoom: 1, targetPhase: 1,
    disposed: false,
  });

  useEffect(() => {
    const s = stateRef.current;
    if (step === 1) { s.targetRot = 0;    s.targetZoom = 1.0;  s.targetPhase = 1.0; }
    if (step === 2) { s.targetRot = 1.57; s.targetZoom = 1.05; s.targetPhase = 0.85; }
    if (step === 3) { s.targetRot = 3.14; s.targetZoom = 1.18; s.targetPhase = 1.0; }
  }, [step]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const state = stateRef.current;
    state.disposed = false;

    let width = container.clientWidth;
    let height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 0, 4.8);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    // Lights (used only for ambient — moon has its own shader lighting)
    const ambient = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambient);

    // Aura plane (behind the moon)
    const auraMat = new THREE.ShaderMaterial({
      vertexShader: auraVertexShader,
      fragmentShader: auraFragmentShader,
      uniforms: { uTime: { value: 0 } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const auraGeom = new THREE.PlaneGeometry(4.5, 4.5);
    const auraMesh = new THREE.Mesh(auraGeom, auraMat);
    auraMesh.position.z = -0.6;
    scene.add(auraMesh);

    // Moon — vraie texture NASA (photo réelle) self-hostée
    const textureLoader = new THREE.TextureLoader();
    const moonTexture = textureLoader.load(
      '/assets/moon_1024.jpg',
      undefined, undefined,
      () => { /* silent fallback */ }
    );
    moonTexture.colorSpace = THREE.SRGBColorSpace;
    moonTexture.anisotropy = 4;

    const moonBumpMap = textureLoader.load(
      '/assets/moon_1024.jpg',
      undefined, undefined,
      () => { /* silent */ }
    );

    const moonMat = new THREE.MeshStandardMaterial({
      map: moonTexture,
      bumpMap: moonBumpMap,
      bumpScale: 0.04,
      roughness: 0.95,
      metalness: 0.0,
      emissive: new THREE.Color(0x1A2035),  // teinte Nuit Douce harmonisée (fin des violets)
      emissiveIntensity: 0.06,
    });
    const moonGeom = new THREE.SphereGeometry(1, 128, 128);
    const moonMesh = new THREE.Mesh(moonGeom, moonMat);
    scene.add(moonMesh);

    // Lumières dédiées à la lune (Solena palette)
    const keyLight = new THREE.DirectionalLight(0xF4E8D2, 1.6);
    keyLight.position.set(2.5, 2.0, 3.0);
    scene.add(keyLight);
    const rimLight = new THREE.DirectionalLight(0x8B6FE6, 0.35);  // violet
    rimLight.position.set(-2, -1, -1);
    scene.add(rimLight);

    // Mouse tracking
    const handleMouse = (e) => {
      const rect = container.getBoundingClientRect();
      state.mouseX = ((e.clientX - rect.left) / rect.width) - 0.5;
      state.mouseY = ((e.clientY - rect.top) / rect.height) - 0.5;
    };
    const handleTilt = (e) => {
      if (e.gamma !== null && e.beta !== null) {
        state.mouseX = Math.max(-0.5, Math.min(0.5, e.gamma / 60));
        state.mouseY = Math.max(-0.5, Math.min(0.5, (e.beta - 45) / 90));
      }
    };
    window.addEventListener('mousemove', handleMouse);
    window.addEventListener('deviceorientation', handleTilt);

    // Resize
    const handleResize = () => {
      if (!container) return;
      width = container.clientWidth;
      height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Animation loop (performance.now() replaces deprecated THREE.Clock)
    const startTime = performance.now();
    let currentScale = 1;
    setReady(true);

    let animId;
    const animate = () => {
      if (state.disposed) return;
      const t = (performance.now() - startTime) / 1000;

      // Rotation & zoom lerp
      const targetY = state.targetRot + state.mouseX * 0.35 + t * 0.06;
      const targetX = state.mouseY * 0.22;

      moonMesh.rotation.y += (targetY - moonMesh.rotation.y) * 0.04;
      moonMesh.rotation.x += (targetX - moonMesh.rotation.x) * 0.05;
      currentScale += (state.targetZoom - currentScale) * 0.05;
      moonMesh.scale.setScalar(currentScale);

      // Emissive intensity varie subtilement avec la phase
      moonMat.emissiveIntensity = 0.06 + (1 - state.targetPhase) * 0.15;

      // Aura anime son time uniform
      auraMat.uniforms.uTime.value = t;
      auraMesh.rotation.z = t * 0.02;

      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };
    animate();

    // Cleanup
    return () => {
      state.disposed = true;
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', handleMouse);
      window.removeEventListener('deviceorientation', handleTilt);
      window.removeEventListener('resize', handleResize);
      if (container && renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
      moonGeom.dispose();
      moonMat.dispose();
      auraGeom.dispose();
      auraMat.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ position: 'absolute', inset: 0, zIndex: 1, pointerEvents: 'none' }}
      data-testid="moon-3d-canvas"
    >
      {!ready && (
        <div style={{
          position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <div style={{ color: 'rgba(226,191,101,0.4)', fontSize: 10, letterSpacing: '0.3em', textTransform: 'uppercase' }}>
            La lune s&apos;éveille…
          </div>
        </div>
      )}
    </div>
  );
}
