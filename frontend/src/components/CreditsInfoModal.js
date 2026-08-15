import React, { useEffect } from 'react';
import { X, Sparkles, HelpCircle, MessageCircle, BookOpen, Compass, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * CreditsInfo — contenu explicatif partagé.
 * Utilisé en :
 *   1. Modal (via <CreditsInfoModal open onClose>)
 *   2. Section pleine page (via <CreditsInfoContent />)
 */

const USAGE = [
  {
    icon: MessageCircle,
    title: '1 question à Soléna',
    cost: '5 crédits',
    desc: 'Une question posée au chat guidé — sur ton mois, un doute, un transit qui te trouble.',
  },
  {
    icon: BookOpen,
    title: '1 tirage de tarot approfondi',
    cost: '15 crédits',
    desc: 'Tarot de Marseille, croix celtique ou tarologie complète — 5 arcanes commentés en détail.',
  },
  {
    icon: Compass,
    title: 'Astro-guidance mensuelle',
    cost: '10 crédits',
    desc: 'Un dossier synthétique de ton mois à venir — cycles, aspects majeurs, rendez-vous à honorer.',
  },
];

const PACKS = [
  { name: 'Découverte',   credits: 40,  price: '6,99€',  hint: '8 questions ou 2 tirages tarot' },
  { name: 'Régulier',     credits: 100, price: '14,99€', hint: '20 questions · le plus choisi', badge: true },
  { name: 'Généreux',     credits: 250, price: '29,99€', hint: 'Meilleure valeur · 3 mois d\'exploration' },
];

export function CreditsInfoContent({ compact = false }) {
  return (
    <div style={{ fontFamily: 'Inter, sans-serif' }}>
      {!compact && (
        <>
          <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Comment ça marche</p>
          <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 20 }}>
            Un crédit = <span className="ps-italic">une intention posée à Soléna.</span>
          </h2>
          <p className="ps-body" style={{ color: '#232323', marginBottom: 40 }}>
            Les crédits te permettent de venir voir Soléna au fil des mois — sans repayer
            une lecture complète à chaque fois. C&apos;est ton <strong>abonnement libre</strong>,
            que tu utilises quand tu en as vraiment besoin.
          </p>
        </>
      )}

      {/* Usages */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 16, marginBottom: 32,
      }}>
        {USAGE.map((u) => {
          const Icon = u.icon;
          return (
            <div key={u.title} data-testid={`credits-usage-${u.title.replace(/[^a-z]/gi, '-').toLowerCase()}`}
              style={{
                background: '#fff', border: '1px solid #E3E1DC',
                borderRadius: 12, padding: 20,
              }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(201,162,75,0.10)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 14,
              }}>
                <Icon style={{ width: 20, height: 20, color: '#C9A24B' }} strokeWidth={1.6} />
              </div>
              <div style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 17, fontWeight: 500, color: '#0F1A3C',
                marginBottom: 4,
              }}>{u.title}</div>
              <div style={{
                fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                letterSpacing: '0.14em', textTransform: 'uppercase',
                color: '#8F6E24', marginBottom: 10,
              }}>= {u.cost}</div>
              <p style={{ fontSize: 13, lineHeight: 1.55, color: '#6B7280', margin: 0 }}>
                {u.desc}
              </p>
            </div>
          );
        })}
      </div>

      {/* Packs */}
      <p className="ps-eyebrow" style={{ marginBottom: 12 }}>Nos packs de crédits</p>
      <div style={{ display: 'grid', gap: 10, marginBottom: 32 }}>
        {PACKS.map((p) => (
          <div key={p.name} data-testid={`credits-pack-${p.name.toLowerCase().replace(/\s+/g, '-')}`}
            className="ps-credits-pack-row"
            style={{
              display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
              padding: '14px 18px', background: '#fff',
              border: p.badge ? '1px solid #C9A24B' : '1px solid #E3E1DC',
              borderRadius: 10,
            }}>
            <div style={{
              fontFamily: 'Playfair Display, serif', fontSize: 18, fontWeight: 500,
              color: '#0F1A3C', minWidth: 0,
            }}>{p.name}</div>
            <div style={{
              fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#8F6E24',
              fontWeight: 600, minWidth: 0, whiteSpace: 'nowrap',
            }}>{p.credits} cr</div>
            <div style={{ flex: '1 1 200px', fontSize: 13, color: '#6B7280', minWidth: 0 }}>{p.hint}</div>
            <div style={{
              fontFamily: 'Playfair Display, serif', fontSize: 20, fontWeight: 500,
              color: '#0F1A3C', whiteSpace: 'nowrap',
            }}>{p.price}</div>
            {p.badge && <span style={{
              background: '#C9A24B', color: '#0F1A3C',
              padding: '3px 8px', borderRadius: 4,
              fontSize: 10, fontWeight: 600, letterSpacing: '0.12em',
              textTransform: 'uppercase',
            }}>Best</span>}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Link to="/acheter-credits" className="ps-btn ps-btn-primary"
          data-testid="credits-info-cta-buy" style={{ padding: '12px 24px' }}>
          <Sparkles style={{ width: 16, height: 16 }} strokeWidth={2} />
          Acheter des crédits
        </Link>
        <Link to="/inscription" className="ps-btn ps-btn-outline"
          data-testid="credits-info-cta-signup" style={{ padding: '12px 24px' }}>
          Aperçu Thème Natal + 20 crédits offerts
          <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
        </Link>
      </div>
    </div>
  );
}

export default function CreditsInfoModal({ open, onClose }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div data-testid="credits-info-overlay" onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 500,
        background: 'rgba(15,26,60,0.72)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24,
      }}>
      <div data-testid="credits-info-modal" onClick={(e) => e.stopPropagation()}
        style={{
          background: '#F7F5F0', borderRadius: 16,
          maxWidth: 760, width: '100%', maxHeight: '90vh', overflowY: 'auto',
          border: '1px solid #E3E1DC',
          boxShadow: '0 40px 80px rgba(0,0,0,0.35)',
        }}>
        <div style={{
          position: 'sticky', top: 0, zIndex: 2,
          background: '#F7F5F0', borderBottom: '1px solid #E3E1DC',
          padding: '20px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'rgba(201,162,75,0.12)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <HelpCircle style={{ width: 20, height: 20, color: '#C9A24B' }} strokeWidth={1.8} />
            </div>
            <div style={{
              fontFamily: 'Playfair Display, serif', fontSize: 20, fontWeight: 500,
              color: '#0F1A3C',
            }}>À quoi servent les crédits ?</div>
          </div>
          <button onClick={onClose} data-testid="credits-info-close"
            aria-label="Fermer"
            style={{
              background: 'transparent', border: 'none', cursor: 'pointer',
              width: 40, height: 40, borderRadius: 999, color: '#6B7280',
            }}>
            <X style={{ width: 22, height: 22 }} strokeWidth={1.8} />
          </button>
        </div>
        <div style={{ padding: 28 }}>
          <CreditsInfoContent />
        </div>
      </div>
    </div>
  );
}
