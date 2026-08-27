/**
 * useDeviceProfile — détection au montage :
 *   - prefers-reduced-motion
 *   - mobile (viewport width + touch)
 *   - low-end GPU (heuristique via hardwareConcurrency + memory)
 *   - WebGL disponible
 *
 * Le résultat est poussé dans le store une seule fois. Les scènes lisent
 * ces flags pour dégrader (moins de particules, pas de bloom, transitions
 * plus courtes) plutôt que de faire des if partout.
 */
import { useEffect } from 'react';
import { useExperienceStore } from '../useExperienceStore';

function detectWebGL() {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch {
    return false;
  }
}

export function useDeviceProfile() {
  const setDeviceProfile = useExperienceStore((s) => s.setDeviceProfile);

  useEffect(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isMobile = window.matchMedia('(max-width: 820px)').matches;
    const cores = navigator.hardwareConcurrency || 4;
    const mem = navigator.deviceMemory || 4;
    const isLowEnd = isMobile && (cores <= 4 || mem <= 3);
    const webglAvailable = detectWebGL();

    setDeviceProfile({
      reducedMotion,
      isMobile,
      isLowEnd,
      webglAvailable,
    });
  }, [setDeviceProfile]);
}
