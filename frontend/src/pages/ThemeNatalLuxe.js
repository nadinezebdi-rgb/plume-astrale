import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Ton Soleil', text: 'Ce qui t\'anime au plus profond — ta lumière, ta trajectoire de devenir.' },
  { title: 'Ta Lune', text: 'Tes émotions cachées, tes réflexes d\'enfance, ta façon de te consoler.' },
  { title: 'Ton Ascendant', text: 'Le masque que ton âme a choisi — ce que les autres perçoivent en premier.' },
  { title: 'Mercure · Vénus · Mars', text: 'Pensée, amour, action — les trois moteurs de ta vie quotidienne.' },
  { title: 'Jupiter · Saturne', text: 'Ta zone d\'expansion et ta discipline intérieure — les deux forces qui te structurent.' },
  { title: 'Uranus · Neptune · Pluton', text: 'Rupture, rêve, transformation — les trois planètes des grandes mutations d\'âme.' },
  { title: 'La danse des aspects', text: 'Ce que tes planètes se disent entre elles — la conversation secrète de ton chart.' },
  { title: 'Une lecture personnalisée', text: 'Chaque paragraphe est composé spécifiquement à partir de ton thème — jamais recopié d\'un signe.' },
];

const TESTIMONIALS = [];  // Concours 2026 : aucun témoignage codé en dur.

export default function ThemeNatalLuxe() {
  return (
    <SalesPageV3
      slug="natal"
      previewProduct="theme-natal"
      path="/theme-natal-luxe"
      seoTitle="Ton Thème Natal Luxe · 49 pages personnalisées · Plume Astrale"
      seoDescription="Un PDF premium de 49 pages où 11 planètes racontent qui tu es vraiment, à partir de 73 dimensions astrologiques. 29,99€ · paiement unique."
      eyebrow="Comprendre — Votre thème personnel"
      title='Comprendre qui vous êtes <span class="ps-italic">vraiment</span>.'
      subtitle="Une lecture de 49 pages, calculée à partir de votre date de naissance. Ce qui vous anime en profondeur, vos forces, vos zones sensibles, votre rythme intérieur."
      priceMain="29,99€"
      priceHint="paiement unique · livraison instantanée"
      pages={49}
      deliveryTime="5 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/planets/sun_1080.png`,
        alt: 'Le Soleil, planète centrale du thème natal',
        caption: 'Le Soleil natal',
      }}
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.natal}
      guarantee="Clarté ou remboursée — 14 jours, sans avoir à te justifier"
      ctaLabelAuth="Générer ma lecture"
      ctaLabelGuest="Recevoir mes 20 crédits · Commencer"
      ctaTargetAuth="/mon-compte?generate=natal"
      ctaTargetGuest="/inscription?next=/mon-compte"
    />
  );
}
