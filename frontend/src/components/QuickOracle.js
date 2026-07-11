import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, X } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const ZODIACS = [
  'Bélier', 'Taureau', 'Gémeaux', 'Cancer',
  'Lion', 'Vierge', 'Balance', 'Scorpion',
  'Sagittaire', 'Capricorne', 'Verseau', 'Poisson'
];

const ORACLE_TEMPLATES = {
  'Bélier': {
    icon: '♈',
    daily: "Mercure te pousse à l'action — tes paroles sont ta force aujourd'hui. Une rencontre fortuite pourrait changer tes plans amoureux.",
  },
  'Taureau': {
    icon: '♉',
    daily: "Vénus sourit à tes amours. C'est le moment pour clarifier tes sentiments. Stabilité et confiance prévalent.",
  },
  'Gémeaux': {
    icon: '♊',
    daily: "Communication magnifique! Exprime ce que tu retenus. Les connexions intellectuelles deviennent électriques.",
  },
  'Cancer': {
    icon: '♋',
    daily: "Émotions en surface. Protège ton cœur, mais reste ouvert. Une personne du passé pourrait réapparaître.",
  },
  'Lion': {
    icon: '♌',
    daily: "Ton charisme est irrésistible. C'est ta journée — prends les devants en amour. Confiance débordante.",
  },
  'Vierge': {
    icon: '♍',
    daily: "Réflexion et analyse. Avant d'avancer, comprends ce que tu veux vraiment. Clarté émerge lentement.",
  },
  'Balance': {
    icon: '♎',
    daily: "Harmonie en vue. Les relations retrouvent l'équilibre. Une belle réconciliation est possible.",
  },
  'Scorpion': {
    icon: '♏',
    daily: "Intensité magnétique. Tu attires exactement ce que tu projettes. Profondeur et transformation.",
  },
  'Sagittaire': {
    icon: '♐',
    daily: "Optimisme débordant. Une opportunité d'amour lointain se présente. Sois courageux.",
  },
  'Capricorne': {
    icon: '♑',
    daily: "Responsabilité appelle. Tes fondations émotionnelles se renforcent. Sérieux dans l'amour.",
  },
  'Verseau': {
    icon: '♒',
    daily: "Liberté d'expression magnifique. Tes idées futuristes fascinent. Connections authentiques.",
  },
  'Poisson': {
    icon: '♓',
    daily: "Intuition surpuissante. Écoute ton ressenti — c'est ta meilleure boussole aujourd'hui. Connexion soulaire.",
  },
};

/**
 * QuickOracle — Landing page "JAB" pour capture gratuite immédiate
 * Design ultra-simple, 1-click, micro-valeur = trust + lead
 */
