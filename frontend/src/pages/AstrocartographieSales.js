import React from 'react';
import SalesPageV3 from '@/components/SalesPageV3';
import AstroCartoHero from '@/components/AstroCartoHero';
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

const TESTIMONIALS = [];  // Concours 2026 : aucun témoignage codé en dur.

export default function AstrocartographieSales() {
  return (
    <SalesPageV3
      slug="astrocarto"
      previewProduct="astrocartographie"
      path="/astrocartographie"
      seoTitle="Astrocartographie · Où vivre ta meilleure vie · Plume Astrale"
      seoDescription="Un PDF premium de 18 pages qui pose 7 lignes planétaires sur la carte du monde. 3 villes idéales + 3 bonus, avec conseils pratiques."
      eyebrow="Comprendre — Astrocartographie"
      title='Où votre vie peut prendre un <span class="ps-italic">nouveau souffle</span>.'
      subtitle="Certains lieux vous portent. D'autres vous freinent. Une lecture de 18 pages pour reconnaître les endroits qui vous correspondent vraiment."
      priceMain="49€"
      priceHint="paiement unique · PDF 18 pages"
      pages={18}
      deliveryTime="5 min"
      heroImage={{
        src: `${process.env.REACT_APP_BACKEND_URL}/api/assets/library/planets/jupiter_1080.png`,
        alt: 'Jupiter — planète de l\'expansion et des lieux d\'abondance',
        caption: 'Jupiter · planète de l\'expansion',
      }}
      heroNode={<AstroCartoHero />}
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
