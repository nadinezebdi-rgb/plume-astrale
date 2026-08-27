/**
 * Store de l'expérience /experience
 * ------------------------------------------------------------------
 * État minimal partagé entre l'orchestrateur GSAP, les scènes 3D
 * et l'overlay UI. Aucune persistance — l'expérience se reset à chaque
 * arrivée sur la route.
 */
import { create } from 'zustand';

export const useExperienceStore = create((set) => ({
  // Progression
  currentScene: 1, // 1..4
  sceneProgress: 0, // 0..1 dans la scène courante
  globalProgress: 0, // 0..1 sur toute l'expérience

  // Interaction utilisateur (sera consommé par la vraie feature plus tard)
  intent: null, // 'relationship' | 'clarity' | 'selfDiscovery' | 'question'
  hoveredIntent: null, // hover en direct pour illuminer la constellation
  drawnCard: null, // clé de la carte symbolique

  // Contraintes environnement
  reducedMotion: false,
  isMobile: false,
  isLowEnd: false,
  webglAvailable: true,

  // UX
  soundEnabled: false,

  // Actions
  setScene: (s) => set({ currentScene: s }),
  setSceneProgress: (p) => set({ sceneProgress: p }),
  setGlobalProgress: (p) => set({ globalProgress: p }),
  setIntent: (i) => set({ intent: i }),
  setHoveredIntent: (i) => set({ hoveredIntent: i }),
  setDrawnCard: (c) => set({ drawnCard: c }),
  setDeviceProfile: (profile) => set(profile),
  toggleSound: () => set((s) => ({ soundEnabled: !s.soundEnabled })),
}));
