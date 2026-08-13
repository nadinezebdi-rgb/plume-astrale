import React, { useState } from 'react';
import { ArrowRight, X, Sparkles } from 'lucide-react';

/**
 * RetentionCTA — Boucle de rétention ininterrompue
 * Affiche après CHAQUE service délivré une proposition de "prochaine étape"
 * 
 * Usage: 
 * <RetentionCTA 
 *   type="oracle_completed"
 *   onNext={() => navigateToPremium()}
 *   creditsNeeded={20}
 * />
 */
export default function RetentionCTA({ type, onNext, onDismiss, creditsNeeded = 0 }) {
  const [dismissed, setDismiss] = useState(false);

  if (dismissed) return null;

  const SCENARIOS = {
    // Après Oracle gratuit → Upsell thème complet
    oracle_completed: {
      emoji: null,
      title: 'C\'était juste l\'aperçu...',
      message: 'Votre lecture complète vous attend. Découvrez votre thème natal en détail avec rapport PDF 40 pages.',
      cta: 'Voir mon thème complet',
      color: '#D4AF37',
      creditsNeeded: 20,
    },

    // Après chat session → Upsell synastrie
    chat_completed: {
      emoji: null,
      title: 'Prêt pour la prochaine lecture ?',
      message: 'Découvrez votre synastrie de couple — comment les astres vous unissent avec votre partenaire.',
      cta: 'Analyser ma synastrie',
      color: '#E8944A',
      creditsNeeded: 25,
    },

    // Après thème natal → Upsell coaching
    natal_completed: {
      emoji: null,
      title: 'Allez plus loin avec Solena',
      message: 'Obtenez une session de coaching astrologique personnalisé pour interpréter vos cycles amoureux à venir.',
      cta: 'Débloquer session coaching',
      color: '#D4AF37',
      creditsNeeded: 30,
    },

    // Après chaque action → Proposition d'accès illimité
    limited_time_upsell: {
      emoji: '🔥',
      title: '10 places disponibles aujourd\'hui',
      message: 'Accès illimité 30 jours aux lectures complètes, synastries, et sessions coaching.',
      cta: 'Débloquer accès illimité',
      color: '#E8944A',
      creditsNeeded: 130,
    },

    // Notification de retour (après 3 jours sans activité)
    re_engagement: {
      emoji: '🌙',
      title: 'Les astres te manquent...',
      message: 'Ton thème se renforce chaque jour. Reviens découvrir ce qui a changé dans tes cycles.',
      cta: 'Redécouvrir mon thème',
      color: '#A89B7E',
      creditsNeeded: 0,
    },
  };

  const scenario = SCENARIOS[type] || SCENARIOS.chat_completed;
  const needed = creditsNeeded || scenario.creditsNeeded;

  return (
    <div
      className="w-full rounded-2xl p-6 md:p-8 animate-slideIn"
      style={{
        background: `linear-gradient(135deg, rgba(212,175,55,0.08), rgba(${scenario.color === '#D4AF37' ? '232,199,102' : '232,148,74'},0.04))`,
        border: `1px solid ${scenario.color}44`,
        boxShadow: `0 0 20px ${scenario.color}22`,
      }}
    >
      <button
        onClick={() => setDismiss(true)}
        className="float-right p-1 opacity-50 hover:opacity-100 transition"
        style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
      >
        <X size={18} style={{ color: scenario.color }} strokeWidth={1.5} />
      </button>

      <div className="flex items-start gap-4">
        <div className="text-4xl flex-shrink-0">{scenario.emoji}</div>

        <div className="flex-1 pr-6">
          <h3
            className="text-lg font-semibold mb-2"
            style={{ color: scenario.color }}
          >
            {scenario.title}
          </h3>

          <p className="text-sm mb-5" style={{ color: 'rgba(244,232,210,0.8)' }}>
            {scenario.message}
          </p>

          {/* CTA Button */}
          <button
            onClick={onNext}
            className="px-6 py-2.5 rounded-lg font-semibold text-sm uppercase transition-all inline-flex items-center gap-2 hover:scale-105"
            style={{
              background: `linear-gradient(135deg, ${scenario.color}, ${scenario.color}cc)`,
              color: scenario.color === '#D4AF37' ? '#0C0918' : '#FFFFFF',
              border: 'none',
              cursor: 'pointer',
              letterSpacing: '0.1em',
            }}
          >
            {scenario.cta}
            <ArrowRight size={14} strokeWidth={2} />
          </button>

          {/* Credit info */}
          {needed > 0 && (
            <div className="text-[10px] mt-3" style={{ color: 'rgba(212,175,55,0.6)' }}>
              ✓ Besoin de {needed} crédits · {scenario.color === '#D4AF37' ? 'Disponible dès 4,99€' : 'Pack Flammes Jumelles'}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideIn {
          animation: slideIn 0.6s ease-out;
        }
      `}</style>
    </div>
  );
}

/**
 * NotificationBadge — Petite notification sticky en bas (mobile-first)
 * Utilisée pour les re-engagement et reminders non-intrusifs
 */
export function NotificationBadge({ message, action, onDismiss, autoClose = true }) {
  const [show, setShow] = useState(true);

  if (!show) return null;

  // Auto-dismiss après 8 secondes
  React.useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => setShow(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [autoClose]);

  return (
    <div
      className="fixed bottom-4 left-4 right-4 md:right-auto md:max-w-sm rounded-xl p-4 z-[100] shadow-lg animate-slideUp"
      style={{
        background: 'linear-gradient(135deg, rgba(212,175,55,0.9), rgba(232,199,102,0.8))',
        border: '1px solid rgba(232,199,102,0.5)',
        backdropFilter: 'blur(10px)',
      }}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1">
          <p
            className="text-sm font-medium"
            style={{ color: '#0C0918' }}
          >
            {message}
          </p>
        </div>

        {action && (
          <button
            onClick={action.onClick}
            className="px-3 py-1 rounded-lg text-xs font-bold uppercase"
            style={{
              background: '#0C0918',
              color: '#D4AF37',
              border: 'none',
              cursor: 'pointer',
              letterSpacing: '0.1em',
            }}
          >
            {action.text}
          </button>
        )}

        <button
          onClick={() => {
            setShow(false);
            if (onDismiss) onDismiss();
          }}
          className="p-1 opacity-70 hover:opacity-100"
          style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
        >
          <X size={16} style={{ color: '#0C0918' }} strokeWidth={2} />
        </button>
      </div>

      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(100px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideUp {
          animation: slideUp 0.4s ease-out;
        }
      `}</style>
    </div>
  );
}

/**
 * Sticky CTA Band — Toujours visible en bas du mobile
 * Encourage l'action continue sans fermer la page
 */
export function StickyCTABand({ onAction, context = 'generic' }) {
  const [dismissed, setDismiss] = useState(false);

  if (dismissed) return null;

  const MESSAGES = {
    low_credits: {
      icon: '⚡',
      text: 'Manques-tu de crédits? +10 gratuits aujourd\'hui',
      cta: 'Recharger',
      color: '#E8944A',
    },
    upsell_reading: {
      icon: '🔮',
      text: 'Veux-tu voir ton synastrie complète?',
      cta: 'Découvrir',
      color: '#D4AF37',
    },
    generic: {
      icon: '✨',
      text: 'Accès illimité à toutes tes lectures',
      cta: 'Débloquer',
      color: '#D4AF37',
    },
  };

  const msg = MESSAGES[context] || MESSAGES.generic;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 md:hidden p-3 z-50"
      style={{
        background: `linear-gradient(135deg, ${msg.color}22, ${msg.color}11)`,
        borderTop: `1px solid ${msg.color}55`,
        backdropFilter: 'blur(8px)',
      }}
    >
      <div className="flex items-center justify-between gap-3">
        <span style={{ color: msg.color, fontSize: '18px' }}>{msg.icon}</span>
        <span className="flex-1 text-xs font-medium" style={{ color: '#F4E8D2' }}>
          {msg.text}
        </span>
        <button
          onClick={onAction}
          className="px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all active:scale-95"
          style={{
            background: msg.color,
            color: '#0C0918',
            border: 'none',
            cursor: 'pointer',
            letterSpacing: '0.1em',
          }}
        >
          {msg.cta}
        </button>
        <button
          onClick={() => setDismiss(true)}
          className="p-1 opacity-50 hover:opacity-100"
          style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
        >
          <X size={14} style={{ color: '#F4E8D2' }} strokeWidth={2} />
        </button>
      </div>
    </div>
  );
}
