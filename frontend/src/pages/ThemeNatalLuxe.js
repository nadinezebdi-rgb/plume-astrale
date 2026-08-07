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
  { title: 'Signature Soléna', text: 'Chaque paragraphe écrit spécifiquement pour toi, jamais recopié d\'un signe.' },
];

const TESTIMONIALS = [
  { name: 'Camille · Lyon', quote: 'J\'ai lu trois fois d\'affilée. C\'était comme si Soléna me connaissait depuis toujours.' },
  { name: 'Elsa · Bruxelles', quote: 'Chaque page m\'a apaisée. Un cadeau que je m\'offre chaque année désormais.' },
  { name: 'Léa · Toulouse', quote: 'Un texte d\'une justesse rare. J\'ai retrouvé du sens à ce que je vivais.' },
];

export default function ThemeNatalLuxe() {
  return (
    <SalesPageV3
      slug="natal"
      previewProduct="theme-natal"
      path="/theme-natal-luxe"
      seoTitle="Ton Thème Natal Luxe · 49 pages écrites par Soléna · Plume Astrale"
      seoDescription="Un PDF premium de 49 pages où 11 planètes racontent qui tu es vraiment. Écrit par Soléna à partir de 73 dimensions astrologiques. Offre bienvenue : 17,99€."
      eyebrow="Bibliothèque Plume · Thème Natal"
      title='Ton Thème Natal, <span class="ps-italic">écrit pour toi.</span>'
      subtitle="Onze planètes racontent qui tu es vraiment. Un PDF premium de 49 pages, à partir de 73 dimensions astrologiques croisées, signé Soléna."
      priceMain="17,99€"
      priceStrike="29€"
      priceHint="offre bienvenue · paiement unique"
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
