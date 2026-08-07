import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Ton chemin de vie', text: 'Le nombre principal calculé à partir de ta date de naissance — ta signature numérique de vie.' },
  { title: 'Ton année personnelle', text: 'La vibration numérique de l\'année en cours — ce que tu es appelée à vivre.' },
  { title: 'Nombre d\'expression', text: 'Ce que tu es venue exprimer dans le monde — calculé sur ton prénom complet.' },
  { title: 'Nombre d\'âme', text: 'Ce que ton âme désire secrètement — les voyelles de ton prénom.' },
  { title: 'Nombre de personnalité', text: 'Comment les autres te perçoivent — les consonnes de ton prénom.' },
  { title: 'Cycles de 9 ans', text: 'Ta cartographie sur 27 ans — les 3 grands cycles de vie que ta numérologie dessine.' },
  { title: 'Ton mantra numérique', text: 'Une phrase courte à répéter chaque matin — vibrationnellement alignée sur ton chemin.' },
];

const TESTIMONIALS = [
  { name: 'Julie · Paris', quote: 'J\'ai enfin compris pourquoi 2025 avait été si dense pour moi. Précision d\'orfèvre.' },
  { name: 'Aurélie · Nantes', quote: 'Le nombre d\'âme m\'a fait pleurer — c\'était exactement ce que je cachais.' },
];

export default function NumerologiePDF() {
  return (
    <SalesPageV3
      slug="numerologie"
      path="/numerologie-pdf"
      seoTitle="Numérologie sacrée · Chemin de vie décodé · Plume Astrale"
      seoDescription="Un PDF premium de 16 pages qui décode ton chemin de vie, ton année personnelle et tes 3 nombres d'expression. Signé Soléna."
      eyebrow="Bibliothèque Plume · Numérologie"
      title='Tes chiffres racontent <span class="ps-italic">ton âme.</span>'
      subtitle="Chemin de vie, année personnelle, nombres d'expression, d'âme et de personnalité — une lecture chiffrée qui complète l'astrologie avec précision."
      priceMain="29€"
      priceHint="paiement unique · PDF 16 pages"
      pages={16}
      deliveryTime="5 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/tarot/01_le_bateleur_512.png`,
        alt: 'Le Bateleur, arcane des nombres et de la magie',
        caption: 'Le Bateleur · Arcane I',
      }}
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.numerologie}
      guarantee="Clarté ou remboursée — 14 jours"
      ctaLabelAuth="Générer ma Numérologie"
      ctaLabelGuest="Recevoir ma Numérologie · 29€"
      ctaTargetAuth="/mon-compte?generate=numerologie"
      ctaTargetGuest="/paiement?product=numerologie"
    />
  );
}
