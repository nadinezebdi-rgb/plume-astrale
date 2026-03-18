import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, History, Bell, BellOff, Settings, LogOut, Coins, Calendar, ChevronRight, Star, Sparkles, Clock, Shield } from 'lucide-react';
import { useAuth, getHistory, getNotifPrefs, setNotifPrefs, requestNotifPermission } from '@/context/AuthContext';
import SEO from '@/components/SEO';

const SERVICE_LABELS = {
  'tarot-oui-non': 'Tarot Oui/Non',
  'tirage-tarot': 'Lecture Tarot',
  'numerologie': 'Numérologie',
  'tarologie': 'Tarologie',
  'compatibilite': 'Compatibilité',
  'premium': 'Cartographie Premium',
  'theme-astral': 'Thème Astral',
  'horoscope': 'Horoscope',
  'account': 'Compte',
};

const Tab = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 text-xs uppercase tracking-widest px-4 py-2.5 rounded-full transition-all duration-300 whitespace-nowrap ${active ? '' : 'hover:bg-[#D4B46A]/10'}`}
    style={{
      border: active ? '1px solid rgba(197,160,89,0.5)' : '1px solid rgba(197,160,89,0.15)',
      color: active ? '#C5A059' : 'rgba(197,160,89,0.5)',
      background: active ? 'rgba(197,160,89,0.08)' : 'transparent',
      letterSpacing: '0.1em',
    }}
  >
    <Icon className="w-3.5 h-3.5" strokeWidth={1.5} />
    {label}
  </button>
);

export default function MonCompte() {
  const navigate = useNavigate();
  const { user, isAuthenticated, creditBalance, logout, isDemo, updateDemoProfile } = useAuth();
  const [tab, setTab] = useState('profil');
  const [history, setHistory] = useState([]);
  const [notifPrefs, setLocalNotifPrefs] = useState(getNotifPrefs());
  const [notifStatus, setNotifStatus] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/connexion');
      return;
    }
    setHistory(getHistory());
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (user) {
      setEditData({
        name: user.name || '',
        birth_place: user.birth_place || '',
        birth_date: user.birth_date || '',
        birth_time: user.birth_time || '',
      });
    }
  }, [user]);

  if (!isAuthenticated || !user) return null;

  const handleNotifToggle = async () => {
    if (!notifPrefs.enabled) {
      const granted = await requestNotifPermission();
      if (granted) {
        const newPrefs = { ...notifPrefs, enabled: true };
        setNotifPrefs(newPrefs);
        setLocalNotifPrefs(newPrefs);
        setNotifStatus('Notifications activées');
      } else {
        setNotifStatus('Permission refusée par le navigateur');
      }
    } else {
      const newPrefs = { ...notifPrefs, enabled: false };
      setNotifPrefs(newPrefs);
      setLocalNotifPrefs(newPrefs);
      setNotifStatus('Notifications désactivées');
    }
    setTimeout(() => setNotifStatus(''), 3000);
  };

  const handleNotifHour = (hour) => {
    const newPrefs = { ...notifPrefs, hour: parseInt(hour) };
    setNotifPrefs(newPrefs);
    setLocalNotifPrefs(newPrefs);
  };

  const handleSaveProfile = () => {
    if (isDemo) {
      updateDemoProfile(editData);
    }
    setEditMode(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return dateStr; }
  };

  const formatBirthDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch { return dateStr; }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'consultation': return <Sparkles className="w-4 h-4" style={{ color: '#A78BFA' }} />;
      case 'inscription': return <Star className="w-4 h-4" style={{ color: '#F4C542' }} />;
      default: return <Clock className="w-4 h-4" style={{ color: '#C5A059' }} />;
    }
  };

  const inputStyle = {
    borderColor: 'rgba(197,160,89,0.3)',
    color: 'var(--pa-body)',
    background: 'transparent',
  };

  return (
    <div className="min-h-screen relative pt-20 pb-12 px-4 md:px-8" data-testid="mon-compte-page">
      <SEO path="/mon-compte" />
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-14 h-14 rounded-full flex items-center justify-center" style={{ background: 'rgba(197,160,89,0.1)', border: '1px solid rgba(197,160,89,0.3)' }}>
            <User className="w-6 h-6" style={{ color: '#C5A059' }} strokeWidth={1.5} />
          </div>
          <div>
            <h1 className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
              Mon Compte
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
              {user.email}
              {isDemo && <span className="ml-2 text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(197,160,89,0.15)', color: '#C5A059' }}>Mode découverte</span>}
            </p>
          </div>
        </div>

        {/* Credit balance card */}
        <div className="rounded-2xl p-6 mb-8" style={{ background: 'rgba(197,160,89,0.06)', border: '1px solid rgba(197,160,89,0.15)' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Coins className="w-5 h-5" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <div>
                <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Solde actuel</p>
                <p className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C5A059', fontWeight: 400 }}>{creditBalance} crédits</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/acheter-credits')}
              className="text-xs uppercase tracking-widest px-5 py-2 rounded-full transition-all duration-300 hover:bg-[#C5A059]/10"
              style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }}
            >
              Recharger
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          <Tab active={tab === 'profil'} onClick={() => setTab('profil')} icon={User} label="Profil" />
          <Tab active={tab === 'historique'} onClick={() => setTab('historique')} icon={History} label="Historique" />
          <Tab active={tab === 'journal'} onClick={() => setTab('journal')} icon={Calendar} label="Journal" />
          <Tab active={tab === 'notifications'} onClick={() => setTab('notifications')} icon={Bell} label="Notifications" />
        </div>

        {/* ── Profil Tab ── */}
        {tab === 'profil' && (
          <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)', backdropFilter: 'blur(16px)' }}>
            <div className="flex items-center justify-between mb-6">
              <p className="text-xs uppercase tracking-widest" style={{ color: '#C5A059', letterSpacing: '0.12em' }}>Informations personnelles</p>
              {isDemo && (
                <button
                  onClick={() => editMode ? handleSaveProfile() : setEditMode(true)}
                  className="text-xs uppercase tracking-widest px-4 py-1.5 rounded-full transition-all"
                  style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', letterSpacing: '0.08em' }}
                >
                  {editMode ? 'Enregistrer' : 'Modifier'}
                </button>
              )}
            </div>

            <div className="space-y-5">
              <div>
                <label className="block text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Email</label>
                <p className="text-base" style={{ color: 'var(--pa-body)' }}>{user.email}</p>
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Nom</label>
                {editMode ? (
                  <input type="text" value={editData.name} onChange={e => setEditData({ ...editData, name: e.target.value })} className="w-full bg-transparent border-b py-1 text-base outline-none" style={inputStyle} />
                ) : (
                  <p className="text-base" style={{ color: 'var(--pa-body)' }}>{user.name || '—'}</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Date de naissance</label>
                  {editMode ? (
                    <input type="date" value={editData.birth_date} onChange={e => setEditData({ ...editData, birth_date: e.target.value })} className="w-full bg-transparent border-b py-1 text-base outline-none" style={inputStyle} />
                  ) : (
                    <p className="text-base" style={{ color: 'var(--pa-body)' }}>{user.birth_date ? formatBirthDate(user.birth_date) : '—'}</p>
                  )}
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Heure de naissance</label>
                  {editMode ? (
                    <input type="time" value={editData.birth_time} onChange={e => setEditData({ ...editData, birth_time: e.target.value })} className="w-full bg-transparent border-b py-1 text-base outline-none" style={inputStyle} />
                  ) : (
                    <p className="text-base" style={{ color: 'var(--pa-body)' }}>{user.birth_time || '—'}</p>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Lieu de naissance</label>
                {editMode ? (
                  <input type="text" value={editData.birth_place} onChange={e => setEditData({ ...editData, birth_place: e.target.value })} className="w-full bg-transparent border-b py-1 text-base outline-none" style={inputStyle} />
                ) : (
                  <p className="text-base" style={{ color: 'var(--pa-body)' }}>{user.birth_place || '—'}{user.birth_country ? `, ${user.birth_country}` : ''}</p>
                )}
              </div>
            </div>

            <div className="mt-8 pt-6 flex flex-col sm:flex-row gap-3" style={{ borderTop: '1px solid rgba(197,160,89,0.1)' }}>
              <button
                onClick={handleLogout}
                className="flex items-center justify-center gap-2 text-xs uppercase tracking-widest px-5 py-2.5 rounded-full transition-all duration-300 hover:bg-red-500/10"
                style={{ border: '1px solid rgba(220,38,38,0.3)', color: '#fca5a5', letterSpacing: '0.08em' }}
              >
                <LogOut className="w-3.5 h-3.5" /> Déconnexion
              </button>
            </div>
          </div>
        )}

        {/* ── Historique Tab ── */}
        {tab === 'historique' && (
          <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)', backdropFilter: 'blur(16px)' }}>
            <p className="text-xs uppercase tracking-widest mb-6" style={{ color: '#C5A059', letterSpacing: '0.12em' }}>Historique des consultations</p>
            {history.length === 0 ? (
              <div className="text-center py-12">
                <History className="w-8 h-8 mx-auto mb-4" style={{ color: 'rgba(197,160,89,0.3)' }} strokeWidth={1.5} />
                <p className="text-sm mb-4" style={{ color: 'var(--pa-muted)' }}>Aucune consultation pour le moment</p>
                <button
                  onClick={() => navigate('/tarot-oui-non')}
                  className="text-xs uppercase tracking-widest px-5 py-2 rounded-full transition-all"
                  style={{ border: '1px solid rgba(197,160,89,0.4)', color: '#C5A059', letterSpacing: '0.08em' }}
                >
                  Commencer une consultation
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((item, idx) => (
                  <div key={item.id || idx} className="flex items-center gap-3 p-3 rounded-xl transition-all" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(197,160,89,0.08)' }}>
                    {getTypeIcon(item.type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate" style={{ color: 'var(--pa-body)' }}>
                        {SERVICE_LABELS[item.service] || item.label || item.service}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>{formatDate(item.date)}</p>
                    </div>
                    {item.credits && (
                      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(197,160,89,0.1)', color: '#C5A059' }}>
                        -{item.credits} cr.
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Journal Tab ── */}
        {tab === 'journal' && (
          <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)', backdropFilter: 'blur(16px)' }}>
            <p className="text-xs uppercase tracking-widest mb-6" style={{ color: '#C5A059', letterSpacing: '0.12em' }}>Journal cosmique du jour</p>

            <div className="text-center mb-8">
              <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
                {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
              </p>
              <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
                Votre guidance du jour
              </h2>
            </div>

            <div className="space-y-4 mb-8">
              <button
                onClick={() => navigate('/quotidien')}
                className="w-full text-left p-4 rounded-xl transition-all hover:scale-[1.01]"
                style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.2)' }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Star className="w-5 h-5" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
                    <div>
                      <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Horoscope du jour</p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Énergie, amour, carrière, santé</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
                </div>
              </button>

              <button
                onClick={() => navigate('/tarot-oui-non')}
                className="w-full text-left p-4 rounded-xl transition-all hover:scale-[1.01]"
                style={{ background: 'rgba(232,121,249,0.06)', border: '1px solid rgba(232,121,249,0.2)' }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Sparkles className="w-5 h-5" style={{ color: '#E879F9' }} strokeWidth={1.5} />
                    <div>
                      <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Tirage du jour</p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Posez votre question aux arcanes</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4" style={{ color: '#E879F9' }} strokeWidth={1.5} />
                </div>
              </button>

              <button
                onClick={() => navigate('/numerologie')}
                className="w-full text-left p-4 rounded-xl transition-all hover:scale-[1.01]"
                style={{ background: 'rgba(244,197,66,0.06)', border: '1px solid rgba(244,197,66,0.2)' }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5" style={{ color: '#F4C542' }} strokeWidth={1.5} />
                    <div>
                      <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Numérologie du jour</p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Votre vibration numérique</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4" style={{ color: '#F4C542' }} strokeWidth={1.5} />
                </div>
              </button>
            </div>

            {/* Journal entries from today */}
            {(() => {
              const today = new Date().toISOString().slice(0, 10);
              const todayEntries = history.filter(h => h.date && h.date.startsWith(today));
              if (todayEntries.length === 0) return (
                <div className="text-center py-6" style={{ borderTop: '1px solid rgba(197,160,89,0.1)' }}>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    Aucune activité aujourd'hui — commencez votre journée cosmique ci-dessus
                  </p>
                </div>
              );
              return (
                <div style={{ borderTop: '1px solid rgba(197,160,89,0.1)' }} className="pt-4">
                  <p className="text-xs uppercase tracking-widest mb-3" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Activité du jour</p>
                  <div className="space-y-2">
                    {todayEntries.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs" style={{ color: 'var(--pa-body)' }}>
                        {getTypeIcon(item.type)}
                        <span>{SERVICE_LABELS[item.service] || item.label}</span>
                        <span style={{ color: 'var(--pa-muted)' }}>— {new Date(item.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* ── Notifications Tab ── */}
        {tab === 'notifications' && (
          <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(197,160,89,0.15)', backdropFilter: 'blur(16px)' }}>
            <p className="text-xs uppercase tracking-widest mb-6" style={{ color: '#C5A059', letterSpacing: '0.12em' }}>Notifications quotidiennes</p>

            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {notifPrefs.enabled ? <Bell className="w-5 h-5" style={{ color: '#34D399' }} /> : <BellOff className="w-5 h-5" style={{ color: 'var(--pa-muted)' }} />}
                  <div>
                    <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Journal quotidien</p>
                    <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Recevez votre guidance chaque jour</p>
                  </div>
                </div>
                <button
                  onClick={handleNotifToggle}
                  className="text-xs uppercase tracking-widest px-4 py-1.5 rounded-full transition-all"
                  style={{
                    border: `1px solid ${notifPrefs.enabled ? 'rgba(52,211,153,0.4)' : 'rgba(197,160,89,0.3)'}`,
                    color: notifPrefs.enabled ? '#34D399' : '#C5A059',
                    background: notifPrefs.enabled ? 'rgba(52,211,153,0.08)' : 'transparent',
                    letterSpacing: '0.08em',
                  }}
                >
                  {notifPrefs.enabled ? 'Activé' : 'Activer'}
                </button>
              </div>

              {notifStatus && (
                <p className="text-xs text-center py-2 rounded-lg" style={{ background: 'rgba(197,160,89,0.06)', color: '#C5A059' }}>
                  {notifStatus}
                </p>
              )}

              {notifPrefs.enabled && (
                <div>
                  <label className="block text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Heure de notification</label>
                  <select
                    value={notifPrefs.hour}
                    onChange={e => handleNotifHour(e.target.value)}
                    className="w-full bg-transparent border-b py-2 text-base outline-none"
                    style={{ borderColor: 'rgba(197,160,89,0.3)', color: 'var(--pa-body)', background: '#0C0918' }}
                  >
                    {[6, 7, 8, 9, 10, 11, 12].map(h => (
                      <option key={h} value={h}>{h}h00</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="p-4 rounded-xl" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.15)' }}>
                <div className="flex items-start gap-3">
                  <Shield className="w-4 h-4 mt-0.5" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--pa-heading)' }}>Contenu de la notification</p>
                    <p className="text-xs" style={{ color: 'var(--pa-muted)', lineHeight: '1.6' }}>
                      Chaque jour, vous recevrez un rappel pour consulter votre horoscope, votre énergie cosmique et votre conseil du jour personnalisé.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
