import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link2, Copy, Check, Users, Gift, Share2, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Panneau parrainage — affiché dans l'onglet "Parrainage" de /mon-compte.
 * - Lien unique + bouton Copier
 * - Boutons partage WhatsApp / Email / Twitter
 * - Statistiques (invités, achats, récompenses)
 * - Explication du fonctionnement
 */
const ReferralPanel = ({ token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    (async () => {
      try {
        const r = await axios.get(`${API}/api/referral/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (mounted) setData(r.data);
      } catch (e) {
        if (mounted) setError('Impossible de charger le programme de parrainage.');
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [token]);

  const copy = async () => {
    if (!data?.link) return;
    try {
      await navigator.clipboard.writeText(data.link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* ignore */ }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12" data-testid="referral-panel-loading">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: 'var(--pa-accent)' }} />
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="rounded-xl p-6 text-sm" data-testid="referral-panel-error"
           style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)', color: 'rgba(227,215,255,0.8)' }}>
        {error || 'Le programme de parrainage n\'est pas encore disponible.'}
      </div>
    );
  }

  const shareText = data.share_text || '';
  const shareUrl = data.link;
  const encodedText = encodeURIComponent(`${shareText}\n${shareUrl}`);
  const whatsappUrl = `https://wa.me/?text=${encodedText}`;
  const emailUrl = `mailto:?subject=${encodeURIComponent('Découvre Plume Astrale 🌙')}&body=${encodedText}`;
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodedText}`;

  return (
    <div className="space-y-6" data-testid="referral-panel">
      {/* Bloc explication */}
      <div className="rounded-2xl p-6"
           style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
        <div className="flex items-start gap-4 mb-4">
          <div className="rounded-full p-3 shrink-0"
               style={{ background: 'rgba(201,162,75,0.12)', border: '1px solid rgba(201,162,75,0.35)' }}>
            <Gift className="w-5 h-5" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
          </div>
          <div>
            <h2 className="text-2xl mb-2"
                style={{ fontFamily: 'Playfair Display, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Partage la lumière, reçois un cadeau
            </h2>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)' }}>
              Envoie ton lien unique à un proche. Dès qu&apos;il commande son <strong>premier</strong> pack Plume Astrale,
              Soléna t&apos;offre l&apos;<strong style={{ color: 'var(--pa-accent)' }}>horoscope journalier de ton signe</strong>
              par email — c&apos;est un merci pour chaque âme que tu nous confies. 🌙
            </p>
          </div>
        </div>
      </div>

      {/* Lien + Copier */}
      <div className="rounded-2xl p-6"
           style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
        <div className="text-[10px] uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em', fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
          ✦ Ton lien de parrainage
        </div>
        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl overflow-hidden"
               style={{ background: 'rgba(201,162,75,0.05)', border: '1px solid rgba(201,162,75,0.25)' }}>
            <Link2 className="w-4 h-4 shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
            <span className="text-sm truncate" style={{ color: 'var(--pa-body)', fontFamily: 'monospace' }}
                  data-testid="referral-link-text">
              {data.link}
            </span>
          </div>
          <button
            onClick={copy}
            data-testid="referral-copy-btn"
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl transition-all hover:opacity-90"
            style={{
              background: copied ? 'rgba(74,222,128,0.14)' : 'linear-gradient(135deg, #C9A24B 0%, #C9A24B 100%)',
              color: copied ? '#4ADE80' : '#0F1A3C',
              border: copied ? '1px solid rgba(74,222,128,0.4)' : 'none',
              fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 11, letterSpacing: '0.15em', textTransform: 'uppercase',
              cursor: 'pointer',
            }}
          >
            {copied ? (<><Check className="w-4 h-4" /> Copié !</>) : (<><Copy className="w-4 h-4" /> Copier le lien</>)}
          </button>
        </div>
        <p className="text-[11px] mt-3" style={{ color: 'var(--pa-muted)' }}>
          Ton code personnel : <strong style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>{data.code}</strong>
        </p>
      </div>

      {/* Partage rapide */}
      <div className="rounded-2xl p-6"
           style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
        <div className="flex items-center gap-2 mb-4">
          <Share2 className="w-4 h-4" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
          <span className="text-xs uppercase" style={{ color: 'var(--pa-accent)', letterSpacing: '0.25em', fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
            Partager en 1 clic
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" data-testid="referral-share-whatsapp"
             className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all hover:opacity-90"
             style={{ background: 'rgba(37,211,102,0.10)', border: '1px solid rgba(37,211,102,0.35)', color: '#25D366', fontSize: 13 }}>
            WhatsApp
          </a>
          <a href={emailUrl} data-testid="referral-share-email"
             className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all hover:opacity-90"
             style={{ background: 'rgba(201,162,75,0.08)', border: '1px solid rgba(201,162,75,0.3)', color: 'var(--pa-accent)', fontSize: 13 }}>
            E-mail
          </a>
          <a href={twitterUrl} target="_blank" rel="noopener noreferrer" data-testid="referral-share-twitter"
             className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all hover:opacity-90"
             style={{ background: 'rgba(139,92,246,0.10)', border: '1px solid rgba(139,92,246,0.35)', color: '#A78BFA', fontSize: 13 }}>
            X / Twitter
          </a>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <StatCell icon={Users} value={data.invited_count} label="Amis invités" testid="referral-stat-invited" />
        <StatCell icon={Link2} value={data.purchased_count} label="Premiers achats" testid="referral-stat-purchased" />
        <StatCell icon={Gift} value={data.rewards_earned} label="Récompenses reçues" testid="referral-stat-rewards" accent />
      </div>

      {/* Historique */}
      {data.referrals && data.referrals.length > 0 && (
        <div className="rounded-2xl p-6"
             style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
          <h3 className="text-base mb-4"
              style={{ fontFamily: 'Playfair Display, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Tes derniers parrainages
          </h3>
          <div className="space-y-2" data-testid="referral-history">
            {data.referrals.slice(0, 8).map((r) => (
              <div key={r.id} className="flex items-center justify-between p-3 rounded-lg"
                   style={{ background: 'rgba(201,162,75,0.04)', border: '1px solid rgba(201,162,75,0.12)' }}>
                <div className="text-xs" style={{ color: 'var(--pa-body)' }}>
                  {r.first_purchase_at
                    ? new Date(r.first_purchase_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
                    : 'En attente'}
                  {r.first_purchase_amount_cents ? ` · ${(r.first_purchase_amount_cents / 100).toFixed(2)}€` : ''}
                </div>
                <div className="text-[10px] uppercase" style={{ letterSpacing: '0.15em',
                     color: r.reward_sent_at ? '#4ADE80' : 'var(--pa-muted)' }}>
                  {r.reward_sent_at ? '✓ Récompense envoyée' : 'À récompenser'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const StatCell = ({ icon: Icon, value, label, testid, accent }) => (
  <div data-testid={testid} className="rounded-2xl p-4 text-center"
       style={{ background: 'var(--pa-surface)', border: `1px solid ${accent ? 'rgba(201,162,75,0.35)' : 'var(--pa-divider)'}` }}>
    <Icon className="w-4 h-4 mx-auto mb-2" strokeWidth={1.5} style={{ color: accent ? 'var(--pa-accent)' : 'var(--pa-muted)' }} />
    <div className="text-2xl mb-1"
         style={{ color: accent ? 'var(--pa-accent)' : 'var(--pa-heading)', fontFamily: 'Playfair Display, serif', fontWeight: 300 }}>
      {value ?? 0}
    </div>
    <div className="text-[10px] uppercase" style={{ color: 'var(--pa-muted)', letterSpacing: '0.15em' }}>{label}</div>
  </div>
);

export default ReferralPanel;
