import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as THREE from 'three';

/**
 * EnhancedMoon3D - Lune 3D photoréaliste avec améliorations :
 * - Texture NASA haute résolution
 * - Shader procédural fBm pour les cratères
 * - Aura fluide Perlin (or + violet/indigo)
 * - Interaction souris/gyroscope ultra-fluide
 * - Réactions dynamiques aux étapes du formulaire
 * - Optimisation mobile (compression, lazy loading)
 * - Effet de "liquid morphing" sur l'aura
 */

// ==================== SHADERS ====================

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
  uniform sampler2D uTexture;
  uniform sampler2D uBumpMap;

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
    // Sample texture
    vec4 texColor = texture2D(uTexture, vUv);
    
    // Add procedural details
    vec3 p = normalize(vPosition) * 2.5;
    float craters = smoothstep(-0.05, 0.35, fbm(p * 3.2 + 5.0 + uTime * 0.01));
    float dark = smoothstep(0.15, 0.55, fbm(p * 1.5 - 2.0));

    vec3 highland = vec3(0.94, 0.87, 0.72);
    vec3 mare     = vec3(0.42, 0.34, 0.24);
    vec3 shadow   = vec3(0.14, 0.10, 0.06);

    // Mix texture with procedural
    vec3 base = mix(highland, mare, dark);
    base = mix(base, shadow, craters * 0.35);
    base = mix(texColor.rgb, base, 0.7);

    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightDir);
    float lambert = max(dot(N, L), 0.0);
    float rim = pow(1.0 - max(dot(N, vec3(0.0, 0.0, 1.0)), 0.0), 3.0);

    vec3 lit = base * (0.15 + lambert * 1.05);
    lit += vec3(0.85, 0.68, 0.35) * rim * 0.4;

    // Phase effect (waxing/waning)
    lit *= mix(0.72, 1.0, smoothstep(0.0, 1.0, uPhase));

    // Add subtle violet tint for harmony with aura
    lit = mix(lit, lit * vec3(0.95, 0.90, 1.05), 0.08);

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
  uniform float uStep;

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
    
    // Animated noise for fluid morphing
    float n = fbm2(uv * 2.6 + vec2(uTime * 0.05, uTime * 0.03));
    float n2 = fbm2(uv * 1.8 + vec2(uTime * -0.03, uTime * 0.05));
    
    // Combine noises for complex pattern
    float noise = mix(n, n2, 0.5);
    
    // Glow effect based on distance and noise
    float glow = smoothstep(0.55, 0.05, d + noise * 0.10);
    
    // Dynamic pulse based on step
    float pulse = 0.5 + 0.5 * sin(uTime * 0.3 + uStep * 0.5);
    
    // Color palette: Gold + Violet/Indigo
    vec3 gold = vec3(0.95, 0.72, 0.28);
    vec3 goldBright = vec3(1.0, 0.85, 0.45);
    vec3 violet = vec3(0.45, 0.32, 0.85);
    vec3 indigo = vec3(0.18, 0.10, 0.42);
    vec3 indigoDeep = vec3(0.08, 0.05, 0.25);
    
    // Create gradient based on distance
    // Inner: gold glow
    // Middle: violet transition
    // Outer: indigo halo
    vec3 col = mix(indigoDeep, indigo, smoothstep(0.7, 0.4, d));
    col = mix(col, violet, smoothstep(0.4, 0.2, d));
    col = mix(col, gold, smoothstep(0.2, 0.05, d) * 0.6);
    col = mix(col, goldBright, smoothstep(0.1, 0.0, d) * 0.8);
    
    // Add noise variation
    col += vec3(0.10, 0.06, 0.20) * noise * 0.6;
    
    // Intensity with pulse effect
    float intensity = glow * (0.45 + 0.12 * sin(uTime * 0.4)) * pulse;
    
    // Step-based color shift
    if (uStep == 2.0) {
      col = mix(col, gold, 0.3);
    } else if (uStep == 3.0) {
      col = mix(col, goldBright, 0.4);
    }
    
    gl_FragColor = vec4(col * intensity, intensity * 0.85);
  }
