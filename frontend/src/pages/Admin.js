import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import {
  Users, Euro, TrendingUp, MessageCircle, Coins, ShoppingCart,
  Loader2, RefreshCw, Search, Tag, Activity, Sparkles, Plus, Power, Trash2, Crown,
} from 'lucide-react';
import SEO from '@/components/SEO';
import AdminThemeNatalFixer from '@/components/AdminThemeNatalFixer';
import AdminLectureComplete from '@/components/AdminLectureComplete';

const API = process.env.REACT_APP_BACKEND_URL;

const Card = ({ icon: Icon, label, value, sub, accent = '#D4AF37' }) => (
  <div className="rounded-2xl p-5" style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(212,175,55,0.18)',
    backdropFilter: 'blur(12px)',
  }} data-testid={`kpi-card-${String(label).replace(/\s+/g, '-')}`}>
    <div className="flex items-center gap-2 mb-3">
      <Icon className="w-4 h-4" style={{ color: accent }} strokeWidth={1.5} />
      <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>{label}</span>
    </div>
    <div className="text-3xl mb-1" style={{ fontFamily: 'Cormorant Garamond, serif', color: accent, fontWeight: 400 }}>{value}</div>
    {sub && <div className="text-xs" style={{ color: 'var(--pa-muted)' }}>{sub}</div>}
  </div>
);

const Tab = ({ label, active, onClick, count }) => (
  <button onClick={onClick}
    className="px-4 py-2 text-xs uppercase tracking-widest rounded-full transition-all"
    style={{
      border: '1px solid',
      borderColor: active ? '#D4AF37' : 'rgba(212,175,55,0.25)',
      color: active ? '#111625' : '#D4AF37',
      background: active ? '#D4AF37' : 'transparent',
      letterSpacing: '0.1em',
    }}
    data-testid={`admin-tab-${label.toLowerCase().replace(/\s+/g, '-')}`}>
    {label}{count !== undefined && ` (${count})`}
  </button>
);

