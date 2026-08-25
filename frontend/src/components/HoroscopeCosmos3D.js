import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

/**
 * HoroscopeCosmos3D — Scène cosmique (Three.js pur, pas de R3F JSX pour rester
 * cohérent avec Moon3D et éviter les conflits babel-metadata).
 * - Planète centrale 100% procédurale (shader fBm)
 * - Planètes en orbite
 * - Constellation du signe zodiacal reliée par des traits
 * Palette Nuit Douce : or #D4AF37, crème #F4E8D2, bleu nuit.
 */

// Formes stylisées des 12 constellations (coordonnées normalisées -1..1)
const ZODIAC_SHAPES = {
  'Bélier':     [[-0.6, 0.3], [-0.2, 0.5], [0.2, 0.2], [0.5, -0.3]],
  'Taureau':    [[-0.5, -0.3], [-0.2, 0.1], [0.1, 0.3], [0.4, 0.2], [0.6, 0.5], [0.1, 0.3], [0.3, -0.4]],
  'Gémeaux':    [[-0.4, -0.5], [-0.4, 0.5], [-0.1, 0.4], [0.3, 0.5], [0.3, -0.5], [-0.1, -0.4], [-0.1, 0.4]],
  'Cancer':     [[-0.5, 0.3], [-0.1, 0.1], [0.2, 0.4], [0.2, -0.3], [-0.1, 0.1]],
  'Lion':       [[-0.6, -0.2], [-0.3, 0.2], [0.0, 0.4], [0.3, 0.2], [0.5, -0.2], [0.2, -0.4], [-0.1, -0.3]],
  'Vierge':     [[-0.6, 0.2], [-0.2, 0.3], [0.1, 0.0], [0.4, 0.2], [0.1, 0.0], [0.2, -0.4]],
  'Balance':    [[-0.5, -0.2], [-0.2, 0.2], [0.2, 0.2], [0.5, -0.2], [-0.2, 0.2], [0.2, 0.2]],
  'Scorpion':   [[-0.6, 0.3], [-0.3, 0.2], [0.0, 0.0], [0.2, -0.2], [0.4, -0.4], [0.6, -0.2]],
  'Sagittaire': [[-0.5, -0.4], [-0.1, 0.0], [0.3, 0.4], [-0.1, 0.0], [0.1, -0.3], [-0.1, 0.0], [-0.3, 0.3]],
  'Capricorne': [[-0.6, 0.2], [-0.2, 0.4], [0.2, 0.1], [0.5, -0.3], [-0.2, 0.4]],
  'Verseau':    [[-0.6, 0.1], [-0.3, 0.3], [0.0, 0.1], [0.3, 0.3], [0.6, 0.1]],
  'Poissons':   [[-0.6, 0.3], [-0.3, 0.1], [0.0, 0.2], [0.3, 0.0], [0.6, 0.3], [0.0, 0.2], [0.1, -0.4]],
};

const planetVertexShader = `
varying vec3 vPosition;
varying vec3 vNormal;
void main() {
  vPosition = position;
  vNormal = normalize(normalMatrix * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const planetFragmentShader = `
precision highp float;
varying vec3 vPosition;
varying vec3 vNormal;
uniform float uTime;
uniform vec3 uColorA;
uniform vec3 uColorB;

vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 permute(vec4 x){return mod289(((x*34.0)+1.0)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1.0/6.0,1.0/3.0);
  const vec4 D=vec4(0.0,0.5,1.0,2.0);
  vec3 i=floor(v+dot(v,C.yyy));
  vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz);
  vec3 l=1.0-g;
  vec3 i1=min(g.xyz,l.zxy);
  vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx;
  vec3 x2=x0-i2+C.yyy;
  vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(
    i.z+vec4(0.0,i1.z,i2.z,1.0))
    +i.y+vec4(0.0,i1.y,i2.y,1.0))
    +i.x+vec4(0.0,i1.x,i2.x,1.0));
  float n_=0.142857142857;
  vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.0*floor(p*ns.z*ns.z);
  vec4 x_=floor(j*ns.z);
  vec4 y_=floor(j-7.0*x_);
  vec4 x=x_*ns.x+ns.yyyy;
  vec4 y=y_*ns.x+ns.yyyy;
  vec4 h=1.0-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy);
  vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.0+1.0;
  vec4 s1=floor(b1)*2.0+1.0;
  vec4 sh=-step(h,vec4(0.0));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;
  vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x);
  vec3 p1=vec3(a0.zw,h.y);
  vec3 p2=vec3(a1.xy,h.z);
  vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
  vec4 m=max(0.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0);
  m=m*m;
  return 42.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
