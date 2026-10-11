import React, { useEffect, useRef, useState } from 'react';

// "1990-05-15" -> "15/05/1990"
const isoToFr = (iso) => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  return m ? `${m[3]}/${m[2]}/${m[1]}` : '';
};

// "15/05/1990" -> "1990-05-15" (chaîne vide si la date n'existe pas)
const frToIso = (fr) => {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(fr);
  if (!m) return '';
  const [, d, mo, y] = m;
  const date = new Date(Number(y), Number(mo) - 1, Number(d));
  const valid = date.getFullYear() === Number(y) && date.getMonth() === Number(mo) - 1 && date.getDate() === Number(d);
  return valid ? `${y}-${mo}-${d}` : '';
};

// Masque JJ/MM/AAAA pendant la saisie
const maskFr = (raw) => {
  const digits = raw.replace(/\D/g, '').slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
};

/**
 * Champ date au format français JJ/MM/AAAA, quelle que soit la langue du navigateur.
 * Remplace <input type="date"> : `value` et `onChange` restent au format ISO (AAAA-MM-JJ),
 * onChange reçoit un objet { target: { name, value } } compatible avec les handlers existants.
 */
export default function FrenchDateInput({
  value, onChange, min, max, required, name, type: _ignoredType, onBlur, ...rest
}) {
  const [text, setText] = useState(isoToFr(value));
  const ref = useRef(null);

  // Resynchronise si la valeur change depuis l'extérieur (chargement du profil, reset du formulaire)
  useEffect(() => {
    if (value !== frToIso(text)) setText(isoToFr(value));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const outOfRange = (iso) => (min && iso < min) || (max && iso > max);

  // Message natif de validation : bloque l'envoi d'un formulaire avec une date incomplète ou impossible
  useEffect(() => {
    if (!ref.current) return;
    const iso = frToIso(text);
    let msg = '';
    if (text && !iso) msg = 'Date invalide : utilisez le format JJ/MM/AAAA.';
    else if (iso && outOfRange(iso)) msg = 'Cette date n\u2019est pas autorisée.';
    ref.current.setCustomValidity(msg);
  }, [text, min, max]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChange = (e) => {
    const masked = maskFr(e.target.value);
    setText(masked);
    const iso = frToIso(masked);
    const next = iso && !outOfRange(iso) ? iso : '';
    if (next !== (value || '')) onChange?.({ target: { name, value: next } });
  };

  return (
    <input
      {...rest}
      ref={ref}
      type="text"
      name={name}
      inputMode="numeric"
      autoComplete={rest.autoComplete || 'off'}
      placeholder={rest.placeholder || 'JJ/MM/AAAA'}
      maxLength={10}
      required={required}
      value={text}
      onChange={handleChange}
      onBlur={onBlur}
    />
  );
}
