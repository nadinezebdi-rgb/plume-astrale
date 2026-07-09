import { useEffect, useMemo } from 'react';
import { useAuth } from '@/context/AuthContext';

/**
 * Calcule le signe solaire depuis une date de naissance ISO YYYY-MM-DD.
 * Retourne 'aries' | 'taurus' | ... | 'pisces' | null
 */
export function getSunSign(birthDateIso) {
  if (!birthDateIso) return null;
  const parts = String(birthDateIso).slice(0, 10).split('-');
  if (parts.length < 3) return null;
  const m = parseInt(parts[1], 10);
  const d = parseInt(parts[2], 10);
  if (isNaN(m) || isNaN(d)) return null;

  const signs = [
    { name: 'capricorn', from: [12, 22], to: [1, 19] },
    { name: 'aquarius',  from: [1, 20],  to: [2, 18] },
    { name: 'pisces',    from: [2, 19],  to: [3, 20] },
    { name: 'aries',     from: [3, 21],  to: [4, 19] },
    { name: 'taurus',    from: [4, 20],  to: [5, 20] },
    { name: 'gemini',    from: [5, 21],  to: [6, 20] },
    { name: 'cancer',    from: [6, 21],  to: [7, 22] },
    { name: 'leo',       from: [7, 23],  to: [8, 22] },
    { name: 'virgo',     from: [8, 23],  to: [9, 22] },
    { name: 'libra',     from: [9, 23],  to: [10, 22] },
    { name: 'scorpio',   from: [10, 23], to: [11, 21] },
    { name: 'sagittarius',from:[11, 22], to: [12, 21] },
  ];
  for (const s of signs) {
    const [fm, fd] = s.from;
    const [tm, td] = s.to;
    if (fm === tm) {
      if (m === fm && d >= fd && d <= td) return s.name;
    } else {
      if ((m === fm && d >= fd) || (m === tm && d <= td)) return s.name;
    }
  }
  return null;
}

/**
 * Mappe un signe solaire vers son element : fire | water | air | earth
 */
export function getElement(sign) {
  const map = {
    aries: 'fire', leo: 'fire', sagittarius: 'fire',
    taurus: 'earth', virgo: 'earth', capricorn: 'earth',
    gemini: 'air', libra: 'air', aquarius: 'air',
    cancer: 'water', scorpio: 'water', pisces: 'water',
  };
  return map[sign] || null;
}

/**
 * Hook : calcule + applique automatiquement la classe .aura-{element} sur <body>
 * une fois que l'utilisateur est connecte (birth_date connu).
 * L'accent color d'accent bascule sur --plume-aura via les classes CSS aura-*.
 *
 * Utilisation : appeler `useAstralElement()` une seule fois dans App.js (deja fait via AuraProvider).
 */
export function useAstralElement() {
  const { user } = useAuth();
  const element = useMemo(() => {
    if (!user?.birth_date) return null;
    return getElement(getSunSign(user.birth_date));
  }, [user?.birth_date]);

  useEffect(() => {
    const body = document.body;
    ['aura-fire', 'aura-water', 'aura-air', 'aura-earth'].forEach(c => body.classList.remove(c));
    if (element) body.classList.add(`aura-${element}`);
    return () => {
      if (element) body.classList.remove(`aura-${element}`);
    };
  }, [element]);

  return element;
}