float fbm(vec3 p){
  float f=0.0; float a=0.5;
  for(int i=0;i<5;i++){ f+=a*snoise(p); p*=2.02; a*=0.5; }
  return f;
}
void main(){
  vec3 p=normalize(vPosition)*2.0;
  float bands=fbm(p*2.5+uTime*0.05);
  float storms=fbm(p*5.0-uTime*0.03);
  vec3 base=mix(uColorA,uColorB,smoothstep(-0.3,0.4,bands));
  base=mix(base,vec3(1.0,0.95,0.8),smoothstep(0.4,0.7,storms)*0.25);
  vec3 N=normalize(vNormal);
  vec3 L=normalize(vec3(1.0,0.8,1.0));
  float lambert=max(dot(N,L),0.0);
  float rim=pow(1.0-max(dot(N,vec3(0.0,0.0,1.0)),0.0),3.0);
  vec3 lit=base*(0.2+lambert*1.0);
  lit+=vec3(0.85,0.68,0.35)*rim*0.5;
  gl_FragColor=vec4(lit,1.0);
}
`;

export default function HoroscopeCosmos3D({ signe = 'Bélier' }) {
  const containerRef = useRef(null);
  const stateRef = useRef({ mouseX: 0, mouseY: 0, disposed: false });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const state = stateRef.current;
    state.disposed = false;

    let width = container.clientWidth;
    let height = container.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 6);

    const renderer = new THREE.WebGLRenderer({
      antialias: true, alpha: true, powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    // ── Planète centrale procédurale ──
    const planetMat = new THREE.ShaderMaterial({
      vertexShader: planetVertexShader,
      fragmentShader: planetFragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uColorA: { value: new THREE.Color(0x8B6FE6) }, // violet doux
        uColorB: { value: new THREE.Color(0xD4AF37) }, // or
      },
    });
    const planet = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 96), planetMat);
    scene.add(planet);

    // ── Planètes en orbite ──
    const orbits = [];
    const orbitConfigs = [
      { radius: 2.0, size: 0.14, speed: 0.5, color: 0xF4E8D2 },
      { radius: 2.7, size: 0.10, speed: 0.32, color: 0xD4AF37 },
      { radius: 3.3, size: 0.18, speed: 0.2, color: 0x8B6FE6 },
    ];
    orbitConfigs.forEach((cfg) => {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(cfg.size, 32, 32),
        new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.6, metalness: 0.1,
          emissive: new THREE.Color(cfg.color), emissiveIntensity: 0.25 })
      );
      // Anneau d'orbite discret
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(cfg.radius - 0.005, cfg.radius + 0.005, 128),
        new THREE.MeshBasicMaterial({ color: 0xD4AF37, transparent: true, opacity: 0.12,
          side: THREE.DoubleSide })
      );
      ring.rotation.x = Math.PI / 2.2;
      scene.add(ring);
      scene.add(m);
      orbits.push({ mesh: m, ...cfg, angle: Math.random() * Math.PI * 2 });
    });

    // ── Constellation du signe ──
    const points = ZODIAC_SHAPES[signe] || ZODIAC_SHAPES['Bélier'];
    const constGroup = new THREE.Group();
    const scale = 2.2;
    const verts = points.map(([x, y]) => new THREE.Vector3(x * scale, y * scale, 2.5));
    // Traits reliant les étoiles
    const lineGeom = new THREE.BufferGeometry().setFromPoints(verts);
    const line = new THREE.Line(lineGeom,
      new THREE.LineBasicMaterial({ color: 0xF4E8D2, transparent: true, opacity: 0.5 }));
    constGroup.add(line);
    // Étoiles aux sommets
    verts.forEach((v) => {
      const star = new THREE.Mesh(
        new THREE.SphereGeometry(0.05, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0xF4D98C })
      );
      star.position.copy(v);
      constGroup.add(star);
    });
    constGroup.position.set(0, 1.3, 0);
    constGroup.scale.set(0.9, 0.9, 0.9);
    scene.add(constGroup);

    // ── Lumières ──
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const key = new THREE.DirectionalLight(0xF4E8D2, 1.2);
    key.position.set(3, 2, 4);
    scene.add(key);

    // Parallaxe souris
    const handleMouse = (e) => {
      const rect = container.getBoundingClientRect();
      state.mouseX = ((e.clientX - rect.left) / rect.width) - 0.5;
      state.mouseY = ((e.clientY - rect.top) / rect.height) - 0.5;
    };
    container.addEventListener('mousemove', handleMouse);

    const handleResize = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    const clock = new THREE.Clock();
    const animate = () => {
      if (state.disposed) return;
      const t = clock.getElapsedTime();
      planetMat.uniforms.uTime.value = t;
      planet.rotation.y = t * 0.15;
      orbits.forEach((o) => {
        o.angle += o.speed * 0.01;
        o.mesh.position.set(Math.cos(o.angle) * o.radius,
          Math.sin(o.angle) * o.radius * 0.45, Math.sin(o.angle) * o.radius);
      });
      constGroup.rotation.z = Math.sin(t * 0.2) * 0.05;
      camera.position.x += (state.mouseX * 1.5 - camera.position.x) * 0.04;
      camera.position.y += (-state.mouseY * 1.0 - camera.position.y) * 0.04;
      camera.lookAt(scene.position);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();

    return () => {
      state.disposed = true;
      window.removeEventListener('resize', handleResize);
      container.removeEventListener('mousemove', handleMouse);
      renderer.dispose();
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
          else obj.material.dispose();
        }
      });
      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    };
  }, [signe]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }} />
  );
}
