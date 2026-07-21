import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import SEO from '@/components/SEO';
import PdfBookOpen from '@/components/PdfBookOpen';

/**
 * NosLivres — Vitrine comparative des 5 livres luxes de Plume Astrale.
 *
 * L'utilisatrice sélectionne un livre via des onglets élégants et voit sa
 * couverture s'ouvrir en 3D. Chaque livre a son propre CTA.
 *
 * Positionnement : page "musée" — la marque affiche sa gamme avant de vendre.
 */

const BOOKS = [
  {
    key: 'natal',
    title: 'Thème Natal',
    accent: 'Ultra',
    price: '80 crédits · ~18€',
    priceHint: 'inclus dans le pack Nébuleuse 17,99€',
    pages: '49 pages',
    description: 'Onze planètes qui racontent qui tu es vraiment, écrites par Soléna à partir de 73 dimensions astrologiques croisées.',
    cta: 'Créer mon Thème Natal',
    ctaTo: '/theme-natal-luxe',
  },
  {
    key: 'synastry',
    title: 'Astrologie relationnelle',
    accent: 'Sur mesure',
    price: '49€',
    priceHint: 'paiement unique',
    pages: '25 pages',
    description: 'L\'aspectarium de votre lien — les deux ciels dansent ensemble. Points d\'harmonie, tensions à cultiver, langages d\'amour croisés.',
    cta: 'Analyser notre lien',
    ctaTo: '/synastrie',
  },
  {
    key: 'kabbale',
    title: 'Arbre de Vie',
    accent: 'Kabbalistique',
    price: '39€',
    priceHint: 'paiement unique',
    pages: '15 pages',
    description: 'Tes 10 Sephiroth et les 22 chemins hébraïques posés sur ta cartographie d\'âme. Où tu rayonnes, où tu ancres, où tu montes.',
    cta: 'Recevoir mon Arbre',
    ctaTo: '/kabbale',
  },
  {
    key: 'astrocarto',
    title: 'Astrocartographie',
    accent: 'Géographie astrale',
    price: '49€',
    priceHint: 'paiement unique',
    pages: '18 pages',
    description: 'Sept lignes planétaires posées sur la carte du monde. Où vivre ta meilleure vie, où l\'amour te touche, où ton corps se pose enfin.',
    cta: 'Découvrir mes lieux',
    ctaTo: '/astrocartographie',
  },
  {
    key: 'karmique',
    title: 'Pack Karmique',
    accent: 'L\'écrin ultime',
    price: '89€',
    priceHint: 'paiement unique · 3 livres réunis',
    pages: '40 pages',
    description: 'L\'écrin le plus profond de Plume Astrale — ton empreinte karmique, ton Arbre de Vie et ta synthèse d\'âme réunis dans un seul document relié.',
    cta: 'Ouvrir mon Karmique',
    ctaTo: '/pack-karmique',
  },
];

