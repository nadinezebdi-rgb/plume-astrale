import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Users, TrendingUp, Coins, Crown, RefreshCw, Shield, Eye, EyeOff, Star, Zap } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const StatCard = ({ icon: Icon, label, value, color, sub }) => (
  <div style={{
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(212,180,106,0.15)',
    borderRadius: 16, padding: 24,
    display: 'flex', flexDirection: 'column', gap: 8,
  }}>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <span style={{ fontSize: 12, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(212,180,106,0.6)' }}>{label}</span>
      <Icon style={{ width: 18, height: 18, color: color || '#C5A059' }} strokeWidth={1.5} />
    </div>
    <div style={{ fontSize: 36, fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: color || '#F5EEE0' }}>
      {value}
    </div>
    {sub && <div style={{ fontSize: 12, color: 'rgba(212,180,106,0.5)' }}>{sub}</div>}
  </div>
);

export default function Admin() {
  const [secret, setSecret] = useState('');
  const [secretInput, setSecretInput] = useState('');
  const [showSecret, setShowSecret] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [editCredits, setEditCredits] = useState({});
  const [msg, setMsg] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);

  const headers = { 'x-admin-secret': secret };

  const fetchStats = useCallback(async () => {
    if (!secret) return;
    try {
      const res = await axios.get(`${API}/api/admin/stats`, { headers });
      setStats(res.data);
    } catch (e) {
      { headers: { 'mon_espace': secret } }
    }
  }, [secret]);

  const fetchUsers = useCallback(async (p = 1) => {
    if (!secret) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/admin/users?page=${p}&limit=20`, { headers });
      setUsers(res.data.users || []);
      setTotalUsers(res.data.total || 0);
      { headers: { 'mon_espace': secret } }
    } catch (e) {
      setMsg('Erreur users : ' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  }, [secret]);

  const handleLogin = () => {
    if (!secretInput.trim()) return;
    setSecret(secretInput.trim());
    setAuthed(true);
  };

  useEffect(() => {
    if (!authed || !secret) return;
    fetchStats();
    fetchUsers(1);
  }, [authed, secret]);

  useEffect(() => {
    }, [authed, secret, fetchStats, fetchUsers]);
    const interval = setInterval(() => { fetchStats(); }, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, authed, fetchStats]);

 const handleSetCredits = async (userId) => {
    const credits = editCredits[userId];
    if (credits === undefined) return;
    try {
      await axios.post(
        `${API}/api/admin/credits`,
        { user_id: userId, credits: parseInt(credits) },
        { headers: { 'x-admin-secret': secret } }
      );
      setMsg('Credits mis a jour !');
      fetchUsers(page);
      setTimeout(() => setMsg(''), 3000);
    } catch (e) {
      setMsg('Erreur : ' + (e.response?.data?.detail || e.message));
    }
  };

  const handleTogglePremium = async (userId, current) => {
    try {
      await axios.post(
        `${API}/api/admin/premium`,
        { user_id: userId, is_premium: !current },
        { headers: { 'mon_espace': secret } }
      );
      setMsg(!current ? 'Premium active !' : 'Premium desactive');
      fetchUsers(page);
      setTimeout(() => setMsg(''), 3000);
    } catch (e) {
      setMsg('Erreur : ' + (e.response?.data?.detail || e.message));
    }
  };


  const bg = { minHeight: '100vh', background: '#0B0B0F', color: '#F0E6D3', fontFamily: 'DM Sans, sans-serif' };

  const tabStyle = (t) => ({
    padding: '8px 20px', borderRadius: 999, fontSize: 12,
    letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer',
    border: activeTab === t ? '1px solid #C5A059' : '1px solid rgba(212,180,106,0.2)',
    background: activeTab === t ? 'rgba(197,160,89,0.15)' : 'transparent',
    color: activeTab === t ? '#D4B46A' : 'rgba(212,180,106,0.5)',
    transition: 'all 0.2s',
  });

  if (!authed) {
    return (
      <div style={Object.assign({}, bg, { display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: 80 })}>
        <div style={{ width: 360, padding: 40, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(212,180,106,0.2)', borderRadius: 20, textAlign: 'center' }}>
          <Shield style={{ width: 40, height: 40, color: '#C5A059', margin: '0 auto 16px' }} strokeWidth={1} />
          <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 28, fontWeight: 300, color: '#F5EEE0', marginBottom: 8 }}>
            Admin Panel
          </h1>
          <p style={{ fontSize: 12, color: 'rgba(212,180,106,0.5)', marginBottom: 28, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Plume Astrale
          </p>
          <div style={{ position: 'relative', marginBottom: 16 }}>
            <input
              type={showSecret ? 'text' : 'password'}
              value={secretInput}
              onChange={e => setSecretInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              placeholder="Mot de passe admin"
              style={{ width: '100%', padding: '12px 44px 12px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(212,180,106,0.3)', borderRadius: 999, color: '#F5EEE0', fontSize: 14, outline: 'none', boxSizing: 'border-box' }}
            />
            <button onClick={() => setShowSecret(!showSecret)}
              style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(212,180,106,0.5)' }}>
              {showSecret ? <EyeOff style={{ width: 16, height: 16 }} /> : <Eye style={{ width: 16, height: 16 }} />}
            </button>
          </div>
          <button onClick={handleLogin}
            style={{ width: '100%', padding: 12, background: 'linear-gradient(135deg, #C5A059, #D4B46A)', color: '#0B0B0F', border: 'none', borderRadius: 999, fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase', fontWeight: 600, cursor: 'pointer' }}>
            Entrer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={bg}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 32, fontWeight: 300, color: '#F5EEE0', margin: 0 }}>
              Admin Dashboard
            </h1>
            <p style={{ fontSize: 12, color: 'rgba(212,180,106,0.5)', margin: '4px 0 0', letterSpacing: '0.1em' }}>
              Plume Astrale — Vue en temps reel
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button onClick={() => setAutoRefresh(!autoRefresh)}
              style={{ padding: '8px 16px', borderRadius: 999, fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer', border: '1px solid rgba(212,180,106,0.3)', background: autoRefresh ? 'rgba(197,160,89,0.15)' : 'transparent', color: autoRefresh ? '#D4B46A' : 'rgba(212,180,106,0.5)' }}>
              {autoRefresh ? 'Auto ON' : 'Auto OFF'}
            </button>
            <button onClick={() => { fetchStats(); fetchUsers(page); }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 999, fontSize: 11, cursor: 'pointer', border: '1px solid rgba(212,180,106,0.3)', background: 'transparent', color: 'rgba(212,180,106,0.6)' }}>
              <RefreshCw style={{ width: 14, height: 14 }} strokeWidth={1.5} />
              Rafraichir
            </button>
          </div>
        </div>

        {msg && (
          <div style={{ padding: '12px 20px', borderRadius: 12, marginBottom: 24, background: 'rgba(197,160,89,0.1)', border: '1px solid rgba(197,160,89,0.3)', color: '#D4B46A', fontSize: 13 }}>
            {msg}
          </div>
        )}

        <div style={{ display: 'flex', gap: 8, marginBottom: 32 }}>
          {[['dashboard', 'Dashboard'], ['users', 'Utilisateurs'], ['payments', 'Paiements']].map(([t, l]) => (
            <button key={t} onClick={() => setActiveTab(t)} style={tabStyle(t)}>{l}</button>
          ))}
        </div>

        {activeTab === 'dashboard' && stats && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
              <StatCard icon={Users} label="Utilisateurs" value={stats.total_users} color="#C5A059" sub={'+' + stats.new_today + ' aujourd&#39;hui'} />
              <StatCard icon={Crown} label="Premium" value={stats.premium_users} color="#B88CFF" sub={stats.total_users > 0 ? Math.round(stats.premium_users / stats.total_users * 100) + '% du total' : '0%'} />
              <StatCard icon={TrendingUp} label="Revenue Total" value={stats.total_revenue + ' EUR'} color="#7CB88A" sub="Paiements Stripe" />
              <StatCard icon={Coins} label="Credits Actifs" value={stats.total_credits} color="#D4B46A" sub="En circulation" />
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,180,106,0.1)', borderRadius: 16, padding: 24 }}>
              <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, fontWeight: 300, color: '#F5EEE0', margin: '0 0 20px' }}>
                Derniers paiements
              </h2>
              {stats.last_payments.length === 0 ? (
                <p style={{ color: 'rgba(212,180,106,0.4)', fontSize: 13 }}>Aucun paiement enregistre</p>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      {['Email', 'Produit', 'Montant', 'Date'].map(h => (
                        <th key={h} style={{ textAlign: 'left', padding: '8px 12px', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(212,180,106,0.5)', borderBottom: '1px solid rgba(212,180,106,0.08)' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {stats.last_payments.map((p, i) => (
                      <tr key={i}>
                        <td style={{ padding: '10px 12px', fontSize: 13, color: '#F0E6D3', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.email || '-'}</td>
                        <td style={{ padding: '10px 12px', fontSize: 13, color: 'rgba(212,180,106,0.7)', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.product || '-'}</td>
                        <td style={{ padding: '10px 12px', fontSize: 13, color: '#7CB88A', fontWeight: 600, borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.amount ? p.amount + ' EUR' : '-'}</td>
                        <td style={{ padding: '10px 12px', fontSize: 12, color: 'rgba(212,180,106,0.4)', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.created_at ? new Date(p.created_at).toLocaleDateString('fr-FR') : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <p style={{ fontSize: 13, color: 'rgba(212,180,106,0.5)' }}>{totalUsers} utilisateurs</p>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => fetchUsers(page - 1)} disabled={page <= 1}
                  style={{ padding: '6px 16px', borderRadius: 999, fontSize: 12, cursor: page > 1 ? 'pointer' : 'default', border: '1px solid rgba(212,180,106,0.2)', background: 'transparent', color: '#D4B46A', opacity: page <= 1 ? 0.4 : 1 }}>
                  Prev
                </button>
                <span style={{ padding: '6px 12px', fontSize: 12, color: 'rgba(212,180,106,0.5)' }}>Page {page}</span>
                <button onClick={() => fetchUsers(page + 1)} disabled={users.length < 20}
                  style={{ padding: '6px 16px', borderRadius: 999, fontSize: 12, cursor: users.length >= 20 ? 'pointer' : 'default', border: '1px solid rgba(212,180,106,0.2)', background: 'transparent', color: '#D4B46A', opacity: users.length < 20 ? 0.4 : 1 }}>
                  Suiv
                </button>
              </div>
            </div>
            {loading ? (
              <div style={{ textAlign: 'center', padding: 40, color: 'rgba(212,180,106,0.4)' }}>Chargement...</div>
            ) : (
              <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,180,106,0.1)', borderRadius: 16, overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: 'rgba(197,160,89,0.04)' }}>
                      {['Email', 'Nom', 'Credits', 'Premium', 'Inscription', 'Actions'].map(h => (
                        <th key={h} style={{ textAlign: 'left', padding: '12px 16px', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(212,180,106,0.5)' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user, i) => (
                      <tr key={user.id || i} style={{ borderTop: '1px solid rgba(212,180,106,0.05)' }}>
                        <td style={{ padding: '12px 16px', fontSize: 13, color: '#F0E6D3' }}>{user.email}</td>
                        <td style={{ padding: '12px 16px', fontSize: 13, color: 'rgba(212,180,106,0.7)' }}>{user.name || '-'}</td>
                        <td style={{ padding: '12px 16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <input type="number" defaultValue={user.credits || 0}
                              onChange={e => setEditCredits(prev => ({ ...prev, [user.id]: e.target.value }))}
                              style={{ width: 70, padding: '4px 8px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(212,180,106,0.2)', borderRadius: 8, color: '#D4B46A', fontSize: 13, outline: 'none' }} />
                            <button onClick={() => handleSetCredits(user.id)}
                              style={{ padding: '4px 10px', borderRadius: 8, fontSize: 11, cursor: 'pointer', border: '1px solid rgba(197,160,89,0.4)', background: 'rgba(197,160,89,0.1)', color: '#C5A059' }}>
                              OK
                            </button>
                          </div>
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <span style={{ padding: '3px 10px', borderRadius: 999, fontSize: 11, background: user.is_premium ? 'rgba(184,140,255,0.15)' : 'rgba(255,255,255,0.04)', border: user.is_premium ? '1px solid rgba(184,140,255,0.4)' : '1px solid rgba(255,255,255,0.08)', color: user.is_premium ? '#B88CFF' : 'rgba(212,180,106,0.4)' }}>
                            {user.is_premium ? 'Premium' : 'Free'}
                          </span>
                        </td>
                        <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(212,180,106,0.4)' }}>
                          {user.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : '-'}
                        </td>
                        <td style={{ padding: '12px 16px' }}>
                          <button onClick={() => handleTogglePremium(user.id, user.is_premium)}
                            style={{ padding: '4px 12px', borderRadius: 999, fontSize: 11, cursor: 'pointer', border: user.is_premium ? '1px solid rgba(255,100,100,0.3)' : '1px solid rgba(184,140,255,0.4)', background: user.is_premium ? 'rgba(255,80,80,0.08)' : 'rgba(184,140,255,0.1)', color: user.is_premium ? '#ff8080' : '#B88CFF' }}>
                            {user.is_premium ? 'Retirer' : 'Activer Premium'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'payments' && stats && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
              <StatCard icon={TrendingUp} label="Revenue Total" value={stats.total_revenue + ' EUR'} color="#7CB88A" />
              <StatCard icon={Star} label="Derniers paiements" value={stats.last_payments.length} color="#C5A059" />
              <StatCard icon={Zap} label="Taux Premium" value={stats.total_users > 0 ? Math.round(stats.premium_users / stats.total_users * 100) + '%' : '0%'} color="#B88CFF" />
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(212,180,106,0.1)', borderRadius: 16, padding: 24 }}>
              <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, fontWeight: 300, color: '#F5EEE0', margin: '0 0 20px' }}>Historique</h2>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>{['Email', 'Produit', 'Montant', 'Date'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '8px 12px', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(212,180,106,0.5)', borderBottom: '1px solid rgba(212,180,106,0.08)' }}>{h}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {stats.last_payments.map((p, i) => (
                    <tr key={i}>
                      <td style={{ padding: '12px', fontSize: 13, color: '#F0E6D3', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.email || '-'}</td>
                      <td style={{ padding: '12px', fontSize: 13, color: 'rgba(212,180,106,0.7)', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.product || '-'}</td>
                      <td style={{ padding: '12px', fontSize: 14, color: '#7CB88A', fontWeight: 600, borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.amount ? p.amount + ' EUR' : '-'}</td>
                      <td style={{ padding: '12px', fontSize: 12, color: 'rgba(212,180,106,0.4)', borderBottom: '1px solid rgba(212,180,106,0.05)' }}>{p.created_at ? new Date(p.created_at).toLocaleDateString('fr-FR') : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