const Table = ({ columns, rows, emptyMessage }) => (
  <div className="rounded-xl overflow-hidden" style={{ border: '1px solid rgba(212,175,55,0.15)' }}>
    <div className="overflow-x-auto">
      <table className="w-full text-sm" style={{ color: 'var(--pa-body)' }}>
        <thead style={{ background: 'rgba(212,175,55,0.06)' }}>
          <tr>
            {columns.map(c => (
              <th key={c.key} className="text-left px-4 py-3 text-[10px] uppercase tracking-widest"
                style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={columns.length} className="text-center py-8 text-xs" style={{ color: 'var(--pa-muted)' }}>
              {emptyMessage || 'Aucune donnee'}
            </td></tr>
          ) : rows.map((r, i) => (
            <tr key={i} style={{ borderTop: '1px solid rgba(212,175,55,0.06)' }}>
              {columns.map(c => (
                <td key={c.key} className="px-4 py-3 text-xs" style={{ color: 'var(--pa-body)' }}>
                  {c.render ? c.render(r) : (r[c.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const fmtDate = (iso) => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });
  } catch { return iso; }
};

const fmtEur = (n) => `${Number(n || 0).toFixed(2).replace('.', ',')} €`;

export default function Admin() {
  const { user, token, loading: authLoading } = useAuth();
  const [tab, setTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [payments, setPayments] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [promoCodes, setPromoCodes] = useState([]);
  const [leads, setLeads] = useState([]);
  const [leadsTotal, setLeadsTotal] = useState(0);
  const [pdfsSent, setPdfsSent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  const loadStats = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/stats`, { headers: { Authorization: `Bearer ${token}` } });
      setStats(r.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadUsers = useCallback(async (q = '') => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/users?page=1&page_size=100${q ? `&search=${encodeURIComponent(q)}` : ''}`, { headers: { Authorization: `Bearer ${token}` } });
      setUsers(r.data.users || []);
      setUsersTotal(r.data.total || 0);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadPayments = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/payments?page=1&page_size=100`, { headers: { Authorization: `Bearer ${token}` } });
      setPayments(r.data.payments || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/transactions?page=1&page_size=200`, { headers: { Authorization: `Bearer ${token}` } });
      setTransactions(r.data.transactions || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadPromo = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/promo-codes`, { headers: { Authorization: `Bearer ${token}` } });
      setPromoCodes(r.data.codes || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadLeads = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/leads?page=1&page_size=200`, { headers: { Authorization: `Bearer ${token}` } });
      setLeads(r.data.leads || []);
      setLeadsTotal(r.data.total || 0);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const loadPdfsSent = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/api/admin/pdfs-sent?page=1&page_size=200`, { headers: { Authorization: `Bearer ${token}` } });
      setPdfsSent(r.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => {
    if (!token || !user?.is_admin) return;
    if (tab === 'overview') loadStats();
    else if (tab === 'users') loadUsers(search);
    else if (tab === 'payments') loadPayments();
    else if (tab === 'transactions') loadTransactions();
    else if (tab === 'leads') loadLeads();
    else if (tab === 'promo') loadPromo();
    else if (tab === 'pdfs-sent') loadPdfsSent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, token, user?.is_admin]);

  const refresh = () => {
    if (tab === 'overview') loadStats();
    else if (tab === 'users') loadUsers(search);
    else if (tab === 'payments') loadPayments();
    else if (tab === 'transactions') loadTransactions();
    else if (tab === 'leads') loadLeads();
    else if (tab === 'pdfs-sent') loadPdfsSent();
    else loadPromo();
  };

  if (authLoading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }} /></div>;
  if (!user) return <Navigate to="/connexion" replace />;
  if (!user.is_admin) return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-md p-8 rounded-2xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)' }} data-testid="admin-access-denied">
        <h1 className="text-2xl mb-3" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>Acces refuse</h1>
        <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>Cette page est reservee aux administrateurs.</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" data-testid="admin-dashboard">
      <SEO path="/admin" />
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <Sparkles className="w-5 h-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
              <h1 className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Tableau de bord
              </h1>
            </div>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              Pilotage Plume Astrale — {user.email}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <a href="/bibliotheque"
              className="flex items-center gap-2 px-4 py-2 text-xs uppercase tracking-widest rounded-full"
              style={{ border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', letterSpacing: '0.1em' }}
              data-testid="admin-biblio-link">
              <Sparkles className="w-3.5 h-3.5" /> Bibliothèque visuelle
            </a>
            <button onClick={refresh}
              className="flex items-center gap-2 px-4 py-2 text-xs uppercase tracking-widest rounded-full"
              style={{ border: '1px solid rgba(212,175,55,0.4)', color: '#D4AF37', letterSpacing: '0.1em' }}
              data-testid="admin-refresh-btn">
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-8">
          <Tab label="Vue d'ensemble" active={tab === 'overview'} onClick={() => setTab('overview')} />
          <Tab label="Utilisateurs" active={tab === 'users'} onClick={() => setTab('users')} count={stats?.users?.total} />
          <Tab label="Paiements" active={tab === 'payments'} onClick={() => setTab('payments')} count={stats?.revenue?.total_paid_count} />
          <Tab label="Transactions" active={tab === 'transactions'} onClick={() => setTab('transactions')} />
          <Tab label="Leads" active={tab === 'leads'} onClick={() => setTab('leads')} count={tab === 'leads' ? leadsTotal : undefined} />
          <Tab label="Codes promo" active={tab === 'promo'} onClick={() => setTab('promo')} />
          <Tab label="PDFs envoyés" active={tab === 'pdfs-sent'} onClick={() => setTab('pdfs-sent')} count={pdfsSent?.total_with_supabase_url} />
          <Tab label="Fix Thème Natal" active={tab === 'fix-natal'} onClick={() => setTab('fix-natal')} />
          <Tab label="Lecture Complète" active={tab === 'lecture-complete'} onClick={() => setTab('lecture-complete')} />
        </div>

        {tab === 'lecture-complete' && (
          <AdminLectureComplete token={token} />
        )}

        {tab === 'fix-natal' && (
          <AdminThemeNatalFixer token={token} />
        )}

        {tab === 'overview' && stats && (
          <>
            <h2 className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Utilisateurs</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <Card icon={Users} label="Total" value={stats.users.total} sub={`+${stats.users.signups_today} aujourd'hui`} />
              <Card icon={TrendingUp} label="7 jours" value={`+${stats.users.signups_7d}`} sub="nouvelles inscriptions" />
              <Card icon={ShoppingCart} label="Payants" value={stats.users.paying_users} sub={`${stats.users.conversion_rate_pct}% conversion`} />
              <Card icon={Activity} label="30 jours" value={`+${stats.users.signups_30d}`} sub="inscriptions" />
            </div>

            <h2 className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Revenus</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <Card icon={Euro} label="Total" value={fmtEur(stats.revenue.total_eur)} sub={`${stats.revenue.total_paid_count} paiements`} />
              <Card icon={Euro} label="7 jours" value={fmtEur(stats.revenue.last_7d_eur)} />
              <Card icon={Euro} label="30 jours" value={fmtEur(stats.revenue.last_30d_eur)} />
              <Card icon={ShoppingCart} label="En attente" value={stats.revenue.pending_count} sub="sessions abandonnees" accent="#a78bfa" />
            </div>

            <h2 className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Engagement</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              <Card icon={Coins} label="Credits en circulation" value={stats.engagement.credits_in_wallets} />
              <Card icon={MessageCircle} label="Messages chat" value={stats.engagement.chat_messages_sent} sub="depuis le debut" />
              <Card icon={Tag} label="Codes promo utilises" value={stats.engagement.promo_redemptions} />
            </div>
          </>
        )}

        {tab === 'users' && (
          <>
            <div className="flex gap-2 mb-4 max-w-sm">
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-3" style={{ color: 'var(--pa-muted)' }} />
                <input type="text" value={search} onChange={e => setSearch(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && loadUsers(search)}
                  placeholder="Rechercher par email..."
                  className="w-full pl-10 pr-4 py-2 bg-transparent rounded-full text-sm outline-none"
                  style={{ border: '1px solid rgba(212,175,55,0.25)', color: 'var(--pa-body)' }}
                  data-testid="admin-user-search" />
              </div>
              <button onClick={() => loadUsers(search)}
                className="px-4 py-2 text-xs uppercase tracking-widest rounded-full"
                style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', letterSpacing: '0.1em', fontWeight: 600 }}>
                Chercher
              </button>
            </div>
            <p className="text-xs mb-3" style={{ color: 'var(--pa-muted)' }}>{usersTotal} utilisateurs au total</p>
            <Table
              columns={[
                { key: 'email', label: 'Email' },
                { key: 'prenom', label: 'Prenom' },
                { key: 'created_at', label: 'Inscrit le', render: r => fmtDate(r.created_at) },
                { key: 'credit_balance', label: 'Solde', render: r => <span style={{ color: '#D4AF37', fontWeight: 600 }}>{r.credit_balance} cr</span> },
                { key: 'premium_status', label: 'Premium', render: r => (
                  r.premium_status === 'active'
                    ? <span style={{ color: '#FDE68A', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <Crown className="w-3 h-3" strokeWidth={1.5} />
                        {r.premium_until ? new Date(r.premium_until).toLocaleDateString('fr-FR') : 'Actif'}
                      </span>
                    : <span style={{ color: 'var(--pa-muted)' }}>—</span>
                ) },
                { key: 'total_spent_eur', label: 'Depense', render: r => fmtEur(r.total_spent_eur) },
                { key: 'is_admin', label: 'Admin', render: r => r.is_admin ? <span style={{ color: '#7CB88A' }}>Oui</span> : '—' },
                { key: 'actions', label: 'Actions', render: r => (
                  <UserActions
                    user={r}
                    token={token}
                    onChange={() => loadUsers(search)}
                  />
                ) },
              ]}
              rows={users}
            />
          </>
        )}

        {tab === 'payments' && (
          <Table
            columns={[
              { key: 'created_at', label: 'Date', render: r => fmtDate(r.created_at) },
              { key: 'user_email', label: 'Utilisateur' },
              { key: 'pack_id', label: 'Pack' },
              { key: 'amount', label: 'Montant', render: r => fmtEur(r.amount) },
              { key: 'credits', label: 'Credits' },
              { key: 'payment_status', label: 'Statut', render: r => (
                <span style={{
                  color: r.payment_status === 'paid' ? '#7CB88A' : r.payment_status === 'unpaid' ? '#fca5a5' : 'var(--pa-muted)',
                  fontWeight: 600,
                }}>{r.payment_status}</span>
              ) },
              { key: 'credits_granted', label: 'Credite', render: r => r.credits_granted ? '✓' : '—' },
            ]}
            rows={payments}
            emptyMessage="Aucun paiement encore"
          />
        )}

        {tab === 'transactions' && (
          <Table
            columns={[
              { key: 'created_at', label: 'Date', render: r => fmtDate(r.created_at) },
              { key: 'user_id', label: 'User ID', render: r => (r.user_id || '').slice(0, 8) + '...' },
              { key: 'tx_type', label: 'Type' },
              { key: 'amount', label: 'Montant', render: r => (
                <span style={{ color: r.amount > 0 ? '#7CB88A' : '#fca5a5', fontWeight: 600 }}>
                  {r.amount > 0 ? '+' : ''}{r.amount} cr
                </span>
              ) },
              { key: 'description', label: 'Description' },
            ]}
            rows={transactions}
          />
        )}

        {tab === 'leads' && (
          <Table
            columns={[
              { key: 'created_at', label: 'Capturé le', render: r => fmtDate(r.created_at) },
              { key: 'email', label: 'Email' },
              { key: 'first_name', label: 'Prénom', render: r => r.first_name || '—' },
              { key: 'source', label: 'Source', render: r => (
                <span className="px-2 py-1 rounded-full text-[10px] uppercase" style={{
                  background: r.source === 'extrait_karmique' ? 'rgba(212,175,55,0.15)' : 'rgba(144,137,181,0.15)',
                  color: r.source === 'extrait_karmique' ? '#D4AF37' : '#9089B5',
                  letterSpacing: '0.08em',
                }}>{r.source || 'oracle'}</span>
              ) },
              { key: 'email_sequence_step', label: 'Séquence', render: r => (
                r.unsubscribed_at ? <span style={{ color: '#fca5a5' }}>Désinscrit</span>
                : r.source !== 'extrait_karmique' ? <span style={{ color: '#9089B5' }}>—</span>
                : <span style={{ color: '#7CB88A' }}>{['En attente J+2', 'J+2 envoyé', 'Séquence terminée'][r.email_sequence_step || 0] || '—'}</span>
              ) },
              { key: 'last_email_sent_at', label: 'Dernier email', render: r => r.last_email_sent_at ? fmtDate(r.last_email_sent_at) : '—' },
            ]}
            rows={leads}
            emptyMessage="Aucun lead capturé pour le moment."
          />
        )}

        {tab === 'promo' && (
          <PromoSection token={token} promoCodes={promoCodes} reload={loadPromo} />
        )}

        {tab === 'pdfs-sent' && (
          <PdfsSentSection data={pdfsSent} loading={loading} reload={loadPdfsSent} />
        )}

      </div>
    </div>
  );
}

// ═══════ PDFs Sent Section (Supabase Storage only) ═══════
function PdfsSentSection({ data, loading, reload }) {
  const items = data?.items || [];
  const total = data?.total_with_supabase_url || 0;
  const totalCompleted = data?.total_completed || 0;
  const [productFilter, setProductFilter] = React.useState('');

  const filteredItems = productFilter
    ? items.filter((i) => i.product === productFilter)
    : items;

  const uniqueProducts = [...new Set(items.map((i) => i.product))].sort();

  const fmtDate = (iso) => {
    if (!iso) return '—';
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }) +
        ' · ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  };

  const productLabel = (p) => ({
    'kabbale_arbre_de_vie': 'Kabbale',
    'kabbale': 'Kabbale',
    'pack_karmique_kabbale': 'Pack Karmique',
    'pack_karmique': 'Pack Karmique',
    'theme_natal_pdf_oneshot': 'Thème Natal 29€',
    'theme_natal_pdf': 'Thème Natal (crédits)',
    'astrocartographie': 'Astrocartographie',
    'rencontres_ultime': 'Rencontres Ultime',
    'numerologie': 'Numérologie',
    'karma_destin_analysis': 'Karma & Destin',
    'karma_destin': 'Karma & Destin',
    'trio_decouverte': 'Trio Découverte',
    'duo_completion': 'Duo Complémentaire',
    'consultation_ultime': 'Consultation Ultime',
  }[p] || p);

  return (
    <div className="rounded-2xl p-6" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,175,55,0.15)' }} data-testid="admin-pdfs-sent-section">
      <div className="flex items-center justify-between mb-5 flex-wrap gap-3">
        <div>
          <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
            PDFs envoyés · <span style={{ color: '#D4AF37' }}>{total}</span>
            <span style={{ color: 'var(--pa-muted)', fontSize: 13, fontStyle: 'italic', marginLeft: 8 }}>
              (sur {totalCompleted} paiements complétés)
            </span>
          </h2>
          <p className="text-xs mt-1" style={{ color: 'var(--pa-muted)' }}>
            Filtré sur les rapports stockés dans le bucket Supabase <code>reports</code> — URLs pérennes.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={productFilter}
            onChange={(e) => setProductFilter(e.target.value)}
            data-testid="admin-pdfs-product-filter"
            style={{
              background: 'rgba(17,22,37,0.6)', color: '#F5EEE0',
              border: '1px solid rgba(212,175,55,0.25)', borderRadius: 6,
              padding: '6px 12px', fontSize: 12, letterSpacing: '0.05em',
            }}
          >
            <option value="">Tous les produits</option>
            {uniqueProducts.map((p) => (
              <option key={p} value={p}>{productLabel(p)}</option>
            ))}
          </select>
          <button
            onClick={reload}
            disabled={loading}
            data-testid="admin-pdfs-refresh"
            style={{
              background: 'rgba(212,175,55,0.10)', color: '#D4AF37',
              border: '1px solid rgba(212,175,55,0.35)', borderRadius: 999,
              padding: '6px 14px', fontSize: 11, letterSpacing: '0.15em',
              textTransform: 'uppercase', cursor: 'pointer',
            }}
          >
            {loading ? '...' : 'Rafraîchir'}
          </button>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="text-center py-12" style={{ color: 'var(--pa-muted)', fontStyle: 'italic', fontFamily: 'Cormorant Garamond, serif' }} data-testid="admin-pdfs-empty">
          {loading ? 'Chargement...' : total === 0
            ? 'Aucun PDF n\u2019a encore été uploadé sur Supabase Storage. Les nouveaux rapports générés y seront automatiquement stockés.'
            : 'Aucun résultat pour ce filtre.'}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" data-testid="admin-pdfs-table">
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(212,175,55,0.2)' }}>
                <th className="text-left py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>DATE</th>
                <th className="text-left py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>CLIENT</th>
                <th className="text-left py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>PRODUIT</th>
                <th className="text-right py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>MONTANT</th>
                <th className="text-center py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>EMAIL</th>
                <th className="text-right py-3 px-2" style={{ color: '#D4AF37', fontFamily: 'Cinzel, serif', fontSize: 11, letterSpacing: '0.15em' }}>PDF</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item) => (
                <tr key={item.session_id} style={{ borderBottom: '1px solid rgba(212,175,55,0.08)' }} data-testid={`admin-pdf-row-${item.session_id}`}>
                  <td className="py-3 px-2" style={{ color: 'var(--pa-muted)', fontSize: 12 }}>
                    {fmtDate(item.sent_at)}
                  </td>
                  <td className="py-3 px-2" style={{ color: '#F5EEE0' }}>
                    {item.user_email}
                  </td>
                  <td className="py-3 px-2">
                    <span style={{
                      background: 'rgba(212,175,55,0.12)', color: '#E8C766',
                      padding: '3px 8px', borderRadius: 999, fontSize: 11,
                      letterSpacing: '0.05em',
                    }}>
                      {productLabel(item.product)}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right" style={{ color: '#F5EEE0', fontFamily: 'Cormorant Garamond, serif' }}>
                    {item.amount > 0 ? `${item.amount.toFixed(2)}€` : '—'}
                  </td>
                  <td className="py-3 px-2 text-center">
                    {item.email_sent ? (
                      <span style={{ color: '#4ADE80', fontSize: 11 }} title="Email envoyé au client">✓</span>
                    ) : (
                      <span style={{ color: 'rgba(227,215,255,0.35)', fontSize: 11 }} title="Email non envoyé">—</span>
                    )}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <a
                      href={item.pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid={`admin-pdf-download-${item.session_id}`}
                      style={{
                        color: '#D4AF37', textDecoration: 'none',
                        border: '1px solid rgba(212,175,55,0.35)',
                        borderRadius: 999, padding: '4px 12px',
                        fontSize: 11, letterSpacing: '0.1em',
                        textTransform: 'uppercase', fontFamily: 'Cinzel, serif',
                      }}
                    >
                      Télécharger ↗
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ═══════ Promo Codes Section (with create form + toggle/delete) ═══════
function PromoSection({ token, promoCodes, reload }) {
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);
  const [form, setForm] = useState({
    code: '', type: 'premium', value: 30, max_uses: '', description: '',
  });

  const submit = async (e) => {
    e.preventDefault();
    if (!form.code.trim()) { setMsg({ type: 'err', text: 'Code requis' }); return; }
    setSaving(true);
    try {
      const payload = {
        code: form.code.trim(),
        description: form.description || undefined,
        max_uses: form.max_uses ? Number(form.max_uses) : null,
        active: true,
      };
      if (form.type === 'premium') payload.premium_days = Number(form.value || 0);
      else payload.credits = Number(form.value || 0);
      await axios.post(`${API}/api/admin/promo-codes`, payload, { headers: { Authorization: `Bearer ${token}` } });
      setMsg({ type: 'ok', text: `Code "${form.code.toUpperCase()}" cree` });
      setForm({ code: '', type: 'premium', value: 30, max_uses: '', description: '' });
      setShowForm(false);
      await reload();
    } catch (err) {
      setMsg({ type: 'err', text: err?.response?.data?.detail || 'Erreur' });
    } finally { setSaving(false); }
  };

  const toggle = async (code, current) => {
    try {
      await axios.patch(`${API}/api/admin/promo-codes/${code}`, { active: !current }, { headers: { Authorization: `Bearer ${token}` } });
      await reload();
    } catch (e) { console.error(e); }
  };

  const remove = async (code) => {
    if (!window.confirm(`Supprimer le code ${code} ?`)) return;
    try {
      await axios.delete(`${API}/api/admin/promo-codes/${code}`, { headers: { Authorization: `Bearer ${token}` } });
      await reload();
    } catch (e) { console.error(e); }
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
          {promoCodes.length} code(s) · Premium offrent un acces complet (energie, compatibilites, cycles)
        </p>
        <button onClick={() => setShowForm(!showForm)} data-testid="admin-create-promo-btn"
          className="flex items-center gap-2 px-4 py-2 rounded-full text-xs uppercase tracking-widest"
          style={{ background: '#D4AF37', color: '#111625', fontFamily: 'Cinzel, serif', fontWeight: 600, border: 'none', cursor: 'pointer' }}>
          <Plus className="w-3.5 h-3.5" strokeWidth={2} />
          {showForm ? 'Annuler' : 'Nouveau code'}
        </button>
      </div>

      {msg && (
        <div className="mb-4 px-4 py-2 rounded-lg text-xs"
          style={{
            background: msg.type === 'ok' ? 'rgba(124,184,138,0.12)' : 'rgba(255,100,100,0.12)',
            border: `1px solid ${msg.type === 'ok' ? 'rgba(124,184,138,0.4)' : 'rgba(255,100,100,0.4)'}`,
            color: msg.type === 'ok' ? '#A3D6AC' : '#fca5a5',
          }}>{msg.text}</div>
      )}

      {/* Create form */}
      {showForm && (
        <form onSubmit={submit} className="mb-8 p-5 rounded-2xl space-y-4"
          style={{ background: 'rgba(212,175,55,0.06)', border: '1px solid rgba(212,175,55,0.25)' }}
          data-testid="admin-promo-form">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Code (ex: FAMILLE2026)">
              <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })}
                style={fieldStyle} data-testid="promo-form-code"
                placeholder="FAMILLE2026" required />
            </Field>

            <Field label="Type">
              <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} style={fieldStyle} data-testid="promo-form-type">
                <option value="premium">Premium offert (jours)</option>
                <option value="credits">Credits offerts</option>
              </select>
            </Field>

            <Field label={form.type === 'premium' ? "Nombre de jours" : "Nombre de credits"}>
              <input type="number" min={1} value={form.value} onChange={(e) => setForm({ ...form, value: e.target.value })}
                style={fieldStyle} data-testid="promo-form-value" required />
            </Field>

            <Field label="Limite d'utilisations (vide = illimitee)">
              <input type="number" min={1} value={form.max_uses} onChange={(e) => setForm({ ...form, max_uses: e.target.value })}
                style={fieldStyle} data-testid="promo-form-max-uses" placeholder="ex: 10" />
            </Field>

            <Field label="Description (optionnel)" full>
              <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                style={fieldStyle} data-testid="promo-form-description"
                placeholder="Acces Premium 1 mois — offre famille" />
            </Field>
          </div>

          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowForm(false)}
              className="px-5 py-2 text-xs uppercase tracking-widest rounded-full"
              style={{ background: 'transparent', color: '#D4AF37', border: '1px solid rgba(212,175,55,0.3)' }}>
              Annuler
            </button>
            <button type="submit" disabled={saving} data-testid="promo-form-submit"
              className="px-6 py-2 text-xs uppercase tracking-widest rounded-full"
              style={{ background: '#D4AF37', color: '#111625', border: 'none', fontFamily: 'Cinzel, serif', fontWeight: 600 }}>
              {saving ? 'Creation...' : 'Creer le code'}
            </button>
          </div>
        </form>
      )}

      {/* Codes table */}
      <Table
        columns={[
          { key: 'code', label: 'Code', render: r => <span style={{ fontFamily: 'monospace', color: '#D4AF37', fontWeight: 600 }}>{r.code}</span> },
          { key: 'type', label: 'Type', render: r => r.premium_days ? <span style={{ color: '#E8C766', display: 'inline-flex', alignItems: 'center', gap: 4 }}><Crown className="w-3 h-3" />Premium</span> : <span>Credits</span> },
          { key: 'reward', label: 'Recompense', render: r => r.premium_days ? `${r.premium_days} jours Premium` : `+${r.credits} cr` },
          { key: 'description', label: 'Description' },
          { key: 'used_count', label: 'Utilisations' },
          { key: 'max_uses', label: 'Limite', render: r => r.max_uses || '\u221E' },
          { key: 'active', label: 'Statut', render: r => r.active
            ? <span style={{ color: '#7CB88A' }}>Actif</span>
            : <span style={{ color: 'var(--pa-muted)' }}>Inactif</span>
          },
          { key: 'actions', label: 'Actions', render: r => (
            <div style={{ display: 'flex', gap: 6 }}>
              <button onClick={() => toggle(r.code, r.active)} title={r.active ? 'Desactiver' : 'Activer'}
                data-testid={`promo-toggle-${r.code}`}
                style={{ background: 'transparent', border: '1px solid rgba(212,175,55,0.3)', borderRadius: 6, padding: '4px 8px', cursor: 'pointer', color: r.active ? '#7CB88A' : '#999' }}>
                <Power className="w-3 h-3" />
              </button>
              <button onClick={() => remove(r.code)} title="Supprimer"
                data-testid={`promo-delete-${r.code}`}
                style={{ background: 'transparent', border: '1px solid rgba(255,100,100,0.3)', borderRadius: 6, padding: '4px 8px', cursor: 'pointer', color: '#fca5a5' }}>
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ) },
        ]}
        rows={promoCodes}
      />
    </div>
  );
}

const fieldStyle = {
  width: '100%', padding: '10px 12px', borderRadius: 8,
  background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(212,175,55,0.25)',
  color: '#F4E4BC', fontSize: 13, outline: 'none',
};

function Field({ label, children, full }) {
  return (
    <label style={{ display: 'block', gridColumn: full ? '1 / -1' : undefined }}>
      <span style={{ display: 'block', marginBottom: 6, fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(212,175,55,0.85)', fontFamily: 'Cinzel, serif' }}>{label}</span>
      {children}
    </label>
  );
}


/* ════════════════════════════════════════════════════════════════════
   USER ACTIONS — credits + premium + suppression
   ════════════════════════════════════════════════════════════════════ */
function UserActions({ user, token, onChange }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [creditsAmount, setCreditsAmount] = useState('');
  const [premiumDays, setPremiumDays] = useState('');
  const [msg, setMsg] = useState('');

  const flash = (text, ok = true) => {
    setMsg(text);
    setTimeout(() => setMsg(''), 2500);
  };

  const handleAddCredits = async () => {
    const amt = parseInt(creditsAmount, 10);
    if (!amt || isNaN(amt)) { flash('Montant invalide', false); return; }
    setBusy(true);
    try {
      const r = await axios.post(
        `${API}/api/admin/users/${user.id}/credits`,
        { amount: amt, description: amt > 0 ? 'Cadeau admin' : 'Retrait admin' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      flash(`Solde : ${r.data.new_balance} cr`);
      setCreditsAmount('');
      onChange?.();
    } catch (e) {
      flash(e?.response?.data?.detail || 'Erreur', false);
    }
    setBusy(false);
  };

  const handleGrantPremium = async (action, days = null) => {
    setBusy(true);
    try {
      const body = action === 'grant_days' ? { action, days: parseInt(days, 10) } : { action };
      await axios.post(`${API}/api/admin/users/${user.id}/premium`, body,
        { headers: { Authorization: `Bearer ${token}` } });
      flash(
        action === 'revoke' ? 'Premium retire'
          : action === 'grant_lifetime' ? 'Premium a vie active'
          : `+${days} jours Premium`
      );
      setPremiumDays('');
      onChange?.();
    } catch (e) {
      flash(e?.response?.data?.detail || 'Erreur', false);
    }
    setBusy(false);
  };

  const handleDelete = async () => {
    if (!window.confirm(`Supprimer definitivement ${user.email} ?\n\nToutes ses donnees seront perdues. Action irreversible.`)) return;
    setBusy(true);
    try {
      await axios.delete(`${API}/api/admin/users/${user.id}`, { headers: { Authorization: `Bearer ${token}` } });
      onChange?.();
    } catch (e) {
      flash(e?.response?.data?.detail || 'Erreur', false);
    }
    setBusy(false);
  };

  if (user.is_admin) {
    return <span style={{ color: 'var(--pa-muted)', fontSize: 11 }}>—</span>;
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        data-testid={`admin-actions-btn-${user.id}`}
        style={{
          background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.35)',
          borderRadius: 6, padding: '4px 10px', cursor: 'pointer',
          color: '#D4AF37', fontSize: 11, letterSpacing: '0.08em',
          textTransform: 'uppercase', fontWeight: 600,
        }}
        title="Gerer cet utilisateur"
      >
        Gerer
      </button>

      {open && (
        <div
          onClick={() => setOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(6px)', zIndex: 50,
            display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            data-testid={`admin-actions-modal-${user.id}`}
            style={{
              background: '#0F1A3C', border: '1px solid rgba(212,175,55,0.3)',
              borderRadius: 16, padding: 24, maxWidth: 460, width: '100%',
              maxHeight: '90vh', overflowY: 'auto',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 11, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--pa-muted)', marginBottom: 4 }}>
                  Gerer l'utilisateur
                </div>
                <div style={{ fontSize: 15, color: 'var(--pa-heading)', fontFamily: 'Cormorant Garamond, serif' }}>
                  {user.email}
                </div>
                <div style={{ fontSize: 12, color: 'var(--pa-muted)', marginTop: 4 }}>
                  Solde actuel : <span style={{ color: '#D4AF37', fontWeight: 600 }}>{user.credit_balance} cr</span>
                  {' · '}
                  Premium : <span style={{ color: user.premium_status === 'active' ? '#FDE68A' : 'var(--pa-muted)' }}>
                    {user.premium_status === 'active' ? (user.premium_until ? `actif jusqu'au ${new Date(user.premium_until).toLocaleDateString('fr-FR')}` : 'actif') : 'inactif'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--pa-muted)', cursor: 'pointer', fontSize: 20, padding: 0, lineHeight: 1 }}
                aria-label="Fermer"
              >×</button>
            </div>

            {msg && (
              <div style={{ background: 'rgba(74,222,128,0.12)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ADE80', padding: 10, borderRadius: 8, fontSize: 12, marginBottom: 16 }} data-testid="admin-action-msg">
                {msg}
              </div>
            )}

            {/* Section credits */}
            <div style={{ marginBottom: 20, padding: 16, background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.15)', borderRadius: 12 }}>
              <div style={{ fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#D4AF37', marginBottom: 10, fontWeight: 600 }}>
                💰 Credits
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="number"
                  value={creditsAmount}
                  onChange={(e) => setCreditsAmount(e.target.value)}
                  placeholder="ex: 5000 ou -100"
                  data-testid="admin-credits-input"
                  style={{
                    flex: 1, background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(212,175,55,0.25)',
                    borderRadius: 8, padding: '8px 12px', color: 'var(--pa-body)', fontSize: 13, outline: 'none',
                  }}
                />
                <button
                  onClick={handleAddCredits}
                  disabled={busy || !creditsAmount}
                  data-testid="admin-add-credits-btn"
                  style={{
                    background: '#D4AF37', color: '#111625', border: 'none',
                    borderRadius: 8, padding: '8px 16px', cursor: busy ? 'wait' : 'pointer',
                    fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase',
                    fontWeight: 700, opacity: busy ? 0.6 : 1,
                  }}
                >
                  Appliquer
                </button>
              </div>
              <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                {[100, 500, 1000, 5000].map(n => (
                  <button
                    key={n}
                    onClick={() => setCreditsAmount(String(n))}
                    style={{
                      background: 'transparent', border: '1px solid rgba(212,175,55,0.3)',
                      borderRadius: 12, padding: '3px 10px', color: '#D4AF37', fontSize: 10,
                      cursor: 'pointer', letterSpacing: '0.05em',
                    }}
                  >
                    +{n}
                  </button>
                ))}
              </div>
            </div>

            {/* Section Premium */}
            <div style={{ marginBottom: 20, padding: 16, background: 'rgba(253,230,138,0.04)', border: '1px solid rgba(253,230,138,0.15)', borderRadius: 12 }}>
              <div style={{ fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#FDE68A', marginBottom: 10, fontWeight: 600 }}>
                👑 Premium
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                {[7, 30, 90, 365].map(d => (
                  <button
                    key={d}
                    onClick={() => handleGrantPremium('grant_days', d)}
                    disabled={busy}
                    data-testid={`admin-premium-${d}d-btn`}
                    style={{
                      background: 'rgba(253,230,138,0.08)', border: '1px solid rgba(253,230,138,0.3)',
                      borderRadius: 8, padding: '8px', cursor: busy ? 'wait' : 'pointer',
                      color: '#FDE68A', fontSize: 11, letterSpacing: '0.05em',
                    }}
                  >
                    +{d} jours
                  </button>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <input
                  type="number"
                  value={premiumDays}
                  onChange={(e) => setPremiumDays(e.target.value)}
                  placeholder="Nombre de jours personnalise"
                  style={{
                    flex: 1, background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(253,230,138,0.2)',
                    borderRadius: 8, padding: '6px 12px', color: 'var(--pa-body)', fontSize: 12, outline: 'none',
                  }}
                />
                <button
                  onClick={() => handleGrantPremium('grant_days', premiumDays)}
                  disabled={busy || !premiumDays}
                  style={{
                    background: 'rgba(253,230,138,0.15)', border: '1px solid rgba(253,230,138,0.4)',
                    borderRadius: 8, padding: '6px 14px', cursor: 'pointer',
                    color: '#FDE68A', fontSize: 11, fontWeight: 600,
                  }}
                >
                  OK
                </button>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  onClick={() => handleGrantPremium('grant_lifetime')}
                  disabled={busy}
                  data-testid="admin-premium-lifetime-btn"
                  style={{
                    flex: 1, background: 'linear-gradient(135deg, #FDE68A, #D4AF37)',
                    color: '#111625', border: 'none', borderRadius: 8, padding: '10px',
                    cursor: 'pointer', fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
                  }}
                >
                  Premium a vie
                </button>
                {user.premium_status === 'active' && (
                  <button
                    onClick={() => {
                      if (window.confirm('Retirer le Premium de cet utilisateur ?')) {
                        handleGrantPremium('revoke');
                      }
                    }}
                    disabled={busy}
                    data-testid="admin-premium-revoke-btn"
                    style={{
                      background: 'transparent', border: '1px solid rgba(255,100,100,0.4)',
                      borderRadius: 8, padding: '10px 14px', cursor: 'pointer',
                      color: '#fca5a5', fontSize: 11, letterSpacing: '0.08em',
                    }}
                  >
                    Retirer
                  </button>
                )}
              </div>
            </div>

            {/* Section suppression */}
            <div style={{ padding: 16, background: 'rgba(255,100,100,0.04)', border: '1px solid rgba(255,100,100,0.15)', borderRadius: 12 }}>
              <div style={{ fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#fca5a5', marginBottom: 10, fontWeight: 600 }}>
                ⚠️ Zone dangereuse
              </div>
              <button
                onClick={handleDelete}
                disabled={busy}
                data-testid={`admin-delete-user-${user.id}`}
                style={{
                  background: 'transparent', border: '1px solid rgba(255,100,100,0.4)',
                  borderRadius: 8, padding: '8px 14px', cursor: 'pointer',
                  color: '#fca5a5', fontSize: 11, letterSpacing: '0.08em',
                  textTransform: 'uppercase', fontWeight: 600,
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                }}
              >
                <Trash2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                Supprimer le compte
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
