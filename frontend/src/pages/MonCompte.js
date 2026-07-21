import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import {
  User, Mail, MapPin, Calendar, Coins, Star, Flame,
  ArrowLeft, ArrowRight, Crown, Check, Sparkles,
  LogOut, RefreshCw, ChevronRight, Gift, Shield
} from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import PageHero from '@/components/PageHero';
import NatalDataModal from '@/components/NatalDataModal';
import LibraryImage from '@/components/LibraryImage';
import BundleCard from '@/components/BundleCard';
import SolenaWritingLoader from '@/components/SolenaWritingLoader';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/* ─────────────────────────────────────────────────────────────────
   Helpers
───────────────────────────────────────────────────────────────── */
const formatDate = (iso) => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'long', year: 'numeric',
    });
  } catch {
    return '—';
  }
};

const ZODIAC_FROM_DATE = (dateStr) => {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  const m = d.getMonth() + 1;
  const j = d.getDate();
  if ((m === 3 && j >= 21) || (m === 4 && j <= 19)) return { signe: 'Bélier',      symbole: '♈' };
  if ((m === 4 && j >= 20) || (m === 5 && j <= 20)) return { signe: 'Taureau',     symbole: '♉' };
  if ((m === 5 && j >= 21) || (m === 6 && j <= 20)) return { signe: 'Gémeaux',     symbole: '♊' };
  if ((m === 6 && j >= 21) || (m === 7 && j <= 22)) return { signe: 'Cancer',      symbole: '♋' };
  if ((m === 7 && j >= 23) || (m === 8 && j <= 22)) return { signe: 'Lion',        symbole: '♌' };
  if ((m === 8 && j >= 23) || (m === 9 && j <= 22)) return { signe: 'Vierge',      symbole: '♍' };
  if ((m === 9 && j >= 23) || (m === 10 && j <= 22)) return { signe: 'Balance',    symbole: '♎' };
  if ((m === 10 && j >= 23) || (m === 11 && j <= 21)) return { signe: 'Scorpion',  symbole: '♏' };
  if ((m === 11 && j >= 22) || (m === 12 && j <= 21)) return { signe: 'Sagittaire',symbole: '♐' };
  if ((m === 12 && j >= 22) || (m === 1 && j <= 19)) return { signe: 'Capricorne', symbole: '♑' };
  if ((m === 1 && j >= 20) || (m === 2 && j <= 18)) return { signe: 'Verseau',     symbole: '♒' };
  return { signe: 'Poissons', symbole: '♓' };
};

