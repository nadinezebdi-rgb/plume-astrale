import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Ton empreinte karmique', text: '22 pages sur tes Nœuds lunaires, ta Lune Noire et ton Chiron — l\'héritage d\'âme complet.' },
  { title: 'Ton Arbre de Vie · Kabbale', text: '15 pages sur tes 10 Sephiroth et les 22 chemins hébraïques qui les relient.' },
  { title: 'Synthèse d\'âme croisée', text: '3 pages inédites qui croisent ton karma et ton Arbre — la carte unique de qui tu es venue devenir.' },
  { title: 'Rituel de libération 21j', text: 'Un protocole personnalisé pour dissoudre ton pattern karmique le plus tenace.' },
  { title: 'Ton nom kabbalistique', text: 'Ton nom en hébreu, calculé à partir de ta naissance — la vibration secrète de ton âme.' },
  { title: '89€ au lieu de 68€', text: 'Une seule commande, un seul PDF de 40 pages — l\'écrin le plus profond de Plume Astrale.' },
];

const TESTIMONIALS = [
  { name: 'Delphine · Marseille', quote: 'Le format le plus complet que j\'ai reçu. Une bibliothèque à moi seule.' },
  { name: 'Anne · Strasbourg', quote: 'La synthèse d\'âme est extraordinaire. Rien à voir avec les lectures séparées.' },
  { name: 'Céline · Bordeaux', quote: 'Je l\'offre à ma sœur pour ses 40 ans. Le cadeau ultime.' },
];

export default function PackKarmique() {
  return (
    <SalesPageV3
      slug="karmique"
      path="/pack-karmique"
      seoTitle="Pack Karmique · 40 pages · L'écrin ultime · Plume Astrale"
      seoDescription="Le format le plus profond de Plume Astrale — ton empreinte karmique, ton Arbre de Vie et ta synthèse d'âme réunis dans un même PDF de 40 pages."
      eyebrow="Bibliothèque Plume · L'offre écrin"
      title='Pack Karmique — <span class="ps-italic">l&rsquo;écrin ultime.</span>'
      subtitle="Ton empreinte karmique, ton Arbre de Vie et ta synthèse d'âme réunis dans un même PDF premium de 40 pages. Le format le plus profond de Plume Astrale."
      priceMain="89€"
      priceHint="offre écrin · 3 lectures réunies · économie 39€"
      pages={40}
      deliveryTime="10 min"
      heroBadge="L'offre écrin"
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.karmique}
      guarantee="Clarté ou remboursée — 14 jours"
      ctaLabelAuth="Générer mon Pack Karmique"
      ctaLabelGuest="Recevoir mon Pack Karmique · 89€"
      ctaTargetAuth="/mon-compte?generate=pack-karmique"
      ctaTargetGuest="/paiement?product=pack-karmique"
    />
  );
}