export default function QuickOracle({ onClose, onSelectPack }) {
  const [step, setStep] = useState(1); // 1 = select sign, 2 = show oracle, 3 = show packs
  const [selectedSign, setSelectedSign] = useState(null);
  const [oracleData, setOracleData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSelectSign = async (sign) => {
    setSelectedSign(sign);
    setLoading(true);
    
    // Simulate API call (or replace with real backend call)
    setTimeout(() => {
      setOracleData({
        sign,
        daily: ORACLE_TEMPLATES[sign].daily,
        generatedAt: new Date().toLocaleString('fr-FR'),
      });
      setStep(2);
      setLoading(false);
    }, 1200);
  };

  const proceedToUpsell = () => {
    setStep(3);
  };

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center px-4 py-6"
      style={{
        background: 'linear-gradient(135deg, rgba(6,3,20,0.95), rgba(20,10,40,0.98))',
        backdropFilter: 'blur(8px)',
      }}>
      <div className="w-full max-w-2xl relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-8 right-0 text-white opacity-60 hover:opacity-100 transition"
          style={{ zIndex: 10001 }}
        >
          <X size={24} strokeWidth={1.5} />
        </button>

        {/* STEP 1: SELECT ZODIAC */}
        {step === 1 && (
          <div className="rounded-2xl p-8 md:p-12 text-center"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.08), rgba(20,15,40,0.6))',
              border: '1px solid rgba(212,175,55,0.25)',
              backdropFilter: 'blur(12px)',
            }}>
            <div className="mb-6">
              <Sparkles size={36} style={{ color: '#D4AF37', margin: '0 auto' }} />
            </div>
            <h2 className="text-2xl md:text-3xl mb-3" style={{
              fontFamily: 'Cormorant Garamond, serif',
              color: '#F4E8D2',
              fontWeight: 300,
            }}>
              ✨ Votre oracle du jour
            </h2>
            <p className="text-sm mb-8" style={{ color: 'rgba(244,232,210,0.7)' }}>
              Sélectionnez votre signe pour une guidance gratuite personnalisée.
            </p>

            {/* Zodiac grid */}
            <div className="grid grid-cols-3 md:grid-cols-4 gap-3 md:gap-4 mb-8">
              {ZODIACS.map((sign) => (
                <button
                  key={sign}
                  onClick={() => handleSelectSign(sign)}
                  disabled={loading}
                  className="p-4 rounded-lg transition transform hover:scale-110 active:scale-95"
                  style={{
                    background: 'rgba(212,175,55,0.12)',
                    border: '1px solid rgba(212,175,55,0.25)',
                    color: '#D4AF37',
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: '0.9rem',
                    fontWeight: 300,
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.5 : 1,
                  }}>
                  {sign}
                </button>
              ))}
            </div>

            <p className="text-[11px] uppercase" style={{
              color: 'rgba(212,175,55,0.5)',
              letterSpacing: '0.15em',
              fontWeight: 300,
            }}>
              Aucune inscription nécessaire
            </p>
          </div>
        )}

        {/* STEP 2: SHOW ORACLE */}
        {step === 2 && oracleData && (
          <div className="rounded-2xl p-8 md:p-12 text-center"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(167,139,250,0.08))',
              border: '1px solid rgba(212,175,55,0.35)',
              backdropFilter: 'blur(12px)',
              animation: 'fadeInUp 0.6s ease-out',
            }}>
            <div className="mb-6">
              <div className="text-5xl mb-3">{ORACLE_TEMPLATES[selectedSign].icon}</div>
              <h3 className="text-2xl mb-2" style={{
                fontFamily: 'Cormorant Garamond, serif',
                color: '#D4AF37',
                fontWeight: 300,
              }}>
                {selectedSign}
              </h3>
              <p className="text-[10px] uppercase" style={{
                color: 'rgba(212,175,55,0.5)',
                letterSpacing: '0.15em',
              }}>
                {new Date().toLocaleDateString('fr-FR', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>

            {/* Oracle text */}
            <div className="mb-10 p-6 rounded-lg"
              style={{
                background: 'rgba(212,175,55,0.08)',
                border: '1px solid rgba(212,175,55,0.18)',
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '1.1rem',
                lineHeight: 1.8,
                color: '#F4E8D2',
                fontStyle: 'italic',
              }}>
              « {oracleData.daily} »
            </div>

            {/* CTA buttons */}
            <div className="space-y-3">
              <button
                onClick={proceedToUpsell}
                className="w-full py-3 rounded-lg font-medium text-sm uppercase transition"
                style={{
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#0C0918',
                  letterSpacing: '0.2em',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}>
                Voir la lecture COMPLÈTE
                <ArrowRight size={14} className="inline ml-2" strokeWidth={2} />
              </button>

              <button
                onClick={onClose}
                className="w-full py-3 rounded-lg text-sm uppercase transition"
                style={{
                  background: 'transparent',
                  color: 'rgba(212,175,55,0.7)',
                  border: '1px solid rgba(212,175,55,0.3)',
                  letterSpacing: '0.2em',
                  cursor: 'pointer',
                }}>
                Peut-être plus tard
              </button>
            </div>

            <p className="text-[10px] uppercase mt-6" style={{
              color: 'rgba(212,175,55,0.4)',
              letterSpacing: '0.15em',
            }}>
              ✧ Lecture personnalisée basée sur votre date exacte
            </p>
          </div>
        )}

        {/* STEP 3: SHOW UPSELL PACKS */}
        {step === 3 && (
          <CreditsUpsellPanel onSelectPack={onSelectPack} onBack={() => setStep(2)} />
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

/**
 * CreditsUpsellPanel — Affiche les 3 packs avec ancrage psychologique
 */
function CreditsUpsellPanel({ onSelectPack, onBack }) {
  const PACKS = [
    {
      id: 'initiation',
      name: 'Initiation',
      emoji: '🌙',
      price: '4,99 €',
      credits: 15,
      bonus: 0,
      features: [
        'Oracle du jour complété',
        '1 thème natal rapide',
        'Accès 7 jours',
      ],
      badge: null,
      cta: 'Essayer',
    },
    {
      id: 'clarte',
      name: 'Clarté',
      emoji: '✨',
      price: '14,99 €',
      credits: 60,
      bonus: 10,
      originalPrice: '19,99 €',
      features: [
        '50 crédits + 10 BONUS 🎁',
        'Thème natal complet (PDF 40p)',
        'Synastrie de base',
        'Chat Solena illimité 30j',
      ],
      badge: {
        text: '⭐ Bestseller',
        subtext: '78% des utilisateurs',
      },
      highlight: true,
      cta: 'Débloquer Clarté',
    },
    {
      id: 'flammes',
      name: 'Flammes Jumelles',
      emoji: '🔥',
      price: '29,99 €',
      credits: 130,
      bonus: 30,
      features: [
        '100 crédits + 30 BONUS 🎁',
        'Accès illimité 30 jours',
        'Synastrie complète',
        'Session coaching (valeur 50€)',
      ],
      badge: {
        text: '🔥 Meilleure valeur',
        subtext: '10 places/jour',
      },
      cta: 'Accéder Flammes Jumelles',
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h3 className="text-xl md:text-2xl mb-2" style={{
          fontFamily: 'Cormorant Garamond, serif',
          color: '#F4E8D2',
          fontWeight: 300,
        }}>
          Accédez à votre profondeur cosmique
        </h3>
        <p className="text-sm" style={{ color: 'rgba(244,232,210,0.7)' }}>
          Chaque plan vous amène plus loin dans votre voyage astrologique.
        </p>
      </div>

      {/* Packs */}
      <div className="grid md:grid-cols-3 gap-4">
        {PACKS.map((pack) => (
          <div
            key={pack.id}
            className="rounded-xl p-6 transition transform hover:scale-105"
            style={{
              background: pack.highlight
                ? 'linear-gradient(135deg, rgba(232,199,102,0.15), rgba(212,175,55,0.08))'
                : 'rgba(212,175,55,0.08)',
              border: pack.highlight
                ? '2px solid rgba(232,199,102,0.4)'
                : '1px solid rgba(212,175,55,0.2)',
              position: 'relative',
            }}>
            {/* Badge */}
            {pack.badge && (
              <div className="absolute -top-3 left-4 text-[10px] uppercase px-3 py-1"
                style={{
                  background: '#D4AF37',
                  color: '#0C0918',
                  fontWeight: 700,
                  borderRadius: '4px',
                  letterSpacing: '0.1em',
                }}>
                {pack.badge.text}
                <div style={{ fontSize: '8px', fontWeight: 400 }}>
                  {pack.badge.subtext}
                </div>
              </div>
            )}

            {/* Icon & Name */}
            <div className="text-3xl mb-2">{pack.emoji}</div>
            <h4 className="text-lg font-semibold mb-1" style={{ color: '#D4AF37' }}>
              {pack.name}
            </h4>

            {/* Price */}
            <div className="flex items-baseline gap-2 mb-4">
              <span className="text-2xl font-bold" style={{ color: '#F4E8D2' }}>
                {pack.price}
              </span>
              {pack.originalPrice && (
                <span className="text-xs line-through" style={{ color: 'rgba(244,232,210,0.4)' }}>
                  {pack.originalPrice}
                </span>
              )}
            </div>

            {/* Features */}
            <ul className="space-y-2 mb-6 text-sm">
              {pack.features.map((feature, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span style={{ color: '#D4AF37', marginTop: '2px' }}>✓</span>
                  <span style={{ color: 'rgba(244,232,210,0.8)' }}>{feature}</span>
                </li>
              ))}
            </ul>

            {/* CTA */}
            <button
              onClick={() => onSelectPack(pack.id)}
              className="w-full py-2 rounded-lg text-sm font-bold uppercase transition"
              style={{
                background: pack.highlight ? 'linear-gradient(135deg, #D4AF37, #E8C766)' : 'rgba(212,175,55,0.2)',
                color: pack.highlight ? '#0C0918' : '#D4AF37',
                border: pack.highlight ? 'none' : '1px solid rgba(212,175,55,0.3)',
                cursor: 'pointer',
                letterSpacing: '0.1em',
              }}>
              {pack.cta}
            </button>
          </div>
        ))}
      </div>

      {/* Back button */}
      <button
        onClick={onBack}
        className="w-full py-2 text-sm uppercase"
        style={{
          background: 'transparent',
          color: 'rgba(212,175,55,0.6)',
          border: '1px solid rgba(212,175,55,0.2)',
          borderRadius: '8px',
          cursor: 'pointer',
          letterSpacing: '0.1em',
        }}>
        ← Retour
      </button>
    </div>
  );
}