const NosLivres = () => {
  const [active, setActive] = useState('natal');
  const book = BOOKS.find((b) => b.key === active) || BOOKS[0];

  return (
    <div
      className="min-h-screen"
      style={{ padding: '110px 20px 140px' }}
      data-testid="nos-livres-page"
    >
      <SEO
        path="/nos-livres"
        title="Nos livres · La Bibliothèque Plume Astrale"
        description="Cinq livres reliés cuir nuit, écrits par Soléna. Thème Natal, Astrologie relationnelle, Arbre de Vie, Astrocartographie, Pack Karmique. À découvrir ci-dessous."
      />

      <div className="max-w-4xl mx-auto">
        {/* HERO */}
        <div className="text-center mb-14">
          <p
            className="text-[10px] uppercase mb-4"
            style={{ color: '#D4AF37', letterSpacing: '0.4em', fontFamily: 'Cinzel, serif' }}
          >
            ✦ La Bibliothèque Plume Astrale ✦
          </p>
          <h1
            style={{
              fontFamily: 'Cormorant Garamond, serif', fontWeight: 300,
              fontSize: 'clamp(38px, 5.5vw, 62px)', color: '#F5EEE0',
              lineHeight: 1.05, marginBottom: 20,
            }}
          >
            Cinq livres,
            <br />
            <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>une seule signature.</em>
          </h1>
          <p
            className="max-w-xl mx-auto text-base"
            style={{
              color: 'rgba(227,215,255,0.75)', fontFamily: 'Cormorant Garamond, serif',
              lineHeight: 1.6, fontStyle: 'italic',
            }}
          >
            Reliure cuir nuit, dorures Cinzel, chaque paragraphe écrit spécifiquement pour toi.
            <span style={{ color: '#F5EEE0' }}> Choisis ton livre — regarde-le s&apos;ouvrir.</span>
          </p>
        </div>

        {/* Onglets */}
        <div className="flex flex-wrap justify-center gap-2 mb-10" data-testid="nos-livres-tabs">
          {BOOKS.map((b) => {
            const isActive = active === b.key;
            return (
              <button
                key={b.key}
                onClick={() => setActive(b.key)}
                data-testid={`tab-${b.key}`}
                className="px-4 py-2 text-[11px] transition-all"
                style={{
                  background: isActive
                    ? 'linear-gradient(90deg, #8a6d1a 0%, #D4AF37 50%, #8a6d1a 100%)'
                    : 'rgba(26,18,48,0.4)',
                  color: isActive ? '#0E0A1E' : 'rgba(245,238,224,0.7)',
                  border: `1px solid ${isActive ? 'rgba(212,175,55,0.7)' : 'rgba(212,175,55,0.22)'}`,
                  borderRadius: 999,
                  fontFamily: 'Cinzel, serif',
                  letterSpacing: '0.22em',
                  textTransform: 'uppercase',
                  fontWeight: isActive ? 600 : 400,
                  cursor: 'pointer',
                }}
              >
                {b.title}
              </button>
            );
          })}
        </div>

        {/* Livre actif */}
        <div key={active} style={{ animation: 'fadeInUp 0.6s ease-out' }}>
          <PdfBookOpen testId={`nos-livres-book-${active}`} theme={active} />

          {/* Card de résumé */}
          <div
            className="mx-auto text-center p-6 md:p-8 mt-4"
            style={{
              maxWidth: 620,
              background: 'linear-gradient(160deg, rgba(26,18,48,0.85) 0%, rgba(14,10,30,0.92) 100%)',
              border: '1px solid rgba(212,175,55,0.4)',
              borderRadius: 12,
              boxShadow: '0 30px 60px -20px rgba(0,0,0,0.5)',
            }}
            data-testid={`nos-livres-details-${active}`}
          >
            <p
              className="mb-2 text-[10px]"
              style={{ color: '#D4AF37', letterSpacing: '0.3em', fontFamily: 'Cinzel, serif', textTransform: 'uppercase' }}
            >
              ✦ {book.accent} · {book.pages} ✦
            </p>
            <h3
              className="mb-3"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, fontSize: 30, color: '#F5EEE0' }}
            >
              {book.title}
            </h3>
            <p
              className="mb-6 max-w-md mx-auto text-sm"
              style={{
                fontFamily: 'Cormorant Garamond, serif',
                color: 'rgba(227,215,255,0.85)',
                fontStyle: 'italic', lineHeight: 1.55,
              }}
            >
              {book.description}
            </p>

            <div className="mb-6">
              <div style={{
                fontFamily: 'Cormorant Garamond, serif', fontWeight: 300,
                fontSize: 42, color: '#F5EEE0', lineHeight: 1,
              }}>
                {book.price}
              </div>
              <div className="text-[10px] mt-2" style={{
                color: 'rgba(212,175,55,0.7)', letterSpacing: '0.22em',
                fontFamily: 'Cinzel, serif', textTransform: 'uppercase',
              }}>
                {book.priceHint}
              </div>
            </div>

            <Link
              to={book.ctaTo}
              data-testid={`cta-${book.key}`}
              className="inline-flex items-center gap-3 py-3.5 px-8"
              style={{
                background: 'linear-gradient(90deg, #8a6d1a 0%, #D4AF37 50%, #8a6d1a 100%)',
                color: '#0E0A1E',
                borderRadius: 10,
                fontFamily: 'Cinzel, serif', fontSize: 12,
                letterSpacing: '0.28em', fontWeight: 600, textTransform: 'uppercase',
                textDecoration: 'none',
                boxShadow: '0 10px 30px -8px rgba(212,175,55,0.4)',
              }}
            >
              <Sparkles className="w-4 h-4" strokeWidth={1.5} />
              {book.cta}
              <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
            </Link>
          </div>
        </div>

        {/* Retour */}
        <div className="text-center mt-14">
          <Link
            to="/"
            className="text-xs"
            style={{
              color: 'rgba(212,175,55,0.55)', fontFamily: 'Cinzel, serif',
              letterSpacing: '0.24em', textTransform: 'uppercase',
            }}
          >
            ← Retour à l&apos;accueil
          </Link>
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0);   }
        }
      `}</style>
    </div>
  );
};

export default NosLivres;
