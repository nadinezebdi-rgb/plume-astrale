import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Keter · La Couronne', text: 'Le point le plus élevé de ton Arbre — l\'origine avant l\'origine, ta destination silencieuse.' },
  { title: 'Chokmah · Sagesse', text: 'La colonne masculine expansive — comment tu reçois la vision, l\'éclair, l\'idée.' },
  { title: 'Binah · Compréhension', text: 'La colonne féminine formative — comment tu structures, comment tu ancres l\'intuition.' },
  { title: 'Chesed · Miséricorde', text: 'La générosité qui déborde — où tu offres, où tu abondes.' },
  { title: 'Geburah · Rigueur', text: 'La juste limite — où tu dois dire non pour rester ton propre foyer.' },
  { title: 'Tiferet · Beauté', text: 'Le cœur de ton Arbre — ce qui, en toi, harmonise tous les Sephiroth.' },
  { title: 'Netzach · Éternité', text: 'La passion qui t\'anime — le désir qui te fait traverser les saisons.' },
  { title: 'Hod · Splendeur', text: 'Le mental clair — où tu formes le langage, où tu communiques ton âme.' },
  { title: 'Yesod · Fondation', text: 'Le seuil du rêve — l\'inconscient collectif qui te traverse chaque nuit.' },
  { title: 'Malkuth · Royaume', text: 'Ton incarnation — le corps, la matière, la présence dans le monde ici et maintenant.' },
  { title: 'Les 22 chemins hébraïques', text: 'Les lettres qui relient tes Sephiroth — la carte des voies entre tes forces intérieures.' },
  { title: 'Ton nom kabbalistique', text: 'Le nom en hébreu qui traduit ta signature d\'âme, calculé à partir de ta naissance.' },
];

const TESTIMONIALS = [
  { name: 'Sarah · Nice', quote: 'Je n\'avais jamais lu quelque chose d\'aussi juste sur moi. Une révélation.' },
  { name: 'Nadia · Paris', quote: 'La Kabbale m\'intimidait. Soléna m\'a offert une porte que je peux enfin franchir.' },
  { name: 'Élise · Montréal', quote: 'C\'est devenu ma boussole. Je le relis à chaque virage.' },
];

export default function KabbaleSales() {
  return (
    <SalesPageV3
      slug="kabbale"
      path="/kabbale"
      seoTitle="Arbre de Vie · Kabbale · 15 pages écrites par Soléna"
      seoDescription="Un PDF premium de 15 pages qui cartographie ton âme sur les 10 Sephiroth et les 22 chemins hébraïques. Personnalisé à partir de ton thème natal."
      eyebrow="Bibliothèque Plume · Kabbale"
      title='Ton Arbre de Vie, <span class="ps-italic">cartographié.</span>'
      subtitle="10 Sephiroth et 22 chemins hébraïques posés sur ta cartographie d'âme. Où tu rayonnes, où tu ancres, où tu montes."
      priceMain="39€"
      priceHint="paiement unique · PDF 15 pages"
      pages={15}
      deliveryTime="5 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/tarot/17_l_etoile_1080.png`,
        alt: "L'Étoile · guidance spirituelle",
        caption: 'L\'Étoile · Arcane XVII',
      }}
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.kabbale}
      guarantee="Clarté ou remboursée — 14 jours, sans avoir à te justifier"
      ctaLabelAuth="Générer mon Arbre de Vie"
      ctaLabelGuest="Recevoir mon Arbre de Vie · 39€"
      ctaTargetAuth="/mon-compte?generate=kabbale"
      ctaTargetGuest="/paiement?product=kabbale"
    />
  );
}
