import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Nœud Sud', text: 'Ce que ton âme porte déjà — la mémoire karmique, les acquis des vies antérieures.' },
  { title: 'Nœud Nord', text: 'Ta destination — ce que ton âme est venue accomplir dans cette incarnation-ci.' },
  { title: 'Lune Noire · Lilith', text: 'Ta zone d\'ombre créative — ce qui te rend puissante quand tu l\'assumes.' },
  { title: 'Chiron', text: 'Ta blessure sacrée — et le don qui en découle une fois traversée.' },
  { title: 'Aspects karmiques', text: 'Les configurations qui pointent des dettes ou des cadeaux d\'âme précis.' },
  { title: 'Rituel de libération', text: 'Un rituel personnalisé de 21 jours pour dissoudre un pattern karmique répétitif.' },
];

const TESTIMONIALS = [
  { name: 'Isabelle · Toulouse', quote: 'C\'est venu clarifier pourquoi je répétais la même histoire depuis 20 ans. Bouleversant.' },
  { name: 'Sonia · Aix', quote: 'Le chapitre sur mon Chiron m\'a fait pleurer — puis tout est devenu limpide.' },
];

export default function KarmaDestinPDF() {
  return (
    <SalesPageV3
      slug="karma"
      path="/karma-destin-pdf"
      seoTitle="Karma & Destin · Ta lignée karmique décodée · Plume Astrale"
      seoDescription="Un PDF premium de 22 pages qui décode ta mémoire karmique, tes Nœuds lunaires, ta Lune Noire et Chiron. Signé Soléna."
      eyebrow="Bibliothèque Plume · Karma"
      title='Ta lignée karmique, <span class="ps-italic">décodée.</span>'
      subtitle="Ce que tu portes de tes vies antérieures, ce que tu viens réparer, ce que tu viens accomplir cette fois-ci."
      priceMain="29€"
      priceHint="paiement unique · PDF 22 pages"
      pages={22}
      deliveryTime="5 min"
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.karma}
      guarantee="Clarté ou remboursée — 14 jours"
      ctaLabelAuth="Générer mon Karma & Destin"
      ctaLabelGuest="Recevoir mon Karma & Destin · 29€"
      ctaTargetAuth="/mon-compte?generate=karma"
      ctaTargetGuest="/paiement?product=karma"
    />
  );
}
