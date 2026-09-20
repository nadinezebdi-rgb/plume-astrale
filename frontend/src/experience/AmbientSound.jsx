import React, { useCallback, useEffect, useRef, useState } from 'react';

export default function AmbientSound() {
  const audioRef = useRef(null);
  const nodesRef = useRef([]);
  const [enabled, setEnabled] = useState(false);

  const start = useCallback(async () => {
    if (audioRef.current) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const master = ctx.createGain();
    master.gain.setValueAtTime(0.0001, ctx.currentTime);
    master.gain.exponentialRampToValueAtTime(0.035, ctx.currentTime + 2.5);
    master.connect(ctx.destination);

    [146.83, 220, 293.66].forEach((frequency, index) => {
      const oscillator = ctx.createOscillator();
      const gain = ctx.createGain();
      oscillator.type = index === 1 ? 'sine' : 'triangle';
      oscillator.frequency.value = frequency;
      oscillator.detune.value = index * 3 - 3;
      gain.gain.value = index === 1 ? 0.22 : 0.12;
      oscillator.connect(gain);
      gain.connect(master);
      oscillator.start();
      nodesRef.current.push(oscillator, gain);
    });
    audioRef.current = { ctx, master };
    setEnabled(true);
  }, []);

  useEffect(() => {
    const unlock = () => start();
    window.addEventListener('pointerdown', unlock, { once: true });
    return () => window.removeEventListener('pointerdown', unlock);
  }, [start]);

  const toggle = async () => {
    if (!audioRef.current) return start();
    const { ctx, master } = audioRef.current;
    if (enabled) {
      master.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
      setEnabled(false);
    } else {
      if (ctx.state === 'suspended') await ctx.resume();
      master.gain.exponentialRampToValueAtTime(0.035, ctx.currentTime + 0.8);
      setEnabled(true);
    }
  };

  return (
    <button type="button" className="exp-sound-toggle" onClick={toggle} aria-label={enabled ? 'Couper l’ambiance sonore' : 'Activer l’ambiance sonore'}>
      {enabled ? '♪ Son activé' : '♪ Activer le son'}
    </button>
  );
}
