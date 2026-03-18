import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, History, Bell, BellOff, Settings, LogOut, Coins, Calendar, ChevronRight, Star, Sparkles, Clock, Shield, Loader2, RefreshCw, Lock, BookOpen } from 'lucide-react';
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

const TAROT_CARDS = [
  'Le Bateleur', 'La Papesse', "L'Impératrice", "L'Empereur", 'Le Pape',
  "L'Amoureux", 'Le Chariot', 'La Justice', "L'Ermite", 'La Roue de Fortune',
  'La Force', 'Le Pendu', 'La Mort', 'Tempérance', 'Le Diable',
  'La Maison Dieu', "L'Étoile", 'La Lune', 'Le Soleil', 'Le Jugement', 'Le Monde',
];

const SIGNES_FR = [
  'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
  'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
];

const getZodiacIndex = (date) => {
  const m = date.getMonth() + 1, d = date.getDate();
  if ((m === 3 && d >= 21) || (m === 4 && d <= 19)) return 0;
  if ((m === 4 && d >= 20) || (m === 5 && d <= 20)) return 1;
  if ((m === 5 && d >= 21) || (m === 6 && d <= 20)) return 2;
  if ((m === 6 && d >= 21) || (m === 7 && d <= 22)) return 3;
  if ((m === 7 && d >= 23) || (m === 8 && d <= 22)) return 4;
  if ((m === 8 && d >= 23) || (m === 9 && d <= 22)) return 5;
  if ((m === 9 && d >= 23) || (m === 10 && d <= 22)) return 6;
  if ((m === 10 && d >= 23) || (m === 11 && d <= 21)) return 7;
  if ((m === 11 && d >= 22) || (m === 12 && d <= 21)) return 8;
  if ((m === 12 && d >= 22) || (m === 1 && d <= 19)) return 9;
  if ((m === 1 && d >= 20) || (m === 2 && d <= 18)) return 10;
  return 11;
};

const calculateLifePath = (date) => {
  const digits = `${date.getFullYear()}${date.getMonth() + 1}${date.getDate()}`;
  let sum = 0;
  for (const ch of digits) sum += parseInt(ch, 10);
  while (sum > 9 && sum !== 11 && sum !== 22 && sum !== 33) {
    let s = 0;
    for (const ch of String(sum)) s += parseInt(ch, 10);
    sum = s;
  }
  return sum;
};

