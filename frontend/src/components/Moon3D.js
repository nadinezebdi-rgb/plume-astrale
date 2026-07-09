import React, { useRef, useEffect, useState } from 'react';
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
const moonVertexShader = `
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying vec2 vUv;
  void main() {
    vNormal = normalize(normalMatrix * normal);
    vPosition = position;
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const moonFragmentShader = `
  precision highp float;
  varying vec3 vNormal;
  varying vec3 vPosition;
  varying vec2 vUv;

  uniform vec3 uLightDir;
  uniform float uTime;
  uniform float uPhase;

  vec3 mod289(vec3 x) { return x - floor(x * (1.0/289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0/289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

  float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute( permute( permute(
              i.z + vec4(0.0, i1.z, i2.z, 1.0))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }

  float fbm(vec3 p) {
    float f = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
      f += a * snoise(p);
      p *= 2.02;
      a *= 0.5;
    }
    return f;
  }

  void main() {
    vec3 p = normalize(vPosition) * 2.5;
    float craters = smoothstep(-0.05, 0.35, fbm(p * 3.2 + 5.0));
    float dark = smoothstep(0.15, 0.55, fbm(p * 1.5 - 2.0));

    vec3 highland = vec3(0.94, 0.87, 0.72);
    vec3 mare     = vec3(0.42, 0.34, 0.24);
    vec3 shadow   = vec3(0.14, 0.10, 0.06);

    vec3 base = mix(highland, mare, dark);
    base = mix(base, shadow, craters * 0.35);

    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightDir);
    float lambert = max(dot(N, L), 0.0);
    float rim = pow(1.0 - max(dot(N, vec3(0.0, 0.0, 1.0)), 0.0), 3.0);

    vec3 lit = base * (0.15 + lambert * 1.05);
    lit += vec3(0.85, 0.68, 0.35) * rim * 0.4;

    lit *= mix(0.72, 1.0, smoothstep(0.0, 1.0, uPhase));

    gl_FragColor = vec4(lit, 1.0);
  }
`;

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

    // Palette violet-indigo pour matcher la section Solena
    vec3 gold = vec3(0.95, 0.72, 0.28);
    vec3 violet = vec3(0.45, 0.32, 0.85);
    vec3 indigo = vec3(0.18, 0.10, 0.42);

    // Coeur : subtile lueur dorée près de la lune ; halo : violet ambiant
    vec3 col = mix(indigo, violet, smoothstep(0.45, 0.10, d));
    col = mix(col, gold, smoothstep(0.28, 0.06, d) * 0.55);
    col += vec3(0.10, 0.06, 0.20) * n * 0.6;

    float intensity = glow * (0.45 + 0.12 * sin(uTime * 0.4));
    gl_FragColor = vec4(col * intensity, intensity * 0.75);
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
      emissive: new THREE.Color(0x2a1e4a),  // teinte violette indigo subtile
      emissiveIntensity: 0.08,
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
