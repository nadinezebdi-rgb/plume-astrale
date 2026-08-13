import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';

/**
 * Découvrir — Onboarding situation-first (Phase 2 du repositionnement).
 *
 * L'utilisateur ne choisit plus un outil (tarot, thème natal, etc.)
 * mais une situation de vie. Le mapping vers un produit se fait ensuite.
 *
 * 6 situations x 2 précisions = 12 recommandations personnalisées.
 */
const SITUATIONS = [
  {
    key: 'doute',
    label: 'Une période de doute',
    hint: 'Vous cherchez du sens, du recul, un point d\'ancrage.',
    recommendation: 'theme-natal',
  },
  {
    key: 'relation',
    label: 'Une relation compliquée',
    hint: 'Un lien important vous questionne, vous fait douter, vous fatigue.',
    recommendation: 'synastrie',
  },
  {
    key: 'changement',
    label: 'Un changement professionnel',
    hint: 'Un projet, une transition, un nouveau chapitre à ouvrir.',
    recommendation: 'astrocartographie',
  },
  {
    key: 'comprendre',
    label: 'Un besoin de mieux vous comprendre',
    hint: 'Découvrir vos schémas profonds, ce qui vous anime réellement.',
    recommendation: 'theme-natal-luxe',
  },
  {
    key: 'decision',
    label: 'Une décision importante',
    hint: 'Vous hésitez, vous voulez peser toutes les dimensions.',
    recommendation: 'karma-destin',
  },
  {
    key: 'evolution',
    label: 'Une envie d\'évoluer',
    hint: 'Passer à autre chose, grandir, prendre une nouvelle direction.',
    recommendation: 'kabbale',
  },
];

const PRODUCT_INFO = {
  'theme-natal': {
    title: 'Votre thème personnel',
    subtitle: 'Un livre imprimé de 49 pages pour comprendre qui vous êtes vraiment.',
    to: '/theme-natal',
    price: '17,99€',
  },
  'theme-natal-luxe': {
    title: 'Votre lecture personnelle · édition Luxe',
    subtitle: '86 pages personnalisées, chapitres d\'âme, rituels et repères profonds.',
    to: '/theme-natal-luxe',
    price: '49€',
  },
  'synastrie': {
    title: 'Comprendre votre lien',
    subtitle: '25 pages qui décodent la dynamique entre vous deux.',
    to: '/synastrie',
    price: '49€',
  },
  'astrocartographie': {
    title: 'Choisir où votre vie peut respirer',
    subtitle: 'Les lieux qui vous portent, ceux à éviter. 38 pages personnalisées.',
    to: '/astrocartographie',
    price: '49€',
  },
  'karma-destin': {
    title: 'Comprendre les schémas qui reviennent',
    subtitle: 'Votre lignée intérieure, ce qui se répète, ce qui se libère.',
    to: '/karma-destin',
    price: '29€',
  },
  'kabbale': {
    title: 'L\'architecture invisible de votre chemin',
    subtitle: 'Votre Arbre de Vie en 42 pages — les grandes lignes de votre évolution.',
    to: '/kabbale',
    price: '39€',
  },
};

