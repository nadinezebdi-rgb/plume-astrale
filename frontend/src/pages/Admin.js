import React, { useEffect, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import {
  Users, Euro, TrendingUp, MessageCircle, Coins, ShoppingCart,
  Loader2, RefreshCw, Search, Tag, Activity, Sparkles, Plus, Power, Trash2, Crown,
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
                { key: 'actions', label: '', render: r => r.is_admin ? null : (
                  <button
                    onClick={async () => {
                      if (!window.confirm(`Supprimer definitivement ${r.email} ?\n\nToutes ses donnees (compte, credits, chats, paiements) seront perdues. Cette action est irreversible.`)) return;
                      try {
                        await axios.delete(`${API}/api/admin/users/${r.id}`, { headers: { Authorization: `Bearer ${token}` } });
                        loadUsers(search);
                      } catch (err) {
                        alert(err?.response?.data?.detail || 'Erreur lors de la suppression');
                      }
                    }}
                    data-testid={`admin-delete-user-${r.id}`}
                    title="Supprimer cet utilisateur"
                    style={{
                      background: 'transparent', border: '1px solid rgba(255,100,100,0.3)',
                      borderRadius: 6, padding: '4px 8px', cursor: 'pointer', color: '#fca5a5',
                    }}
                  >
                    <Trash2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                  </button>
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

        {tab === 'promo' && (
          <PromoSection token={token} promoCodes={promoCodes} reload={loadPromo} />
        )}

      </div>
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
          style={{ background: '#C5A059', color: '#0C0918', fontFamily: 'Cinzel, serif', fontWeight: 600, border: 'none', cursor: 'pointer' }}>
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
          style={{ background: 'rgba(197,160,89,0.06)', border: '1px solid rgba(197,160,89,0.25)' }}
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
              style={{ background: 'transparent', color: '#C5A059', border: '1px solid rgba(197,160,89,0.3)' }}>
              Annuler
            </button>
            <button type="submit" disabled={saving} data-testid="promo-form-submit"
              className="px-6 py-2 text-xs uppercase tracking-widest rounded-full"
              style={{ background: '#C5A059', color: '#0C0918', border: 'none', fontFamily: 'Cinzel, serif', fontWeight: 600 }}>
              {saving ? 'Creation...' : 'Creer le code'}
            </button>
          </div>
        </form>
      )}

      {/* Codes table */}
      <Table
        columns={[
          { key: 'code', label: 'Code', render: r => <span style={{ fontFamily: 'monospace', color: '#C5A059', fontWeight: 600 }}>{r.code}</span> },
          { key: 'type', label: 'Type', render: r => r.premium_days ? <span style={{ color: '#F4D98C', display: 'inline-flex', alignItems: 'center', gap: 4 }}><Crown className="w-3 h-3" />Premium</span> : <span>Credits</span> },
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
                style={{ background: 'transparent', border: '1px solid rgba(197,160,89,0.3)', borderRadius: 6, padding: '4px 8px', cursor: 'pointer', color: r.active ? '#7CB88A' : '#999' }}>
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
  background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(197,160,89,0.25)',
  color: '#F4E4BC', fontSize: 13, outline: 'none',
};

function Field({ label, children, full }) {
  return (
    <label style={{ display: 'block', gridColumn: full ? '1 / -1' : undefined }}>
      <span style={{ display: 'block', marginBottom: 6, fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(197,160,89,0.85)', fontFamily: 'Cinzel, serif' }}>{label}</span>
      {children}
    </label>
  );
}
