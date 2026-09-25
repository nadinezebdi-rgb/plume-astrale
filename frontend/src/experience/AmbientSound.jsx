import React, { useCallback, useEffect, useRef, useState } from 'react';

export default function AmbientSound() {
  const audioRef = useRef(null);
  const timerRef = useRef(null);
  const stepRef = useRef(0);
  const [enabled, setEnabled] = useState(false);

  const playMelodyStep = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || !enabled) return;

    const { ctx, master } = audio;
    const notes = [261.63, 329.63, 392.0, 440.0, 523.25, 440.0, 392.0, 329.63, 293.66, 329.63, 392.0, 523.25];
    const note = notes[stepRef.current % notes.length];
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const shimmer = ctx.createOscillator();
    const shimmerGain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(note, ctx.currentTime);
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.14, ctx.currentTime + 0.15);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 1.2);

    shimmer.type = 'triangle';
    shimmer.frequency.setValueAtTime(note * 2, ctx.currentTime);
    shimmerGain.gain.setValueAtTime(0.0001, ctx.currentTime);
    shimmerGain.gain.exponentialRampToValueAtTime(0.04, ctx.currentTime + 0.12);
    shimmerGain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.9);

    osc.connect(gain);
    shimmer.connect(shimmerGain);
    gain.connect(master);
    shimmerGain.connect(master);

    osc.start(ctx.currentTime);
    shimmer.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 1.3);
    shimmer.stop(ctx.currentTime + 0.95);

    stepRef.current += 1;
  }, [enabled]);

  const start = useCallback(async () => {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;

    if (!audioRef.current) {
      const ctx = new AudioCtx();
      const master = ctx.createGain();
      master.gain.setValueAtTime(0.0001, ctx.currentTime);
      master.connect(ctx.destination);
      audioRef.current = { ctx, master };
    }

    const { ctx, master } = audioRef.current;
    if (ctx.state === 'suspended') await ctx.resume();

    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(0.0001, ctx.currentTime);
    master.gain.exponentialRampToValueAtTime(0.045, ctx.currentTime + 1.4);

    if (!timerRef.current) {
      playMelodyStep();
      timerRef.current = window.setInterval(playMelodyStep, 700);
    }

    setEnabled(true);
  }, [playMelodyStep]);

  useEffect(() => {
    const unlock = () => start();
    const events = ['pointerdown', 'touchstart', 'keydown', 'click'];
    events.forEach((eventName) => window.addEventListener(eventName, unlock, { passive: true }));
    return () => {
      events.forEach((eventName) => window.removeEventListener(eventName, unlock));
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [start]);

  const toggle = async () => {
    if (!audioRef.current) return start();
    const { ctx, master } = audioRef.current;
    if (enabled) {
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
      setEnabled(false);
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    } else {
      if (ctx.state === 'suspended') await ctx.resume();
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.exponentialRampToValueAtTime(0.045, ctx.currentTime + 0.8);
      playMelodyStep();
      timerRef.current = window.setInterval(playMelodyStep, 700);
      setEnabled(true);
    }
  };

  return (
    <button type="button" className="exp-sound-toggle" onClick={toggle} aria-label={enabled ? 'Couper l’ambiance sonore' : 'Activer l’ambiance sonore'}>
      {enabled ? '♪ Son activé' : '♪ Activer le son'}
    </button>
  );
}
