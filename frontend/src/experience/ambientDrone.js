/**
 * ambientDrone.js — génération procédurale de nappes sonores via Web Audio API.
 *
 * Zéro fichier audio téléchargé. Tout est synthétisé dans le navigateur :
 *   • oscillateurs (sine + triangle)
 *   • filtre passe-bas
 *   • LFO subtils sur gain (respiration)
 *   • gentle reverb via convolution d'un IR généré au vol
 *
 * Trois presets exposés :
 *   - `vestibule`     : grave enveloppant, quinte + shimmer haut, cathédrale
 *   - `voile`         : accord mineur suspendu, souffle doux, brume
 *   - `constellation` : bourdon rare + notes de clochette lointaines
 *
 * API :
 *   const drone = createAmbientDrone('vestibule');
 *   drone.start();  // demande obligatoirement un geste utilisateur (autoplay policy)
 *   drone.setVolume(0.6);
 *   drone.stop();
 */

function makeReverbIR(ctx, seconds = 3, decay = 2.4) {
  const rate = ctx.sampleRate;
  const length = Math.floor(rate * seconds);
  const impulse = ctx.createBuffer(2, length, rate);
  for (let ch = 0; ch < 2; ch += 1) {
    const buf = impulse.getChannelData(ch);
    for (let i = 0; i < length; i += 1) {
      buf[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
    }
  }
  return impulse;
}

function osc(ctx, type, freq, gain, dest) {
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = type;
  o.frequency.value = freq;
  g.gain.value = 0;
  o.connect(g); g.connect(dest);
  o.start();
  // fade-in doux 3s pour éviter tout click
  g.gain.linearRampToValueAtTime(gain, ctx.currentTime + 3);
  return { o, g };
}

function slowLFO(ctx, target, min, max, periodSec) {
  const lfo = ctx.createOscillator();
  const lfoGain = ctx.createGain();
  lfo.type = 'sine';
  lfo.frequency.value = 1 / periodSec;
  lfoGain.gain.value = (max - min) / 2;
  lfo.connect(lfoGain); lfoGain.connect(target);
  target.value = (min + max) / 2;
  lfo.start();
  return lfo;
}

export function createAmbientDrone(preset = 'vestibule') {
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtx) return null;

  const ctx = new AudioCtx();
  const master = ctx.createGain();
  master.gain.value = 0.7;

  // Filtre master : lp doux pour arrondir
  const lp = ctx.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 900;
  lp.Q.value = 0.5;

  // Reverb
  const convolver = ctx.createConvolver();
  convolver.buffer = makeReverbIR(ctx, 3.6, 2.6);
  const wet = ctx.createGain(); wet.gain.value = 0.28;
  const dry = ctx.createGain(); dry.gain.value = 0.85;

  // graph : sources → lp → (dry + wet(convolver)) → master → destination
  lp.connect(dry); dry.connect(master);
  lp.connect(convolver); convolver.connect(wet); wet.connect(master);
  master.connect(ctx.destination);

  const nodes = [];

  const addOsc = (type, freq, gain) => nodes.push(osc(ctx, type, freq, gain, lp));

  if (preset === 'vestibule') {
    // Deep low drone + fifth + high shimmer
    addOsc('sine', 55, 0.35);        // A1
    addOsc('sine', 82.5, 0.22);      // E2 (5th)
    addOsc('triangle', 220, 0.08);   // A3 sparkle
    slowLFO(ctx, lp.frequency, 500, 1400, 22);
    slowLFO(ctx, master.gain, 0.55, 0.75, 14);
  } else if (preset === 'voile') {
    // Accord mineur suspendu : A2 / C3 / E3 (Am) + subtle top
    addOsc('sine', 110, 0.28);       // A2
    addOsc('sine', 130.81, 0.22);    // C3
    addOsc('sine', 164.81, 0.20);    // E3
    addOsc('triangle', 440, 0.05);   // A4 top voile
    lp.frequency.value = 720;
    slowLFO(ctx, lp.frequency, 500, 1000, 28);
    slowLFO(ctx, master.gain, 0.5, 0.72, 18);
  } else if (preset === 'constellation') {
    // Single deep bourdon + rare bell-like top
    addOsc('sine', 73.42, 0.34);       // D2
    addOsc('triangle', 587.33, 0.06);  // D5 bell far
    addOsc('triangle', 880, 0.04);     // A5 shimmer
    lp.frequency.value = 1100;
    slowLFO(ctx, lp.frequency, 700, 1400, 36);
    // Volume qui respire large
    slowLFO(ctx, master.gain, 0.45, 0.75, 22);
  }

  let started = false;
  return {
    ctx,
    start: async () => {
      if (started) return;
      started = true;
      try { await ctx.resume(); } catch { /* noop */ }
    },
    stop: () => {
      if (!started) return;
      started = false;
      // Fade-out puis close pour éviter click
      const t = ctx.currentTime;
      master.gain.cancelScheduledValues(t);
      master.gain.setValueAtTime(master.gain.value, t);
      master.gain.linearRampToValueAtTime(0.0001, t + 1.4);
      setTimeout(() => { try { ctx.close(); } catch { /* noop */ } }, 1600);
    },
    setVolume: (v) => {
      const t = ctx.currentTime;
      master.gain.cancelScheduledValues(t);
      master.gain.linearRampToValueAtTime(Math.max(0, Math.min(1, v)), t + 0.5);
    },
    isStarted: () => started,
    _nodes: nodes,
  };
}

export const AMBIENT_PRESETS = [
  {
    key: 'vestibule',
    name: 'Vestibule',
    subtitle: 'Cathédrale à 4 h du matin — grave + quinte + shimmer',
    description: 'Nappe basse enveloppante avec une quinte discrète et un scintillement lointain. Reverb longue.',
  },
  {
    key: 'voile',
    name: 'Le Voile',
    subtitle: 'Accord mineur suspendu — La-Do-Mi + brume',
    description: 'Un accord mineur qui flotte, avec un souffle très haut. Plus doux et méditatif.',
  },
  {
    key: 'constellation',
    name: 'Constellation',
    subtitle: 'Bourdon rare + clochettes lointaines',
    description: 'Un bourdon très bas, ponctué par des harmoniques cristallines qui évoquent des étoiles.',
  },
];
