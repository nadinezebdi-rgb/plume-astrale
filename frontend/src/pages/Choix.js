import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Check, Circle, Sparkles } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';

/**
 * Choix — page de sélection Essentiel / Premium.
 * Migration V3 (Feb 2026) : fond crème #F7F5F0, Playfair Display en titres,
 * cartes blanches à ombre douce, badge "Recommandé" doré.
 */
const Choix = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const data = localStorage.getItem('plume_astrale_data');
    if (!data) { navigate('/formulaire'); return; }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const handleSelectPlan = (plan) => {
    localStorage.setItem('plume_astrale_plan', plan);
    navigate('/paiement');
  };

  if (!userData) {
    return (
      <PsPageShell background="light">
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Loader2 style={{ width: 22, height: 22, color: '#C9A24B' }} className="animate-spin" />
        </div>
      </PsPageShell>
    );
  }

  const essentielFeatures = [
    { text: 'Chemin de vie complet', on: true },
    { text: 'Ann\u00e9e personnelle 2026', on: true },
    { text: 'Identit\u00e9 c\u00e9leste', on: true },
    { text: 'Mission de vie', on: true },
    { text: 'PDF t\u00e9l\u00e9chargeable', on: true },
    { text: 'Tirage Tarot personnalis\u00e9', on: false },
    { text: 'Compatibilit\u00e9 amoureuse', on: false },
    { text: 'Horoscope mensuel', on: false },
  ];

  const premiumFeatures = [
    { text: 'Chemin de vie complet', on: true },
    { text: 'Ann\u00e9e personnelle 2026', on: true },
    { text: 'Identit\u00e9 c\u00e9leste', on: true },
    { text: 'Mission de vie', on: true },
    { text: 'PDF t\u00e9l\u00e9chargeable', on: true },
    { text: 'Tirage Tarot personnalis\u00e9', on: true, highlight: true },
    { text: 'Compatibilit\u00e9 amoureuse', on: true, highlight: true },
    { text: 'Horoscope mensuel', on: true, highlight: true },
  ];

  return (
    <PsPageShell background="light">
      <section
        style={{
          padding: '96px 24px 96px',
          maxWidth: 1100,
          margin: '0 auto',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              color: '#C9A24B',
              marginBottom: 16,
            }}
          >
            ✦ Choisis ta guidance ✦
          </p>
          <h1
            style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(32px, 5.4vw, 52px)',
              fontWeight: 500,
              color: '#0F1A3C',
              lineHeight: 1.15,
              marginBottom: 16,
            }}
          >
            {userData.prenom ? `${userData.prenom}, ton` : 'Ton'}{' '}
            <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>manuscrit t&apos;attend.</span>
          </h1>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 15,
              lineHeight: 1.65,
              color: 'rgba(15,26,60,0.65)',
              maxWidth: 520,
              margin: '0 auto',
            }}
          >
            Deux chemins s&apos;offrent à toi. Choisis celui qui résonne — sans engagement, sans surprise.
          </p>
        </div>

        {/* Plans grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 28,
            marginBottom: 40,
          }}
        >
          <PlanCard
            label="Essentiel"
            price="9,90€"
            tagline="Ton manuscrit céleste de base"
            features={essentielFeatures}
            cta="Découvrir l'essentiel"
            onSelect={() => handleSelectPlan('essentiel')}
            testid="btn-essentiel"
          />
          <PlanCard
            label="Premium"
            price="29,90€"
            tagline="L'expérience cosmique complète"
            features={premiumFeatures}
            cta="Recevoir mon manuscrit complet"
            onSelect={() => handleSelectPlan('premium')}
            recommended
            testid="btn-premium"
          />
        </div>

        {/* Trust badges */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 32,
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            letterSpacing: '0.10em',
            textTransform: 'uppercase',
            color: 'rgba(15,26,60,0.50)',
          }}
        >
          <span>Paiement sécurisé</span>
          <span>Accès immédiat</span>
          <span>Satisfait ou remboursé 30j</span>
        </div>
      </section>
    </PsPageShell>
  );
};

function PlanCard({ label, price, tagline, features, cta, onSelect, recommended, testid }) {
  return (
    <div
      data-testid={`plan-card-${label.toLowerCase()}`}
      style={{
        position: 'relative',
        background: '#FFFFFF',
        border: recommended ? '1px solid #C9A24B' : '1px solid #E3E1DC',
        borderRadius: 16,
        padding: '40px 32px 32px',
        boxShadow: recommended
          ? '0 24px 48px -20px rgba(201,162,75,0.30)'
          : '0 12px 32px -18px rgba(15,26,60,0.10)',
      }}
    >
      {recommended && (
        <div
          style={{
            position: 'absolute',
            top: -14,
            left: 24,
            background: '#C9A24B',
            color: '#0F1A3C',
            fontFamily: 'Inter, sans-serif',
            fontSize: 10,
            fontWeight: 600,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            padding: '5px 14px',
            borderRadius: 999,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <Sparkles style={{ width: 11, height: 11 }} strokeWidth={2} />
          Recommandé
        </div>
      )}

      <p
        style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: '0.20em',
          textTransform: 'uppercase',
          color: recommended ? '#C9A24B' : 'rgba(15,26,60,0.55)',
          marginBottom: 12,
        }}
      >
        {label}
      </p>

      <div
        style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: 40,
          fontWeight: 500,
          color: '#0F1A3C',
          lineHeight: 1,
          marginBottom: 6,
        }}
      >
        {price}
      </div>
      <p
        style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 13,
          color: 'rgba(15,26,60,0.55)',
          marginBottom: 28,
        }}
      >
        {tagline}
      </p>

      <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 32px' }}>
        {features.map((f, i) => (
          <li
            key={i}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '8px 0',
              fontFamily: 'Inter, sans-serif',
              fontSize: 14,
              color: f.on ? '#232323' : 'rgba(15,26,60,0.35)',
              opacity: f.on ? 1 : 0.7,
            }}
          >
            {f.on ? (
              <Check
                style={{ width: 15, height: 15, color: f.highlight ? '#C9A24B' : '#7A8AB0', flexShrink: 0 }}
                strokeWidth={2}
              />
            ) : (
              <Circle
                style={{ width: 8, height: 8, color: 'rgba(15,26,60,0.20)', flexShrink: 0 }}
                strokeWidth={1.5}
              />
            )}
            <span style={{ color: f.highlight ? '#C9A24B' : 'inherit', fontWeight: f.highlight ? 500 : 400 }}>
              {f.text}
            </span>
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={onSelect}
        data-testid={testid}
        className={recommended ? 'ps-btn ps-btn-primary' : 'ps-btn ps-btn-outline'}
        style={{ width: '100%', justifyContent: 'center', padding: '14px 20px' }}
      >
        {cta}
      </button>
    </div>
  );
}

export default Choix;
