import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Vos deux Soleils croisés', text: 'Ce que vos élans essentiels se disent — attraction fondamentale ou danse à ajuster.' },
  { title: 'Vos deux Lunes', text: 'Comment vos émotions s\'accordent — la clé de la tendresse quotidienne.' },
  { title: 'Vénus × Mars', text: 'La chimie amoureuse — le désir, la séduction, l\'appétit l\'un de l\'autre.' },
  { title: 'Aspects majeurs croisés', text: 'Trigones, carrés, oppositions — les tensions créatives et les harmonies naturelles.' },
  { title: 'Karma relationnel', text: 'Vos Nœuds lunaires croisés — ce que vous êtes venus vous apprendre l\'un à l\'autre.' },
  { title: 'Composite (5e planète)', text: 'La signature d\'âme de votre couple en tant qu\'entité à part entière.' },
  { title: 'Rituel du couple', text: 'Un rituel court à faire ensemble tous les samedis — pour cultiver l\'harmonie.' },
];

const TESTIMONIALS = [];  // Concours 2026 : aucun témoignage codé en dur.

export default function SynastrieSales() {
  return (
    <SalesPageV3
      slug="synastry"
      previewProduct="synastrie"
      path="/synastrie"
      seoTitle="Astrologie relationnelle · Vos deux ciels croisés · Plume Astrale"
      seoDescription="Un PDF premium de 25 pages qui croise vos deux thèmes natals. Attraction, tensions créatives, karma relationnel, rituel du couple."
      eyebrow="Comprendre — Votre lien"
      title='Comprendre la dynamique qui <span class="ps-italic">vous lie</span>.'
      subtitle="Une lecture de 25 pages qui décrypte votre relation — ce qui vous rapproche, ce qui vous éprouve, ce que vous êtes venus apprendre l'un de l'autre."
      priceMain="49€"
      priceHint="paiement unique · PDF 25 pages · pour un couple"
      pages={25}
      deliveryTime="10 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/tarot/06_les_amoureux_1080.png`,
        alt: 'Les Amoureux · arcane du lien',
        caption: 'Les Amoureux · Arcane VI',
      }}
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.synastry}
      guarantee="Clarté ou remboursée — 14 jours"
      ctaLabelAuth="Générer notre Synastrie"
      ctaLabelGuest="Analyser notre lien · 49€"
      ctaTargetAuth="/mon-compte?generate=synastry"
      ctaTargetGuest="/paiement?product=synastrie"
    />
  );
}