export default function Decouvrir() {
  const [params] = useSearchParams();
  const initialTheme = params.get('theme') || null;
  const [step, setStep] = useState(1);
  const [selected, setSelected] = useState(null);
  const [showSolena, setShowSolena] = useState(false);

  // Pré-sélection via ?theme=... venant des piliers homepage
  useEffect(() => {
    if (initialTheme) {
      const map = {
        cycles: 'doute',
        relations: 'relation',
        decisions: 'decision',
        evolution: 'evolution',
      };
      if (map[initialTheme]) setSelected(map[initialTheme]);
    }
  }, [initialTheme]);

  const handleSubmit = () => {
    if (!selected) return;
    setStep(2);
    setTimeout(() => setShowSolena(true), 800);
  };

  const situation = SITUATIONS.find((s) => s.key === selected);
  const product = situation ? PRODUCT_INFO[situation.recommendation] : null;

  return (
    <div
      data-testid="page-decouvrir"
      style={{
        minHeight: '100vh',
        background: 'radial-gradient(ellipse at 50% 0%, #1E2A5E 0%, #0F1A3C 40%, #0A1128 100%)',
        color: '#F7F5F0',
        padding: '96px 24px',
      }}
    >
      <SEO
        path="/decouvrir"
        title="Découvrir mon parcours · Plume Astrale"
        description="Répondez à une question simple. Recevez une lecture personnalisée pour comprendre ce que vous traversez."
      />

      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        {/* ─── ÉTAPE 1 : question ─── */}
        {step === 1 && (
          <div data-testid="decouvrir-step1">
            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
                letterSpacing: '0.4em',
                textTransform: 'uppercase',
                color: 'rgba(184, 147, 90, 0.85)',
                marginBottom: 32,
                textAlign: 'center',
              }}
            >
              Un instant pour vous
            </p>

            <h1
              style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 'clamp(2rem, 4vw, 3rem)',
                fontWeight: 400,
                lineHeight: 1.2,
                textAlign: 'center',
                marginBottom: 24,
                color: '#F7F5F0',
              }}
            >
              Que traversez-vous <em style={{ color: '#B8935A' }}>aujourd&apos;hui</em>&nbsp;?
            </h1>

            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 15,
                lineHeight: 1.6,
                textAlign: 'center',
                color: 'rgba(247, 245, 240, 0.7)',
                marginBottom: 64,
              }}
            >
              Choisissez ce qui résonne le plus avec vous. La lecture qui vous correspond
              se dessinera à partir de ce que vous partagez.
            </p>

            <div style={{ display: 'grid', gap: 14 }}>
              {SITUATIONS.map((s) => {
                const isSelected = selected === s.key;
                return (
                  <button
                    key={s.key}
                    type="button"
                    onClick={() => setSelected(s.key)}
                    data-testid={`situation-${s.key}`}
                    style={{
                      textAlign: 'left',
                      padding: '20px 24px',
                      borderRadius: 14,
                      background: isSelected
                        ? 'linear-gradient(135deg, rgba(184, 147, 90, 0.18) 0%, rgba(184, 147, 90, 0.08) 100%)'
                        : 'rgba(30, 42, 94, 0.35)',
                      border: `1px solid ${isSelected ? '#B8935A' : 'rgba(184, 147, 90, 0.15)'}`,
                      color: '#F7F5F0',
                      cursor: 'pointer',
                      transition: 'all 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.borderColor = 'rgba(184, 147, 90, 0.5)';
                        e.currentTarget.style.background = 'rgba(30, 42, 94, 0.5)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.borderColor = 'rgba(184, 147, 90, 0.15)';
                        e.currentTarget.style.background = 'rgba(30, 42, 94, 0.35)';
                      }
                    }}
                  >
                    <div
                      style={{
                        fontFamily: 'Playfair Display, serif',
                        fontSize: 19,
                        color: isSelected ? '#F7F5F0' : 'rgba(247, 245, 240, 0.92)',
                        marginBottom: 4,
                      }}
                    >
                      {s.label}
                    </div>
                    <div
                      style={{
                        fontFamily: 'Inter, sans-serif',
                        fontSize: 13,
                        color: 'rgba(247, 245, 240, 0.55)',
                        lineHeight: 1.5,
                      }}
                    >
                      {s.hint}
                    </div>
                  </button>
                );
              })}
            </div>

            <div style={{ textAlign: 'center', marginTop: 56 }}>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!selected}
                data-testid="decouvrir-continue-btn"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '18px 40px',
                  borderRadius: 999,
                  background: selected ? '#B8935A' : 'rgba(184, 147, 90, 0.2)',
                  color: selected ? '#0A1128' : 'rgba(247, 245, 240, 0.4)',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 14,
                  fontWeight: 600,
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  border: 'none',
                  cursor: selected ? 'pointer' : 'not-allowed',
                  transition: 'all 0.4s ease',
                }}
              >
                Continuer
                <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
              </button>
            </div>
          </div>
        )}

        {/* ─── ÉTAPE 2 : Soléna + recommandation ─── */}
        {step === 2 && product && (
          <div data-testid="decouvrir-step2" style={{ textAlign: 'center' }}>
            {/* Apparition douce de Soléna */}
            <div
              style={{
                opacity: showSolena ? 1 : 0,
                transform: showSolena ? 'translateY(0)' : 'translateY(20px)',
                transition: 'opacity 1600ms ease, transform 1600ms cubic-bezier(0.16, 1, 0.3, 1)',
                marginBottom: 48,
              }}
            >
              <p
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontStyle: 'italic',
                  fontSize: 22,
                  lineHeight: 1.5,
                  color: 'rgba(247, 245, 240, 0.92)',
                  maxWidth: 560,
                  margin: '0 auto 12px',
                }}
              >
                &laquo;&nbsp;Merci de m&apos;avoir confié quelques instants de votre histoire.&nbsp;&raquo;
              </p>
              <p
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 12,
                  letterSpacing: '0.24em',
                  textTransform: 'uppercase',
                  color: 'rgba(184, 147, 90, 0.8)',
                  margin: 0,
                }}
              >
                Soléna
              </p>
            </div>

            {/* Recommandation */}
            <div
              style={{
                opacity: showSolena ? 1 : 0,
                transform: showSolena ? 'translateY(0)' : 'translateY(20px)',
                transition: 'opacity 1600ms 600ms ease, transform 1600ms 600ms cubic-bezier(0.16, 1, 0.3, 1)',
                background: 'rgba(30, 42, 94, 0.35)',
                border: '1px solid rgba(184, 147, 90, 0.3)',
                borderRadius: 20,
                padding: '48px 40px',
                maxWidth: 560,
                margin: '0 auto',
              }}
              data-testid="decouvrir-recommendation"
            >
              <p
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  letterSpacing: '0.4em',
                  textTransform: 'uppercase',
                  color: 'rgba(184, 147, 90, 0.85)',
                  marginBottom: 20,
                }}
              >
                Ce qui vous correspond
              </p>
              <h2
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                  fontWeight: 400,
                  color: '#F7F5F0',
                  lineHeight: 1.25,
                  marginBottom: 16,
                }}
              >
                {product.title}
              </h2>
              <p
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 15,
                  lineHeight: 1.6,
                  color: 'rgba(247, 245, 240, 0.72)',
                  marginBottom: 32,
                }}
              >
                {product.subtitle}
              </p>

              <div
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 28,
                  fontStyle: 'italic',
                  color: '#B8935A',
                  marginBottom: 32,
                }}
              >
                {product.price}
              </div>

              <Link
                to={product.to}
                data-testid="decouvrir-cta"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '16px 36px',
                  borderRadius: 999,
                  background: '#B8935A',
                  color: '#0A1128',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  fontWeight: 600,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  textDecoration: 'none',
                  transition: 'all 0.4s ease',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#C9A24B'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = '#B8935A'; }}
              >
                Découvrir
                <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
              </Link>
            </div>

            {/* Retour */}
            <button
              type="button"
              onClick={() => { setStep(1); setShowSolena(false); }}
              data-testid="decouvrir-back-btn"
              style={{
                marginTop: 40,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                background: 'transparent',
                border: 'none',
                color: 'rgba(247, 245, 240, 0.55)',
                fontFamily: 'Inter, sans-serif',
                fontSize: 12,
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                cursor: 'pointer',
                opacity: showSolena ? 1 : 0,
                transition: 'opacity 1600ms 1200ms ease',
              }}
            >
              <ArrowLeft style={{ width: 12, height: 12 }} strokeWidth={2} />
              Choisir une autre situation
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
