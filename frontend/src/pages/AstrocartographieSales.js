import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import { APERCUS } from '@/config/apercus';

const INCLUDES = [
  { title: 'Ligne Soleil', text: 'Là où ton essence rayonne au maximum — les villes où tu deviens visible, magnétique, entrepreneuse.' },
  { title: 'Ligne Lune', text: 'Là où ta sensibilité se dépose enfin — les villes du repos, du foyer, de l\'enfance retrouvée.' },
  { title: 'Ligne Vénus', text: 'Là où l\'amour, la beauté et la douceur t\'accueillent — les villes qui rendent belle sans effort.' },
  { title: 'Ligne Mars', text: 'Là où tu retrouves ton feu — les villes qui te rendent combative, sportive, ambitieuse.' },
  { title: 'Ligne Jupiter', text: 'Là où la chance et l\'expansion t\'attendent — les villes de l\'abondance et des rencontres.' },
  { title: 'Ligne Saturne', text: 'Là où tu construis quelque chose de durable — les villes de la maturation, du travail long.' },
  { title: 'Ligne Neptune', text: 'Là où le rêve, l\'art et la spiritualité s\'ouvrent — les villes du dessin, de la musique, du soin.' },
  { title: '3 villes idéales pour toi', text: 'Sélectionnées et racontées en détail — climat, cuisine, énergie, conseils pratiques.' },
  { title: '3 villes bonus surprise', text: 'Des lieux inattendus qui pourraient bien te correspondre — Soléna te dit pourquoi.' },
  { title: 'Ta carte du monde personnelle', text: 'Un visuel astral que tu peux imprimer — tes 7 lignes planétaires en un coup d\'œil.' },
];

const TESTIMONIALS = [
  { name: 'Amélie · Bordeaux', quote: 'J\'hésitais entre 4 pays. Sa carte m\'a débloquée en une lecture.' },
  { name: 'Sophie · Genève', quote: 'Lisbonne était sur ma ligne Vénus-AC. J\'y suis allée. Elle avait raison.' },
  { name: 'Marion · Rennes', quote: 'La précision géographique est bluffante. Un document qui vaut son pesant d\'or.' },
];

export default function AstrocartographieSales() {
  return (
    <SalesPageV3
      slug="astrocarto"
      path="/astrocartographie"
      seoTitle="Astrocartographie · Où vivre ta meilleure vie · Plume Astrale"
      seoDescription="Un PDF premium de 18 pages qui pose 7 lignes planétaires sur la carte du monde. 3 villes idéales + 3 bonus, avec conseils pratiques. Signé Soléna."
      eyebrow="Bibliothèque Plume · Astrocartographie"
      title='Où vivre <span class="ps-italic">ta meilleure vie ?</span>'
      subtitle="Sept lignes planétaires posées sur la carte du monde. Où l'amour te touche, où ton corps se pose enfin, où tu deviens visible — Soléna te trace la carte."
      priceMain="49€"
      priceHint="paiement unique · PDF 18 pages"
      pages={18}
      deliveryTime="5 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/planets/uranus_1080.png`,
        alt: 'Uranus, planète du mouvement et de la géographie',
        caption: 'Uranus · Mouvement',
      }}
      includes={INCLUDES}
      testimonials={TESTIMONIALS}
      apercu={APERCUS.astrocarto}
      guarantee="Clarté ou remboursée — 14 jours, sans avoir à te justifier"
      ctaLabelAuth="Générer mon Astrocartographie"
      ctaLabelGuest="Découvrir mes lieux · 49€"
      ctaTargetAuth="/mon-compte?generate=astrocarto"
      ctaTargetGuest="/paiement?product=astrocarto"
    />
  );
}