`;

// ==================== COMPOSANT PRINCIPAL ====================

export default function EnhancedMoon3D({ step = 1, isLoading = false }) {
  const containerRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const stateRef = useRef({
    mouseX: 0,
    mouseY: 0,
    targetRot: 0,
    targetZoom: 1,
    targetPhase: 1,
    currentRotY: 0,
    currentRotX: 0,
    currentScale: 1,
    disposed: false,
  });

  // Mettre à jour les cibles en fonction de l'étape
  useEffect(() => {
    const s = stateRef.current;
    if (step === 1) { 
      s.targetRot = 0; 
      s.targetZoom = 1.0; 
      s.targetPhase = 1.0; 
    }
    if (step === 2) { 
      s.targetRot = Math.PI / 2; 
      s.targetZoom = 1.08; 
      s.targetPhase = 0.85; 
    }
    if (step === 3) { 
      s.targetRot = Math.PI; 
      s.targetZoom = 1.25; 
      s.targetPhase = 1.0; 
    }
  }, [step]);

  // Initialisation Three.js
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const state = stateRef.current;
    state.disposed = false;

    let width = container.clientWidth;
    let height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 5.5);

    // Renderer avec optimisations
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
      precision: 'highp',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.15);
    scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xF4E8D2, 1.8);
    keyLight.position.set(3, 2.5, 4);
    keyLight.castShadow = false;
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x8B6FE6, 0.4);
    rimLight.position.set(-2.5, -1.5, -2);
    scene.add(rimLight);

    const fillLight = new THREE.DirectionalLight(0xD4B46A, 0.3);
    fillLight.position.set(-1, 1, 2);
    scene.add(fillLight);

    // Aura plane (behind the moon) - plus grande pour un meilleur effet
    const auraMat = new THREE.ShaderMaterial({
      vertexShader: auraVertexShader,
      fragmentShader: auraFragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uStep: { value: step }
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    
    const auraGeom = new THREE.PlaneGeometry(6, 6, 32, 32);
    const auraMesh = new THREE.Mesh(auraGeom, auraMat);
    auraMesh.position.z = -1.2;
    scene.add(auraMesh);

    // Moon avec texture NASA
    const textureLoader = new THREE.TextureLoader();
    
    // Charger la texture de la lune
    const moonTexture = textureLoader.load(
      '/assets/moon_1024.jpg',
      (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = 8;
        setProgress(prev => Math.min(prev + 30, 100));
      },
      undefined,
      () => {
        // Fallback si erreur de chargement
        console.warn('Moon texture failed to load, using procedural');
        setProgress(prev => Math.min(prev + 30, 100));
      }
    );
    
    // Charger la bump map
    const moonBumpMap = textureLoader.load(
      '/assets/moon_1024.jpg',
      (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = 4;
        setProgress(prev => Math.min(prev + 30, 100));
      },
      undefined,
      () => setProgress(prev => Math.min(prev + 30, 100))
    );

    // Matériau de la lune avec shader
    const moonMat = new THREE.ShaderMaterial({
      vertexShader: moonVertexShader,
      fragmentShader: moonFragmentShader,
      uniforms: {
        uLightDir: { value: new THREE.Vector3(0.5, 0.3, 0.7).normalize() },
        uTime: { value: 0 },
        uPhase: { value: 1.0 },
        uTexture: { value: moonTexture },
        uBumpMap: { value: moonBumpMap }
      },
    });
    
    const moonGeom = new THREE.SphereGeometry(1.1, 128, 128);
    const moonMesh = new THREE.Mesh(moonGeom, moonMat);
    scene.add(moonMesh);

    // Gestion des événements
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

    const handleResize = () => {
      if (!container) return;
      width = container.clientWidth;
      height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('mousemove', handleMouse, { passive: true });
    window.addEventListener('deviceorientation', handleTilt, { passive: true });
    window.addEventListener('resize', handleResize, { passive: true });

    // Animation loop
    const clock = new THREE.Clock();
    let animId;
    
    const animate = () => {
      if (state.disposed) return;
      
      const t = clock.getElapsedTime();
      const delta = clock.getDelta();

      // Rotation fluide avec inertie
      const targetY = state.targetRot + state.mouseX * 0.4 + t * 0.04;
      const targetX = state.mouseY * 0.25;

      // Lerp pour une animation douce
      state.currentRotY += (targetY - state.currentRotY) * 0.06 * (delta * 60);
      state.currentRotX += (targetX - state.currentRotX) * 0.08 * (delta * 60);
      
      moonMesh.rotation.y = state.currentRotY;
      moonMesh.rotation.x = state.currentRotX;

      // Zoom fluide
      state.currentScale += (state.targetZoom - state.currentScale) * 0.08 * (delta * 60);
      moonMesh.scale.setScalar(state.currentScale);

      // Phase de la lune (pour l'éclairage)
      moonMat.uniforms.uPhase.value = state.targetPhase;
      
      // Mettre à jour la direction de la lumière
      const lightAngle = t * 0.1;
      moonMat.uniforms.uLightDir.value.set(
        Math.cos(lightAngle) * 0.7,
        Math.sin(lightAngle) * 0.3,
        0.6
      ).normalize();

      // Mettre à jour le temps pour les shaders
      moonMat.uniforms.uTime.value = t;
      auraMat.uniforms.uTime.value = t;
      auraMat.uniforms.uStep.value = step;

      // Rotation subtile de l'aura
      auraMesh.rotation.z = t * 0.015;

      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };

    // Démarrer l'animation
    animate();
    setReady(true);
    setProgress(100);

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
      
      // Nettoyage des ressources
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
      style={{ 
        position: 'absolute', 
        inset: 0, 
        zIndex: 1, 
        pointerEvents: 'none' 
      }}
      data-testid="enhanced-moon-3d"
    >
      {!ready && progress < 100 && (
        <div style={{
          position: 'absolute', 
          inset: 0, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
        }}>
          <div style={{
            color: 'rgba(226, 191, 101, 0.4)',
            fontSize: 10,
            letterSpacing: '0.3em',
            textTransform: 'uppercase',
            fontFamily: 'Inter, sans-serif',
          }}>
            {isLoading ? 'La lune s\'éveille…' : `Chargement ${progress}%`}
          </div>
        </div>
      )}
      
      {/* Overlay pour améliorer le contraste */}
      <div style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        background: 'radial-gradient(ellipse at 50% 50%, transparent 30%, rgba(0,0,0,0.15) 70%, rgba(0,0,0,0.4) 100%)',
      }} />
    </div>
  );
}