const getRandomCard = () => TAROT_CARDS[Math.floor(Math.random() * TAROT_CARDS.length)];
const getEnergyScore = () => Math.floor(Math.random() * 40) + 55;

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
  const [journalContent, setJournalContent] = useState('');
  const [journalLoading, setJournalLoading] = useState(false);
  const [journalError, setJournalError] = useState('');
  const [journalGenerated, setJournalGenerated] = useState(false);
  const [isPremium, setIsPremium] = useState(false);

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

  // Compute user astral data from profile
  const getUserAstralData = () => {
    const userName = user?.name?.split(' ')[0] || 'Utilisateur';
    let userSign = '';
    let userLifePath = '';

    if (user?.birth_date) {
      try {
        const d = new Date(user.birth_date);
        const signIdx = getZodiacIndex(d);
        if (signIdx >= 0) userSign = SIGNES_FR[signIdx];
        userLifePath = String(calculateLifePath(d));
      } catch (e) { /* ignore */ }
    }

    // Fallback: check localStorage
    if (!userSign) {
      const data = localStorage.getItem('plume_astrale_data');
      if (data) {
        try {
          const parsed = JSON.parse(data);
          if (parsed.dateNaissance) {
            const d = new Date(parsed.dateNaissance);
            const signIdx = getZodiacIndex(d);
            if (signIdx >= 0) userSign = SIGNES_FR[signIdx];
            userLifePath = String(calculateLifePath(d));
          }
        } catch (e) { /* ignore */ }
      }
    }

    return { userName, userSign, userLifePath };
  };

  const generateJournal = async () => {
    const { userName, userSign, userLifePath } = getUserAstralData();

    if (!userSign) {
      setJournalError('Veuillez compléter votre date de naissance dans votre profil pour obtenir votre analyse astrale.');
      return;
    }

    setJournalLoading(true);
    setJournalError('');
    setJournalContent('');

    try {
      const res = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: userName,
          sign: userSign,
          lifePath: userLifePath ? parseInt(userLifePath, 10) : undefined,
          tarotCard: getRandomCard(),
          energyScore: getEnergyScore(),
          isPremium,
        }),
      });

      if (!res.ok) throw new Error('Erreur serveur');

      const data = await res.json();
      setJournalContent(data.journal);
      setJournalGenerated(true);
    } catch (e) {
      console.error('Journal error:', e);
      setJournalError("Une erreur est survenue lors du calcul de votre analyse astrale. Veuillez réessayer.");
    }
    setJournalLoading(false);
  };

  const handleRegenerateJournal = () => {
    setJournalGenerated(false);
    setJournalContent('');
    generateJournal();
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
            <p className="text-xs uppercase tracking-widest mb-2" style={{ color: '#C5A059', letterSpacing: '0.12em' }}>Analyse astrale du jour</p>
            <p className="text-xs mb-6" style={{ color: 'var(--pa-muted)', lineHeight: '1.6' }}>
              Calculée par <span style={{ color: '#C5A059' }}>Astrology API</span> — données astronomiques en temps réel
            </p>

            {/* User astral profile summary */}
            {(() => {
              const { userName, userSign, userLifePath } = getUserAstralData();
              return (
                <div className="flex flex-wrap gap-3 mb-6">
                  {userSign && (
                    <span className="text-xs px-3 py-1.5 rounded-full" style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)', color: '#A78BFA' }}>
                      ☉ {userSign}
                    </span>
                  )}
                  {userLifePath && (
                    <span className="text-xs px-3 py-1.5 rounded-full" style={{ background: 'rgba(244,197,66,0.08)', border: '1px solid rgba(244,197,66,0.2)', color: '#F4C542' }}>
                      Chemin de vie : {userLifePath}
                    </span>
                  )}
                  {user?.birth_date && (
                    <span className="text-xs px-3 py-1.5 rounded-full" style={{ background: 'rgba(197,160,89,0.08)', border: '1px solid rgba(197,160,89,0.15)', color: 'var(--pa-muted)' }}>
                      {formatBirthDate(user.birth_date)}
                    </span>
                  )}
                </div>
              );
            })()}

            {/* Not generated yet */}
            {!journalGenerated && !journalLoading && (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ background: 'rgba(197,160,89,0.06)', border: '1px solid rgba(197,160,89,0.15)' }}>
                  <BookOpen className="w-7 h-7" style={{ color: '#C5A059' }} strokeWidth={1.2} />
                </div>

                <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
                  {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                </p>
                <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 300 }}>
                  Votre analyse astrale personnalisée
                </h2>
                <p className="text-xs mb-6 max-w-md mx-auto" style={{ color: 'var(--pa-muted)', lineHeight: '1.8' }}>
                  Basée sur vos données de naissance et les positions planétaires actuelles, votre analyse est calculée via les algorithmes de la plateforme Astrology API.
                </p>

                {/* Premium toggle */}
                <div
                  className="flex items-center gap-3 p-4 mb-6 mx-auto max-w-sm transition-all duration-300 rounded-xl"
                  style={{
                    border: '1px solid rgba(167,139,250,0.2)',
                    background: isPremium ? 'rgba(167,139,250,0.06)' : 'transparent',
                  }}
                >
                  <button
                    onClick={() => setIsPremium(!isPremium)}
                    className="relative w-10 h-5 rounded-full transition-all duration-300"
                    style={{ background: isPremium ? 'rgba(167,139,250,0.5)' : 'rgba(255,255,255,0.1)' }}
                  >
                    <span
                      className="absolute top-0.5 w-4 h-4 rounded-full transition-all duration-300"
                      style={{
                        background: isPremium ? '#A78BFA' : 'rgba(255,255,255,0.3)',
                        left: isPremium ? '22px' : '2px',
                      }}
                    />
                  </button>
                  <div className="text-left">
                    <p className="text-sm flex items-center gap-1.5" style={{ color: isPremium ? '#A78BFA' : 'var(--pa-muted)' }}>
                      <Sparkles className="w-3.5 h-3.5" strokeWidth={1.5} />
                      Analyse approfondie
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--pa-muted)', opacity: 0.6 }}>
                      Interprétation détaillée des transits et maisons astrales
                    </p>
                  </div>
                </div>

                {journalError && (
                  <p className="text-xs mb-4" style={{ color: '#C97878' }}>{journalError}</p>
                )}

                <button
                  onClick={generateJournal}
                  className="px-8 py-3 text-xs tracking-widest uppercase transition-all duration-500 flex items-center justify-center gap-2 mx-auto rounded-full"
                  style={{
                    border: '1px solid rgba(212,180,106,0.5)',
                    color: '#D4B46A',
                    background: 'rgba(212,180,106,0.08)',
                    letterSpacing: '0.12em',
                    fontWeight: 500,
                  }}
                >
                  <Star className="w-4 h-4" strokeWidth={1.5} />
                  Consulter mon analyse du jour
                </button>
              </div>
            )}

            {/* Loading state */}
            {journalLoading && (
              <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
                <Loader2 className="w-8 h-8 animate-spin mb-6" style={{ color: 'var(--pa-accent)' }} />
                <p className="text-sm mb-1" style={{ color: 'var(--pa-muted)', fontStyle: 'italic' }}>
                  Calculs astraux en cours...
                </p>
                <p className="text-xs" style={{ color: 'var(--pa-muted)', opacity: 0.5 }}>
                  Analyse des positions planétaires via Astrology API
                </p>
              </div>
            )}

            {/* Journal result */}
            {journalGenerated && journalContent && !journalLoading && (
              <div className="animate-fade-in">
                <div
                  className="p-6 md:p-8 mb-6 rounded-xl"
                  style={{
                    border: '1px solid rgba(212,180,106,0.12)',
                    background: 'rgba(42, 31, 85, 0.3)',
                  }}
                >
                  <div
                    className="text-base leading-relaxed whitespace-pre-line"
                    style={{
                      fontFamily: 'Cormorant Garamond, serif',
                      color: 'var(--pa-body)',
                      lineHeight: '2',
                      fontSize: '1.05rem',
                    }}
                  >
                    {journalContent}
                  </div>
                </div>

                {/* Trust badge */}
                <div className="flex items-start gap-3 p-4 mb-6 rounded-xl" style={{ background: 'rgba(197,160,89,0.04)', border: '1px solid rgba(197,160,89,0.1)' }}>
                  <Shield className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: '#C5A059' }} strokeWidth={1.5} />
                  <div>
                    <p className="text-xs" style={{ color: 'var(--pa-muted)', lineHeight: '1.6' }}>
                      Analyse calculée à partir de vos données de naissance et des éphémérides astronomiques fournies par <span style={{ color: '#C5A059' }}>Astrology API</span> — service de calculs astraux de référence utilisé par les professionnels.
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleRegenerateJournal}
                    className="flex-1 py-3 text-xs tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-2 rounded-full"
                    style={{
                      border: '1px solid rgba(212,180,106,0.3)',
                      color: '#D4B46A',
                      letterSpacing: '0.1em',
                    }}
                  >
                    <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Nouvelle analyse
                  </button>

                  {!isPremium && (
                    <button
                      onClick={() => {
                        setIsPremium(true);
                        setJournalGenerated(false);
                        setJournalContent('');
                      }}
                      className="flex-1 py-3 text-xs tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-2 rounded-full"
                      style={{
                        border: '1px solid rgba(167,139,250,0.4)',
                        color: '#A78BFA',
                        background: 'rgba(167,139,250,0.06)',
                        letterSpacing: '0.1em',
                      }}
                    >
                      <Lock className="w-3.5 h-3.5" strokeWidth={1.5} />
                      Analyse approfondie
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Quick access services */}
            {!journalGenerated && !journalLoading && (
              <div className="mt-8 pt-6" style={{ borderTop: '1px solid rgba(197,160,89,0.1)' }}>
                <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--pa-muted)', letterSpacing: '0.1em' }}>Autres consultations</p>
                <div className="space-y-3">
                  <button
                    onClick={() => navigate('/quotidien')}
                    className="w-full text-left p-3 rounded-xl transition-all hover:scale-[1.01]"
                    style={{ background: 'rgba(167,139,250,0.04)', border: '1px solid rgba(167,139,250,0.12)' }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Star className="w-4 h-4" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Horoscope du jour</p>
                      </div>
                      <ChevronRight className="w-4 h-4" style={{ color: '#A78BFA' }} strokeWidth={1.5} />
                    </div>
                  </button>
                  <button
                    onClick={() => navigate('/tarot-oui-non')}
                    className="w-full text-left p-3 rounded-xl transition-all hover:scale-[1.01]"
                    style={{ background: 'rgba(232,121,249,0.04)', border: '1px solid rgba(232,121,249,0.12)' }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Sparkles className="w-4 h-4" style={{ color: '#E879F9' }} strokeWidth={1.5} />
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Tirage du jour</p>
                      </div>
                      <ChevronRight className="w-4 h-4" style={{ color: '#E879F9' }} strokeWidth={1.5} />
                    </div>
                  </button>
                  <button
                    onClick={() => navigate('/numerologie')}
                    className="w-full text-left p-3 rounded-xl transition-all hover:scale-[1.01]"
                    style={{ background: 'rgba(244,197,66,0.04)', border: '1px solid rgba(244,197,66,0.12)' }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4" style={{ color: '#F4C542' }} strokeWidth={1.5} />
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>Numérologie du jour</p>
                      </div>
                      <ChevronRight className="w-4 h-4" style={{ color: '#F4C542' }} strokeWidth={1.5} />
                    </div>
                  </button>
                </div>
              </div>
            )}
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
                    style={{ borderColor: 'rgba(197,160,89,0.3)', color: 'var(--pa-body)', background: '#1A1050' }}
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
