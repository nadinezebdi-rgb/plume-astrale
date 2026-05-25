import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import {
  Users, Euro, TrendingUp, MessageCircle, Coins, ShoppingCart,
  Loader2, RefreshCw, Search, Tag, Activity, Sparkles,
} from 'lucide-react';
import SEO from '@/components/SEO';

const API = process.env.REACT_APP_BACKEND_URL;

const Card = ({ icon: Icon, label, value, sub, accent = '#C5A059' }) => (
  <div className="rounded-2xl p-5" style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(197,160,89,0.18)',
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
      borderColor: active ? '#C5A059' : 'rgba(197,160,89,0.25)',
      color: active ? '#0C0918' : '#C5A059',
      background: active ? '#C5A059' : 'transparent',
      letterSpacing: '0.1em',
    }}
    data-testid={`admin-tab-${label.toLowerCase().replace(/\s+/g, '-')}`}>
    {label}{count !== undefined && ` (${count})`}
  </button>
);

const Table = ({ columns, rows, emptyMessage }) => (
  <div className="rounded-xl overflow-hidden" style={{ border: '1px solid rgba(197,160,89,0.15)' }}>
    <div className="overflow-x-auto">
      <table className="w-full text-sm" style={{ color: 'var(--pa-body)' }}>
        <thead style={{ background: 'rgba(197,160,89,0.06)' }}>
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
            <tr key={i} style={{ borderTop: '1px solid rgba(197,160,89,0.06)' }}>
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

  useEffect(() => {
    if (!token || !user?.is_admin) return;
    if (tab === 'overview') loadStats();
    else if (tab === 'users') loadUsers(search);
    else if (tab === 'payments') loadPayments();
    else if (tab === 'transactions') loadTransactions();
    else if (tab === 'promo') loadPromo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, token, user?.is_admin]);

  const refresh = () => {
    if (tab === 'overview') loadStats();
    else if (tab === 'users') loadUsers(search);
    else if (tab === 'payments') loadPayments();
    else if (tab === 'transactions') loadTransactions();
    else loadPromo();
  };

  if (authLoading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#C5A059' }} /></div>;
  if (!user) return <Navigate to="/connexion" replace />;
  if (!user.is_admin) return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-md p-8 rounded-2xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)' }} data-testid="admin-access-denied">
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
              <Sparkles className="w-5 h-5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <h1 className="text-3xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Tableau de bord
              </h1>
            </div>
            <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
              Pilotage Plume Astrale — {user.email}
            </p>
          </div>
          <button onClick={refresh}
            className="flex items-center gap-2 px-4 py-2 text-xs uppercase tracking-widest rounded-full"
            style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.1em' }}
            data-testid="admin-refresh-btn">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-8">
          <Tab label="Vue d'ensemble" active={tab === 'overview'} onClick={() => setTab('overview')} />
          <Tab label="Utilisateurs" active={tab === 'users'} onClick={() => setTab('users')} count={stats?.users?.total} />
          <Tab label="Paiements" active={tab === 'payments'} onClick={() => setTab('payments')} count={stats?.revenue?.total_paid_count} />
          <Tab label="Transactions" active={tab === 'transactions'} onClick={() => setTab('transactions')} />
          <Tab label="Codes promo" active={tab === 'promo'} onClick={() => setTab('promo')} />
        </div>

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
                  style={{ border: '1px solid rgba(197,160,89,0.25)', color: 'var(--pa-body)' }}
                  data-testid="admin-user-search" />
              </div>
              <button onClick={() => loadUsers(search)}
                className="px-4 py-2 text-xs uppercase tracking-widest rounded-full"
                style={{ border: '1px solid #C5A059', color: '#0C0918', background: '#C5A059', letterSpacing: '0.1em', fontWeight: 600 }}>
                Chercher
              </button>
            </div>
            <p className="text-xs mb-3" style={{ color: 'var(--pa-muted)' }}>{usersTotal} utilisateurs au total</p>
            <Table
              columns={[
                { key: 'email', label: 'Email' },
                { key: 'prenom', label: 'Prenom' },
                { key: 'created_at', label: 'Inscrit le', render: r => fmtDate(r.created_at) },
                { key: 'credit_balance', label: 'Solde', render: r => <span style={{ color: '#C5A059', fontWeight: 600 }}>{r.credit_balance} cr</span> },
                { key: 'total_spent_eur', label: 'Depense', render: r => fmtEur(r.total_spent_eur) },
                { key: 'is_admin', label: 'Admin', render: r => r.is_admin ? <span style={{ color: '#7CB88A' }}>Oui</span> : '—' },
                { key: 'birth_place', label: 'Lieu naissance' },
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

        {tab === 'promo' && (
          <Table
            columns={[
              { key: 'code', label: 'Code', render: r => <span style={{ fontFamily: 'monospace', color: '#C5A059', fontWeight: 600 }}>{r.code}</span> },
              { key: 'credits', label: 'Credits', render: r => `+${r.credits} cr` },
              { key: 'description', label: 'Description' },
              { key: 'used_count', label: 'Utilisations' },
              { key: 'max_uses', label: 'Limite', render: r => r.max_uses || '∞' },
              { key: 'active', label: 'Actif', render: r => r.active ? <span style={{ color: '#7CB88A' }}>Oui</span> : 'Non' },
            ]}
            rows={promoCodes}
          />
        )}

      </div>
    </div>
  );
}
