import { useCallback, useRef } from 'react';

/**
 * useCardFlipSound — génère un son de carte manipulée via Web Audio API.
 *
 * Aucun asset externe : c'est un burst de bruit filtré + envelope courte
 * qui imite un léger "whoosh" de carte glissant sur du tissu.
 *
 * Utilisation :
 *   const playFlip = useCardFlipSound();
 *   ...
 *   <button onClick={() => { doFlip(); playFlip(); }} />
 *
 * Silencieux si la browser n'a pas d'interaction utilisateur préalable
 * (politique autoplay). Ne casse jamais l'UX en cas d'erreur.
 */
export default function useCardFlipSound(volume = 0.35) {
  const ctxRef = useRef(null);

  const play = useCallback(() => {
    try {
      // Réutilise le même AudioContext (idempotent)
      if (!ctxRef.current) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        ctxRef.current = new AC();
      }
      const ctx = ctxRef.current;
      if (ctx.state === 'suspended') { ctx.resume(); }

      const now = ctx.currentTime;
      const duration = 0.35;

      // 1. Générateur de bruit blanc (burst court)
      const bufferSize = ctx.sampleRate * duration;
      const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        // Bruit blanc décroissant (tapered pour émuler le contact carte→carte)
        const progress = i / bufferSize;
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - progress, 2);
      }
      const noise = ctx.createBufferSource();
      noise.buffer = noiseBuffer;

      // 2. Filtre passe-bande centré à 3.5 kHz (bruit sec de papier)
      const bandpass = ctx.createBiquadFilter();
      bandpass.type = 'bandpass';
      bandpass.frequency.setValueAtTime(3500, now);
      bandpass.frequency.exponentialRampToValueAtTime(1800, now + duration);
      bandpass.Q.value = 1.5;

      // 3. Envelope (attack rapide, release doux)
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(volume, now + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

      // 4. Chaîne : noise → bandpass → gain → speakers
      noise.connect(bandpass);
      bandpass.connect(gain);
      gain.connect(ctx.destination);
      noise.start(now);
      noise.stop(now + duration);

      // 5. Petit clic sec au tout début (whip-crack) pour ajouter de la texture
      const click = ctx.createOscillator();
      click.type = 'square';
      click.frequency.setValueAtTime(120, now);
      click.frequency.exponentialRampToValueAtTime(30, now + 0.06);
      const clickGain = ctx.createGain();
      clickGain.gain.setValueAtTime(0, now);
      clickGain.gain.linearRampToValueAtTime(volume * 0.4, now + 0.008);
      clickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
      click.connect(clickGain);
      clickGain.connect(ctx.destination);
      click.start(now);
      click.stop(now + 0.1);
    } catch (_e) {
      // Silent fail — l'audio ne doit jamais casser l'UX
    }
  }, [volume]);

  return play;
}