/* ─────────────────────────────────────────────────────────────────
   Sous-composant : Carte Fidélité (remplace "streak")
   "Assiduité" = nombre de jours consécutifs de connexion
───────────────────────────────────────────────────────────────── */
const FideliteCard = ({ fidelite, onCheckin, checkinLoading }) => {
  const count    = fidelite?.streak_count      ?? 0;
  const deja     = fidelite?.checked_in_today  ?? false;
  const record   = fidelite?.longest_streak    ?? 0;
  const total    = fidelite?.total_checkins    ?? 0;
  const prochainPalier = fidelite?.next_milestone ?? {};

  const pct = prochainPalier.days
    ? Math.min((count / prochainPalier.days) * 100, 100)
    : 100;

  const flammeColor  = count > 0 ? '#FF6B35' : 'var(--pa-accent)';
  const flammeGlow   = count >= 7 ? '0 0 12px rgba(255,107,53,0.5)' : 'none';

  return (
    <div
      className="rounded-2xl p-6 md:p-8"
      style={{
        background: 'linear-gradient(135deg, rgba(212,175,55,0.07) 0%, rgba(255,107,53,0.03) 100%)',
        border: '1px solid rgba(212,175,55,0.2)',
      }}
      data-testid="fidelite-card"
    >
      {/* En-tête */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="relative">
            <Flame
              className="w-9 h-9"
              strokeWidth={1.5}
              style={{ color: flammeColor, filter: count >= 7 ? `drop-shadow(${flammeGlow})` : 'none' }}
            />
            {count > 0 && (
              <span
                className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-semibold"
                style={{ background: flammeColor, color: '#fff' }}
              >
                {count}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-lg mb-0.5" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Assiduité céleste
            </h3>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              {count === 0
                ? 'Commencez votre présence quotidienne'
                : count === 1
                ? '1 jour consécutif — beau début !'
                : `${count} jours consécutifs`}
            </p>
          </div>
        </div>

        {/* Bouton check-in */}
        <button
          onClick={onCheckin}
          disabled={deja || checkinLoading}
          className="flex items-center gap-2 text-xs uppercase tracking-widest px-4 py-2 rounded-full transition-all duration-300 whitespace-nowrap"
          style={{
            border: deja ? '1px solid rgba(212,175,55,0.2)' : '1px solid rgba(212,175,55,0.5)',
            color: deja ? 'var(--pa-muted)' : 'var(--pa-accent)',
            background: deja ? 'transparent' : 'rgba(212,175,55,0.08)',
            cursor: deja ? 'default' : 'pointer',
            letterSpacing: '0.08em',
          }}
          data-testid="checkin-btn"
        >
          {checkinLoading ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : deja ? (
            <><Check className="w-3.5 h-3.5" /> Présent aujourd'hui</>
          ) : (
            <><Sparkles className="w-3.5 h-3.5" /> Marquer ma présence</>
          )}
        </button>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Jours consécutifs', value: count, icon: null },
          { label: 'Record personnel', value: record, icon: null },
          { label: 'Total de présences', value: total, icon: null },
        ].map(({ label, value, icon }) => (
          <div
            key={label}
            className="rounded-xl p-3 text-center"
            style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.12)' }}
          >
            <div className="text-lg mb-0.5">{icon}</div>
            <div className="text-xl font-light mb-0.5" style={{ color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>
              {value}
            </div>
            <div className="text-[10px] tracking-wider uppercase" style={{ color: 'var(--pa-muted)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Barre de progression vers le prochain palier */}
      {prochainPalier.days && (
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              Prochain palier : {prochainPalier.days} jours
            </span>
            <span className="text-xs" style={{ color: 'var(--pa-accent)' }}>
              + {prochainPalier.bonus} crédits offerts
            </span>
          </div>
          <div className="h-px w-full relative" style={{ background: 'rgba(212,175,55,0.15)' }}>
            <div
              className="h-px absolute left-0 top-0 transition-all duration-1000"
              style={{ width: `${pct}%`, background: 'linear-gradient(90deg, var(--pa-accent), #FF6B35)' }}
            />
          </div>
          <p className="text-xs mt-2" style={{ color: 'var(--pa-muted)' }}>
            Encore {prochainPalier.remaining} jour{prochainPalier.remaining > 1 ? 's' : ''} pour débloquer votre bonus
          </p>
        </div>
      )}
    </div>
  );
};

/* ─────────────────────────────────────────────────────────────────
   Sous-composant : Carte Abonnement
───────────────────────────────────────────────────────────────── */
const AbonnementCard = ({ subscription, onSouscrire, loading }) => {
  const actif = !!subscription;

  if (actif) {
    const nomProduit = subscription.product_id === 'journal_quotidien'
      ? 'Journal Astral Quotidien'
      : subscription.product_id === 'cercle_mensuel'
      ? 'Le Cercle — Mensuel'
      : subscription.product_name || 'Abonnement';

    const montant = subscription.product_id === 'journal_quotidien' ? '15,99 €' : '14,90 €';
    const finPeriode = subscription.current_period_end
      ? formatDate(subscription.current_period_end)
      : null;

    return (
      <div
        className="rounded-2xl p-6 md:p-8"
        style={{
          background: 'linear-gradient(135deg, rgba(167,139,250,0.08) 0%, rgba(212,175,55,0.04) 100%)',
          border: '1px solid rgba(167,139,250,0.3)',
        }}
        data-testid="abonnement-actif"
      >
        <div className="flex items-start gap-4 mb-5">
          <Crown className="w-8 h-8 flex-shrink-0 mt-0.5" strokeWidth={1.5} style={{ color: '#A78BFA' }} />
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                {nomProduit}
              </h3>
              <span
                className="text-[10px] tracking-widest uppercase px-2.5 py-0.5 rounded-full"
                style={{ background: 'rgba(74,222,128,0.15)', color: '#4ADE80', border: '1px solid rgba(74,222,128,0.3)' }}
              >
                Actif
              </span>
            </div>
            <p className="text-sm mt-1" style={{ color: 'var(--pa-muted)' }}>
              {montant} / mois
              {finPeriode && <span> · Prochain renouvellement : {finPeriode}</span>}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {(subscription.product_id === 'journal_quotidien'
            ? [
                '✦ Journal astrologique personnalisé chaque jour',
                '✦ 20 % de réduction sur tous les services',
                '✦ Contenu exclusif abonnés',
                '✦ Priorité sur les nouvelles fonctionnalités',
              ]
            : [
                '✦ Tarot quotidien personnalisé',
                '✦ Horoscope détaillé chaque matin',
                '✦ Lune & énergies du jour',
                '✦ Crédits bonus chaque mois',
              ]
          ).map((item) => (
            <div key={item} className="flex items-start gap-2">
              <span className="text-xs mt-0.5" style={{ color: 'var(--pa-accent)' }}>✦</span>
              <span className="text-xs" style={{ color: 'var(--pa-body)' }}>
                {item.replace('✦ ', '')}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Pas d'abonnement actif → proposer
  return (
    <div
      className="rounded-2xl p-6 md:p-8"
      style={{
        background: 'linear-gradient(135deg, rgba(212,175,55,0.05) 0%, rgba(167,139,250,0.03) 100%)',
        border: '1px solid rgba(212,175,55,0.18)',
      }}
      data-testid="abonnement-inactif"
    >
      <div className="flex items-start gap-4 mb-5">
        <Crown className="w-8 h-8 flex-shrink-0 mt-0.5" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
        <div>
          <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
            Aucun abonnement actif
          </h3>
          <p className="text-sm mt-1" style={{ color: 'var(--pa-muted)' }}>
            Rejoignez l'un de nos parcours pour une guidance quotidienne personnalisée
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Journal Quotidien */}
        <div
          className="rounded-xl p-5 flex flex-col gap-3"
          style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.2)' }}
        >
          <div>
            <p className="text-xs tracking-widest uppercase mb-1" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
              Journal Astral
            </p>
            <p className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
              15,99 €<span className="text-sm font-light"> / mois</span>
            </p>
          </div>
          <ul className="space-y-1.5 flex-1">
            {['Journal personnalisé chaque jour', '20 % de réduction partout', 'Contenu exclusif abonnés'].map(t => (
              <li key={t} className="flex items-start gap-2">
                <Check className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" strokeWidth={2} style={{ color: 'var(--pa-accent)' }} />
                <span className="text-xs" style={{ color: 'var(--pa-body)' }}>{t}</span>
              </li>
            ))}
          </ul>
          <button
            onClick={() => onSouscrire('journal_quotidien')}
            disabled={loading}
            className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-4 py-2.5 rounded-full w-full transition-all duration-300"
            style={{
              background: 'rgba(212,175,55,0.15)',
              border: '1px solid rgba(212,175,55,0.5)',
              color: 'var(--pa-accent)',
              letterSpacing: '0.08em',
            }}
            data-testid="btn-souscrire-journal"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <>S'abonner <ArrowRight className="w-3.5 h-3.5" /></>}
          </button>
        </div>

        {/* Le Cercle */}
        <div
          className="rounded-xl p-5 flex flex-col gap-3"
          style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.2)' }}
        >
          <div>
            <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#A78BFA', letterSpacing: '0.1em' }}>
              Le Cercle
            </p>
            <p className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
              14,90 €<span className="text-sm font-light"> / mois</span>
            </p>
          </div>
          <ul className="space-y-1.5 flex-1">
            {['Tarot quotidien', 'Horoscope détaillé', 'Crédits bonus mensuels'].map(t => (
              <li key={t} className="flex items-start gap-2">
                <Check className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" strokeWidth={2} style={{ color: '#A78BFA' }} />
                <span className="text-xs" style={{ color: 'var(--pa-body)' }}>{t}</span>
              </li>
            ))}
          </ul>
          <Link
            to="/cercle"
            className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-4 py-2.5 rounded-full w-full transition-all duration-300"
            style={{
              background: 'rgba(167,139,250,0.1)',
              border: '1px solid rgba(167,139,250,0.35)',
              color: '#A78BFA',
              letterSpacing: '0.08em',
            }}
            data-testid="btn-voir-cercle"
          >
            Découvrir <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};

/* ─────────────────────────────────────────────────────────────────
   Page principale MonCompte
───────────────────────────────────────────────────────────────── */
const MonCompte = () => {
  const navigate = useNavigate();
  const { user, token, creditBalance, logout, refreshBalance, loading: authLoading } = useAuth();

  const [profil, setProfil]               = useState(null);
  const [fidelite, setFidelite]           = useState(null);
  const [subscription, setSubscription]   = useState(null);
  const [transactions, setTransactions]   = useState([]);
  const [loading, setLoading]             = useState(true);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [checkinMsg, setCheckinMsg]       = useState(null);
  const [subsLoading, setSubsLoading]     = useState(false);
  const [subsError, setSubsError]         = useState(null);
  const [activeTab, setActiveTab]         = useState('apercu');
  const [natalModalOpen, setNatalModalOpen] = useState(false);
  const [promoCode, setPromoCode]       = useState('');
  const [promoLoading, setPromoLoading] = useState(false);
  const [promoMsg, setPromoMsg]         = useState(null); // {type:'success'|'error', text}
  const [pdfLoading, setPdfLoading]     = useState(false);

  // Redirection si non connecté — attendre que AuthContext finisse de restaurer la session
  useEffect(() => {
    if (!authLoading && !token) navigate('/connexion');
  }, [token, authLoading, navigate]);

  // Succès abonnement depuis Stripe + Trigger PDF Natal depuis landing luxe
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('subscription') === 'success') {
      setCheckinMsg({ type: 'success', text: '🎉 Votre abonnement est maintenant actif !' });
      window.history.replaceState({}, '', '/mon-compte');
    }
    // Auto-trigger PDF natal si arrivée depuis /theme-natal-luxe
    if (params.get('generate') === 'natal') {
      window.history.replaceState({}, '', '/mon-compte');
      // Petit délai pour laisser le profil se charger
      setTimeout(() => {
        try { handlePdfDownload(); } catch (_) { /* silent */ }
      }, 1500);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const chargerProfil = useCallback(async () => {
    if (!token) return;
    try {
      // 1) Profil + balance via /api/auth/me
      const meRes = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfil(meRes.data.user);

      // 2) Streak/fidélité via /api/cercle/streak (silent fail si indisponible)
      try {
        const ritualRes = await axios.get(`${API_URL}/api/cercle/streak`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setFidelite(ritualRes.data);
      } catch { /* streak optional */ }

      // 3) Premium subscription status (silent fail)
      try {
        const subRes = await axios.get(`${API_URL}/api/premium/status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSubscription(subRes.data);
      } catch { /* subscription optional */ }
    } catch (err) {
      console.error('Erreur chargement profil', err);
    }
  }, [token]);

  const chargerTransactions = useCallback(async () => {
    if (!token) return;
    try {
      const { data } = await axios.get(`${API_URL}/api/wallet/transactions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTransactions(data.transactions?.slice(0, 10) || []);
    } catch { /* ignore */ }
  }, [token]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([chargerProfil(), chargerTransactions()]);
      setLoading(false);
    };
    init();
  }, [chargerProfil, chargerTransactions]);

  /* ── Check-in quotidien ── */
  const handleCheckin = async () => {
    if (!token || fidelite?.checked_in_today) return;
    setCheckinLoading(true);
    setCheckinMsg(null);
    try {
      const { data } = await axios.post(`${API_URL}/api/cercle/checkin`, { mood: 'paisible' }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (data.already_checked_in) {
        setCheckinMsg({ type: 'info', text: 'Présence déjà enregistrée aujourd\'hui ✓' });
      } else {
        const msg = data.milestone_bonus > 0
          ? `✨ +${data.credits_earned} crédits ! Palier ${data.streak_count} jours atteint — bonus de ${data.milestone_bonus} crédits !`
          : `✦ +${data.credits_earned} crédit gagné. ${data.streak_count} jour${data.streak_count > 1 ? 's' : ''} consécutif${data.streak_count > 1 ? 's' : ''} !`;
        setCheckinMsg({ type: 'success', text: msg });
      }
      await Promise.all([chargerProfil(), refreshBalance()]);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 403) {
        setCheckinMsg({ type: 'info', text: detail || "L'assiduité quotidienne est réservée aux membres du Cercle." });
      } else {
        setCheckinMsg({ type: 'error', text: 'Une erreur est survenue. Réessayez.' });
      }
    }
    setCheckinLoading(false);
  };

  /* ── Souscription abonnement ── */
  const handleSouscrire = async (productId) => {
    if (!token) { navigate('/connexion'); return; }
    setSubsLoading(true);
    setSubsError(null);
    try {
      const endpoint = productId === 'journal_quotidien'
        ? '/api/subscription/journal-quotidien'
        : '/api/subscription/cercle';
      const { data } = await axios.post(
        `${API_URL}${endpoint}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      setSubsError(err.response?.data?.detail || 'Erreur lors de la souscription.');
    }
    setSubsLoading(false);
  };

  /* ── Déconnexion ── */
  const handleLogout = () => { logout(); navigate('/'); };

  /* ── Signe zodiacal ── */
  const zodiac = profil?.birth_date ? ZODIAC_FROM_DATE(profil.birth_date) : null;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--pa-bg)' }}>
        <div className="text-center">
          <Star className="w-8 h-8 mx-auto mb-4 animate-pulse" strokeWidth={1} style={{ color: 'var(--pa-accent)' }} />
          <p className="text-sm tracking-widest" style={{ color: 'var(--pa-muted)' }}>Chargement de votre espace…</p>
        </div>
      </div>
    );
  }

  /* ─── Code promo ─── */
  const handlePromo = async () => {
    const code = promoCode.trim().toUpperCase();
    if (!code) return;
    setPromoLoading(true); setPromoMsg(null);
    try {
      const res = await axios.post(
        `${API_URL}/api/credits/promo`,
        { code },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const earned = res.data?.credits_earned ?? res.data?.credits ?? 0;
      const msg = earned > 0
        ? `✦ ${earned} crédits ajoutés à votre solde !`
        : res.data?.message || 'Code appliqué avec succès.';
      setPromoMsg({ type: 'success', text: msg });
      setPromoCode('');
      refreshBalance?.();
    } catch (e) {
      const detail = e.response?.data?.detail || 'Code invalide ou déjà utilisé.';
      setPromoMsg({ type: 'error', text: detail });
    }
    setPromoLoading(false);
  };

  /* ─── Télécharger PDF thème natal ─── */
  const handlePdfDownload = async () => {
    if (!profil?.birth_date) {
      alert('Ajoutez votre date de naissance dans votre profil pour générer le PDF natal.');
      return;
    }
    setPdfLoading(true);
    try {
      const res = await axios.post(
        `${API_URL}/api/astrology/v3/natal/pdf`,
        {},
        { headers: { Authorization: `Bearer ${token}` }, responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `theme-natal-${profil?.prenom || 'plume'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Erreur lors de la génération du PDF. Réessayez dans quelques instants.');
    }
    setPdfLoading(false);
  };

  /* ─── Onglets ─── */
  const tabs = [
    { id: 'apercu',       label: 'Aperçu'       },
    { id: 'rapports',     label: 'Mes Rapports' },
    { id: 'credits',      label: 'Crédits'       },
    { id: 'fidelite',     label: 'Assiduité'    },
  ];

  return (
    <div className="min-h-screen relative" style={{ background: 'var(--pa-bg)' }}>
      {/* Overlay animé pendant la génération du PDF Thème Natal (~60s) */}
      {pdfLoading && <SolenaWritingLoader estimatedSeconds={55} />}

      <SEO path="/mon-compte" />
      <PageHero
        image="/images/astrale/image-astrale-8.jpg"
        title={profil?.prenom ? `Bienvenue, ${profil.prenom}` : 'Mon Espace Personnel'}
        subtitle="Votre univers astral personnalisé"
        height="220px"
      />

      {/* Fond décoratif */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 20% 20%, rgba(120,80,200,0.07) 0%, transparent 70%), radial-gradient(ellipse 50% 50% at 80% 80%, rgba(212,175,55,0.05) 0%, transparent 70%)',
          zIndex: 0,
        }}
      />

      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">

          {/* Retour */}
          <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
          </button>

          {/* ── En-tête profil ── */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mb-10">
            {/* Avatar : glyphe zodiacal si date de naissance connue, sinon initiales */}
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center flex-shrink-0 text-xl"
              style={{
                background: 'linear-gradient(135deg, rgba(212,175,55,0.2) 0%, rgba(167,139,250,0.15) 100%)',
                border: '1px solid rgba(212,175,55,0.35)',
                fontFamily: 'Cormorant Garamond, serif',
                color: 'var(--pa-accent)',
                fontWeight: 300,
                boxShadow: '0 4px 20px rgba(212,175,55,0.15)',
              }}
              data-testid="account-avatar"
            >
              {zodiac?.signe ? (
                <LibraryImage type="sign" name={zodiac.signe} size={56} alt={`Signe ${zodiac.signe}`} />
              ) : (
                profil?.email ? profil.email[0].toUpperCase() : <User className="w-6 h-6" strokeWidth={1} />
              )}
            </div>

            <div className="flex-1">
              <p className="section-label mb-1">Mon espace personnel</p>
              <h1
                className="text-2xl md:text-3xl mb-1"
                style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
              >
                {profil?.email?.split('@')[0] || 'Voyageuse céleste'}
                {zodiac && (
                  <span className="ml-3 text-xl" title={zodiac.signe} style={{ color: 'var(--pa-accent)' }}>
                    {zodiac.symbole}
                  </span>
                )}
              </h1>
              {zodiac && (
                <p className="text-xs tracking-widest" style={{ color: 'var(--pa-muted)' }}>
                  {zodiac.signe} · Membre depuis {formatDate(profil?.created_at)}
                </p>
              )}
            </div>

            {/* Bouton déconnexion */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-xs uppercase tracking-widest px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-red-500/10 flex-shrink-0"
              style={{ border: '1px solid rgba(212,175,55,0.2)', color: 'var(--pa-muted)', letterSpacing: '0.08em' }}
              data-testid="logout-btn"
            >
              <LogOut className="w-3.5 h-3.5" strokeWidth={1.5} /> Déconnexion
            </button>
          </div>

          {/* Message flash (check-in / succès abonnement) */}
          {checkinMsg && (
            <div
              className="rounded-xl px-5 py-3 mb-6 text-sm flex items-start gap-3"
              style={{
                background: checkinMsg.type === 'success'
                  ? 'rgba(74,222,128,0.1)'
                  : checkinMsg.type === 'error'
                  ? 'rgba(248,113,113,0.1)'
                  : 'rgba(212,175,55,0.08)',
                border: `1px solid ${checkinMsg.type === 'success' ? 'rgba(74,222,128,0.3)' : checkinMsg.type === 'error' ? 'rgba(248,113,113,0.3)' : 'rgba(212,175,55,0.2)'}`,
                color: checkinMsg.type === 'success' ? '#4ADE80' : checkinMsg.type === 'error' ? '#F87171' : 'var(--pa-accent)',
              }}
              data-testid="flash-msg"
            >
              <span>{checkinMsg.text}</span>
              <button onClick={() => setCheckinMsg(null)} className="ml-auto text-xs opacity-60 hover:opacity-100">✕</button>
            </div>
          )}
          {subsError && (
            <div
              className="rounded-xl px-5 py-3 mb-6 text-sm"
              style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.25)', color: '#F87171' }}
            >
              {subsError}
            </div>
          )}

          {/* ── Bandeau solde crédits ── */}
          <Link
            to="/acheter-credits"
            className="flex items-center justify-between gap-4 rounded-2xl px-6 py-4 mb-8 group transition-all duration-300 hover:border-[rgba(212,175,55,0.45)]"
            style={{
              background: 'linear-gradient(135deg, rgba(212,175,55,0.1) 0%, rgba(212,175,55,0.04) 100%)',
              border: '1px solid rgba(212,175,55,0.25)',
            }}
            data-testid="credit-banner"
          >
            <div className="flex items-center gap-3">
              <Coins className="w-6 h-6" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
              <div>
                <p className="text-xs tracking-widest uppercase mb-0.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>
                  Solde de crédits
                </p>
                <p className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
                  {creditBalance} <span className="text-base" style={{ color: 'var(--pa-accent)' }}>crédits</span>
                </p>
              </div>
            </div>
            <div
              className="flex items-center gap-1.5 text-xs uppercase tracking-widest px-4 py-2 rounded-full transition-all duration-300 group-hover:bg-[rgba(212,175,55,0.15)]"
              style={{ border: '1px solid rgba(212,175,55,0.35)', color: 'var(--pa-accent)', letterSpacing: '0.08em' }}
            >
              <Gift className="w-3.5 h-3.5" strokeWidth={1.5} /> Recharger
            </div>
          </Link>

          {/* ── Navigation par onglets ── */}
          <div className="flex items-center gap-1 mb-8 overflow-x-auto pb-1" style={{ borderBottom: '1px solid rgba(212,175,55,0.1)' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="flex-shrink-0 text-xs uppercase tracking-widest px-4 py-2.5 rounded-t transition-all duration-200"
                style={{
                  letterSpacing: '0.1em',
                  color: activeTab === tab.id ? 'var(--pa-accent)' : 'var(--pa-muted)',
                  borderBottom: activeTab === tab.id ? '1px solid var(--pa-accent)' : '1px solid transparent',
                  background: activeTab === tab.id ? 'rgba(212,175,55,0.06)' : 'transparent',
                  marginBottom: '-1px',
                }}
                data-testid={`tab-${tab.id}`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* ══════════════════════════════════════════════════
              ONGLET APERÇU
          ══════════════════════════════════════════════════ */}
          {activeTab === 'apercu' && (
            <div className="space-y-6">
              {/* Informations personnelles */}
              <div
                className="rounded-2xl p-6 md:p-8"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
                data-testid="profil-card"
              >
                <h2
                  className="text-base mb-6 flex items-center justify-between gap-3"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                >
                  <span className="flex items-center gap-3">
                    <User className="w-4 h-4" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
                    Informations personnelles
                  </span>
                  <button
                    onClick={() => setNatalModalOpen(true)}
                    data-testid="edit-natal-btn"
                    style={{
                      fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase',
                      padding: '6px 12px', borderRadius: 999,
                      border: '1px solid rgba(212,175,55,0.4)',
                      color: 'var(--pa-accent)', background: 'transparent',
                      cursor: 'pointer', fontFamily: 'Cinzel, serif', fontWeight: 500,
                    }}
                  >
                    Modifier
                  </button>
                </h2>

                <div className="space-y-4">
                  {/* Email */}
                  <div className="flex items-start gap-4">
                    <Mail className="w-4 h-4 mt-0.5 flex-shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                    <div>
                      <p className="text-[10px] tracking-widest uppercase mb-0.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Adresse e-mail</p>
                      <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{profil?.email || '—'}</p>
                    </div>
                  </div>

                  {/* Date de naissance */}
                  <div className="flex items-start gap-4">
                    <Calendar className="w-4 h-4 mt-0.5 flex-shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                    <div>
                      <p className="text-[10px] tracking-widest uppercase mb-0.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Date de naissance</p>
                      <p className="text-sm" style={{ color: 'var(--pa-body)' }}>
                        {profil?.birth_date ? formatDate(profil.birth_date) : '—'}
                        {zodiac && (
                          <span className="ml-2 text-xs" style={{ color: 'var(--pa-accent)' }}>
                            {zodiac.symbole} {zodiac.signe}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>

                  {/* Heure de naissance */}
                  {profil?.birth_time && (
                    <div className="flex items-start gap-4">
                      <Star className="w-4 h-4 mt-0.5 flex-shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                      <div>
                        <p className="text-[10px] tracking-widest uppercase mb-0.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Heure de naissance</p>
                        <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{profil.birth_time}</p>
                      </div>
                    </div>
                  )}

                  {/* Lieu de naissance */}
                  {(profil?.birth_place || profil?.birth_country) && (
                    <div className="flex items-start gap-4">
                      <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                      <div>
                        <p className="text-[10px] tracking-widest uppercase mb-0.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Lieu de naissance</p>
                        <p className="text-sm" style={{ color: 'var(--pa-body)' }}>
                          {[profil.birth_place, profil.birth_country].filter(Boolean).join(', ')}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Raccourcis vers les services */}
              <div
                className="rounded-2xl p-6"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
              >
                <h2
                  className="text-base mb-5 flex items-center gap-3"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                >
                  <Sparkles className="w-4 h-4" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
                  Accès rapide
                </h2>

                <div className="grid grid-cols-2 gap-3">
                  {[
                    { to: '/quotidien',              label: 'Guidance du jour',      icon: '☀️' },
                    { to: '/tarot-oui-non',          label: 'Tarot Oui / Non',       icon: '🃏' },
                    { to: '/astrologie-vedique',     label: 'Astrologie Védique',    icon: '🕉️' },
                    { to: '/acheter-credits',        label: 'Acheter des crédits',   icon: '✦' },
                  ].map(({ to, label, icon }) => (
                    <Link
                      key={to}
                      to={to}
                      className="flex items-center gap-3 rounded-xl px-4 py-3 transition-all duration-200 hover:border-[rgba(212,175,55,0.3)]"
                      style={{ background: 'rgba(212,175,55,0.04)', border: '1px solid rgba(212,175,55,0.12)' }}
                    >
                      <span className="text-base">{icon}</span>
                      <span className="text-xs" style={{ color: 'var(--pa-body)' }}>{label}</span>
                      <ChevronRight className="w-3 h-3 ml-auto" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                    </Link>
                  ))}
                </div>
                <button
                  onClick={() => setActiveTab('rapports')}
                  className="w-full mt-1 rounded-xl px-4 py-3 flex items-center gap-3 transition-all duration-200 hover:border-[rgba(167,139,250,0.5)]"
                  style={{ background: 'rgba(167,139,250,0.12)', border: '1px solid rgba(167,139,250,0.35)' }}
                  data-testid="quick-open-rapports-pdf"
                >
                  <span className="text-base">✶</span>
                  <span className="text-xs" style={{ color: 'var(--pa-body)' }}>
                    {profil?.birth_date ? 'Télécharger mon thème natal PDF' : 'Compléter mes infos pour le PDF natal'}
                  </span>
                  <ChevronRight className="w-3 h-3 ml-auto" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                </button>
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════════
              ONGLET MES RAPPORTS
          ══════════════════════════════════════════════════ */}
          {activeTab === 'rapports' && (
            <div className="space-y-4" data-testid="rapports-tab">
              <div className="mb-2">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <h2
                    className="text-2xl"
                    style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                  >
                    Vos rapports astrologiques
                  </h2>
                  <button
                    onClick={handlePdfDownload}
                    disabled={pdfLoading || !profil?.birth_date}
                    data-testid="btn-pdf-natal"
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      padding: '8px 16px', borderRadius: 999, flexShrink: 0,
                      background: profil?.birth_date ? 'rgba(167,139,250,0.15)' : 'rgba(148,163,184,0.15)',
                      border: profil?.birth_date ? '1px solid rgba(167,139,250,0.4)' : '1px solid rgba(148,163,184,0.35)',
                      color: profil?.birth_date ? '#A78BFA' : '#94A3B8',
                      fontSize: 11,
                      letterSpacing: '0.08em', textTransform: 'uppercase',
                      cursor: (pdfLoading || !profil?.birth_date) ? 'not-allowed' : 'pointer',
                    }}
                  >
                    {!profil?.birth_date ? '✶ Données incomplètes' : (pdfLoading ? '⏳ Génération…' : '✶ Télécharger PDF')}
                  </button>
                </div>
                <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                  Chaque rapport est calcule avec les ephemerides Swiss Ephemeris.
                  Débloquez vos lectures avec vos crédits
                </p>
                {!profil?.birth_date && (
                  <p className="text-xs mt-2" style={{ color: '#94A3B8' }}>
                    Pour generer votre PDF natal, renseignez au minimum votre date de naissance dans votre profil.
                  </p>
                )}
              </div>

              {[
                { to: '/karma-destin', title: 'Karma & Destin', subtitle: 'Lecture karmique avec Noeud Nord et mission de vie', price: 20, icon: '☉', accent: '#D4AF37' },
                { to: '/compatibilite', title: 'Compatibilite (4 liens)', subtitle: 'Amour · Amitie · Famille · Travail', price: 20, icon: '♡', accent: '#F472B6' },
                { to: '/revolution-solaire', title: 'Revolution Solaire', subtitle: "Themes de votre prochaine annee, votre rituel d'anniversaire", price: 20, icon: '✦', accent: '#FDE68A' },
                { to: '/love-languages', title: "Langages d'Amour", subtitle: 'Votre signature affective selon Venus, Mars et Lune', price: 10, icon: '♥', accent: '#FB7185' },
                { to: '/formulaire', title: 'Thème Natal complet', subtitle: 'Chart wheel + interprétations psychologiques (28 sections)', price: 20, icon: '✶', accent: '#A78BFA' },
                { to: '/consultation', title: 'Chat avec Plume', subtitle: 'Conversation astrologique avec votre theme natal embarque', price: 3, perUse: true, icon: '✺', accent: '#7DD3FC' },
              ].map(({ to, title, subtitle, price, perUse, icon, accent }) => (
                <Link
                  key={to}
                  to={to}
                  data-testid={`rapport-card-${to.replace('/', '')}`}
                  className="block rounded-2xl p-5 md:p-6 transition-all duration-300 hover:-translate-y-0.5"
                  style={{
                    background: 'var(--pa-surface)',
                    border: '1px solid var(--pa-divider)',
                    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03)',
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 text-xl"
                      style={{
                        background: `linear-gradient(135deg, ${accent}22 0%, ${accent}10 100%)`,
                        border: `1px solid ${accent}55`,
                        color: accent,
                        fontFamily: 'Cormorant Garamond, serif',
                      }}
                    >
                      {icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3
                        className="text-base md:text-lg mb-0.5"
                        style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                      >
                        {title}
                      </h3>
                      <p className="text-xs leading-relaxed" style={{ color: 'var(--pa-muted)' }}>
                        {subtitle}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1 flex-shrink-0">
                      {profil?.premium_status !== 'active' && (
                        <span className="text-base" style={{ color: 'var(--pa-accent)', fontFamily: 'Cormorant Garamond, serif' }}>
                          {price} cr
                        </span>
                      )}
                      {perUse && !profil?.premium_status === 'active' && (
                        <span className="text-[10px]" style={{ color: 'var(--pa-muted)' }}>/ question</span>
                      )}
                      <ChevronRight className="w-3.5 h-3.5" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                    </div>
                  </div>
                </Link>
              ))}

              {profil?.premium_status !== 'active' && (
                <Link
                  to="/premium"
                  className="block rounded-2xl p-5 md:p-6 text-center transition-all duration-300 hover:-translate-y-0.5"
                  data-testid="rapports-premium-cta"
                  style={{
                    background: 'linear-gradient(135deg, rgba(212,175,55,0.1) 0%, rgba(167,139,250,0.08) 100%)',
                    border: '1px solid rgba(212,175,55,0.35)',
                  }}
                >
                  <Crown className="w-6 h-6 mx-auto mb-2" strokeWidth={1.3} style={{ color: 'var(--pa-accent)' }} />
                  <p className="text-base mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
                    Acces illimite a tous vos rapports
                  </p>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    Decouvrez Premium · 7 jours d'essai offerts
                  </p>
                </Link>
              )}
            </div>
          )}

          {/* ══════════════════════════════════════════════════
              ONGLET ABONNEMENT
          ══════════════════════════════════════════════════ */}
          {activeTab === 'abonnement' && (
            <AbonnementCard
              subscription={subscription}
              onSouscrire={handleSouscrire}
              loading={subsLoading}
            />
          )}

          {/* ══════════════════════════════════════════════════
              ONGLET CRÉDITS
          ══════════════════════════════════════════════════ */}
          {activeTab === 'credits' && (
            <div className="space-y-6">
              {/* Solde + recharge */}
              <div
                className="rounded-2xl p-6 md:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
              >
                <div className="flex items-center gap-4">
                  <Coins className="w-8 h-8" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
                  <div>
                    <p className="text-xs tracking-widest uppercase mb-1" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Solde actuel</p>
                    <p className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
                      {creditBalance} <span className="text-lg" style={{ color: 'var(--pa-accent)' }}>crédits</span>
                    </p>
                  </div>
                </div>
                <Link
                  to="/acheter-credits"
                  className="flex items-center gap-2 text-xs uppercase tracking-widest px-5 py-2.5 rounded-full transition-all duration-300"
                  style={{
                    background: 'rgba(212,175,55,0.12)',
                    border: '1px solid rgba(212,175,55,0.4)',
                    color: 'var(--pa-accent)',
                    letterSpacing: '0.08em',
                  }}
                  data-testid="btn-recharger"
                >
                  <Gift className="w-3.5 h-3.5" strokeWidth={1.5} /> Recharger
                </Link>
              </div>

              {/* Historique */}
              <div
                className="rounded-2xl p-6"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
                data-testid="historique-transactions"
              >
                <h2
                  className="text-base mb-5"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                >
                  Historique des mouvements
                </h2>

                {transactions.length === 0 ? (
                  <p className="text-sm text-center py-6" style={{ color: 'var(--pa-muted)' }}>
                    Aucun mouvement de crédits pour le moment.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {transactions.map((tx, i) => (
                      <div
                        key={tx.id || i}
                        className="flex items-center justify-between px-4 py-3 rounded-xl"
                        style={{ background: 'rgba(212,175,55,0.03)', border: '1px solid rgba(212,175,55,0.08)' }}
                      >
                        <div>
                          <p className="text-xs" style={{ color: 'var(--pa-body)' }}>
                            {tx.description || tx.type || 'Mouvement de crédits'}
                          </p>
                          <p className="text-[10px] mt-0.5" style={{ color: 'var(--pa-muted)' }}>
                            {formatDate(tx.created_at)}
                          </p>
                        </div>
                        <span
                          className="text-sm font-medium"
                          style={{ color: tx.amount > 0 ? '#4ADE80' : '#F87171' }}
                        >
                          {tx.amount > 0 ? '+' : ''}{tx.amount} crédits
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Code promo */}
              <div
                className="rounded-2xl p-6"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
                data-testid="promo-section"
              >
                <h2 className="text-base mb-1 flex items-center gap-2"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  <Gift className="w-4 h-4" strokeWidth={1.5} style={{ color: 'var(--pa-accent)' }} />
                  Code de réduction
                </h2>
                <p className="text-xs mb-4" style={{ color: 'var(--pa-muted)' }}>
                  Entrez un code promo pour obtenir des crédits ou débloquer un accès.
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={promoCode}
                    onChange={e => { setPromoCode(e.target.value.toUpperCase()); setPromoMsg(null); }}
                    onKeyDown={e => e.key === 'Enter' && handlePromo()}
                    placeholder="VOTRECODERÉDUC"
                    maxLength={32}
                    style={{
                      flex: 1, background: 'rgba(255,255,255,0.04)',
                      border: '1px solid rgba(212,180,106,0.25)',
                      borderRadius: 999, padding: '10px 16px',
                      color: 'var(--pa-heading)', fontSize: 13,
                      letterSpacing: '0.08em', outline: 'none',
                    }}
                    data-testid="promo-input"
                  />
                  <button
                    onClick={handlePromo}
                    disabled={promoLoading || !promoCode.trim()}
                    style={{
                      padding: '10px 20px', borderRadius: 999,
                      background: 'rgba(197,160,89,0.15)',
                      border: '1px solid rgba(197,160,89,0.4)',
                      color: 'var(--pa-accent)', fontSize: 12,
                      letterSpacing: '0.08em', textTransform: 'uppercase',
                      cursor: promoLoading ? 'wait' : 'pointer',
                      opacity: promoCode.trim() ? 1 : 0.5, whiteSpace: 'nowrap',
                    }}
                    data-testid="promo-submit"
                  >
                    {promoLoading ? '…' : 'Appliquer'}
                  </button>
                </div>
                {promoMsg && (
                  <p className="mt-2 text-xs"
                    style={{ color: promoMsg.type === 'success' ? '#4ADE80' : '#F87171' }}
                    data-testid="promo-msg">
                    {promoMsg.text}
                  </p>
                )}
              </div>

              {/* Info sécurité paiement */}
              <div
                className="rounded-xl px-5 py-4 flex items-center gap-3"
                style={{ background: 'rgba(212,175,55,0.04)', border: '1px solid rgba(212,175,55,0.12)' }}
              >
                <Shield className="w-4 h-4 flex-shrink-0" strokeWidth={1.5} style={{ color: 'var(--pa-muted)' }} />
                <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                  Paiements sécurisés par <strong style={{ color: 'var(--pa-body)' }}>Stripe</strong>. Vos données bancaires ne sont jamais stockées sur nos serveurs.
                </p>
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════════
              ONGLET ASSIDUITÉ
          ══════════════════════════════════════════════════ */}
          {activeTab === 'fidelite' && (
            <div className="space-y-6">
              <FideliteCard
                fidelite={fidelite}
                onCheckin={handleCheckin}
                checkinLoading={checkinLoading}
              />

              {/* Explications des paliers */}
              <div
                className="rounded-2xl p-6"
                style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}
              >
                <h2
                  className="text-base mb-5"
                  style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}
                >
                  Paliers et récompenses
                </h2>
                <div className="space-y-3">
                  {[
                    { jours: 7,   bonus: 10,  label: 'Une semaine de constance' },
                    { jours: 14,  bonus: 20,  label: 'Deux semaines d\'alignement' },
                    { jours: 30,  bonus: 30, label: 'Un mois d\'assiduité' },
                    { jours: 60,  bonus: 45, label: 'Deux mois de fidélité' },
                    { jours: 100, bonus: 125, label: 'Cent jours de présence céleste' },
                  ].map(({ jours, bonus, label }) => {
                    const atteint = (fidelite?.streak_count ?? 0) >= jours;
                    return (
                      <div
                        key={jours}
                        className="flex items-center gap-4 rounded-xl px-4 py-3"
                        style={{
                          background: atteint ? 'rgba(74,222,128,0.06)' : 'rgba(212,175,55,0.03)',
                          border: `1px solid ${atteint ? 'rgba(74,222,128,0.2)' : 'rgba(212,175,55,0.1)'}`,
                        }}
                      >
                        <div
                          className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs"
                          style={{
                            background: atteint ? 'rgba(74,222,128,0.15)' : 'rgba(212,175,55,0.08)',
                            color: atteint ? '#4ADE80' : 'var(--pa-accent)',
                          }}
                        >
                          {atteint ? <Check className="w-4 h-4" strokeWidth={2} /> : jours}
                        </div>
                        <div className="flex-1">
                          <p className="text-xs" style={{ color: 'var(--pa-body)' }}>{label}</p>
                          <p className="text-[10px] mt-0.5" style={{ color: 'var(--pa-muted)' }}>{jours} jours consécutifs</p>
                        </div>
                        <span
                          className="text-xs font-medium flex-shrink-0"
                          style={{ color: atteint ? '#4ADE80' : 'var(--pa-accent)' }}
                        >
                          +{bonus} crédits
                        </span>
                      </div>
                    );
                  })}
                </div>
                <p className="text-xs mt-5" style={{ color: 'var(--pa-muted)' }}>
                  ✦ Chaque connexion quotidienne vous rapporte également <strong style={{ color: 'var(--pa-body)' }}>1 crédit</strong> automatiquement.
                </p>
              </div>
            </div>
          )}


          {/* ── Nos offres ── (déplacé en bas de page) */}
          {/* Bundle Découverte Soléna — offre irrésistible post-inscription/connexion */}
          <div className="mb-6">
            <BundleCard testId="mon-compte-bundle" dense />
          </div>

          {/* Teaser Cercle Soléna — LTV mensuelle */}
          <Link
            to="/cercle-solena"
            className="block plume-glass p-4 mb-10 hover:opacity-90 transition-opacity"
            data-testid="mon-compte-cercle-solena-teaser"
            style={{ border: '1px solid rgba(212,175,55,0.25)' }}
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <div style={{ fontFamily: 'Cinzel, serif', fontSize: 11, color: '#D4AF37', letterSpacing: '0.24em', marginBottom: 4 }}>
                  ✦ Cercle Soléna · 14,90 €/mois ✦
                </div>
                <div className="text-sm" style={{ color: '#F5EEE0', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                  30 crédits/mois · Communauté privée · -10% sur les PDF
                </div>
              </div>
              <div className="text-xs shrink-0" style={{ color: '#D4AF37', letterSpacing: '0.15em' }}>
                DÉCOUVRIR →
              </div>
            </div>
          </Link>

          {/* Séparateur bas de page */}
          <div className="mt-16 mb-6" style={{ borderTop: '1px solid rgba(212,175,55,0.1)' }} />
          <p className="text-center text-xs" style={{ color: 'var(--pa-muted)' }}>
            Plume Astrale · <Link to="/charte-de-confiance" className="hover:opacity-80 transition-opacity" style={{ color: 'var(--pa-muted)' }}>Charte de confiance</Link>
          </p>

        </div>
      </div>

      {/* Natal data edit modal */}
      <NatalDataModal
        open={natalModalOpen}
        onClose={() => setNatalModalOpen(false)}
        onSuccess={chargerProfil}
      />
    </div>
  );
};

export default MonCompte;
