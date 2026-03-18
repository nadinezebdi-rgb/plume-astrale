import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Sparkles, Lock, RefreshCw } from 'lucide-react';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const SIGNES_FR = [
  'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
  'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
];

const TAROT_CARDS = [
  'Le Bateleur', 'La Papesse', "L'Impératrice", "L'Empereur", 'Le Pape',
  "L'Amoureux", 'Le Chariot', 'La Justice', "L'Ermite", 'La Roue de Fortune',
  'La Force', 'Le Pendu', 'La Mort', 'Tempérance', 'Le Diable',
  'La Maison Dieu', "L'Étoile", 'La Lune', 'Le Soleil', 'Le Jugement', 'Le Monde',
];

const getRandomCard = () => TAROT_CARDS[Math.floor(Math.random() * TAROT_CARDS.length)];
const getEnergyScore = () => Math.floor(Math.random() * 40) + 55; // 55-95

const Journal = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [name, setName] = useState('');
  const [sign, setSign] = useState('');
  const [lifePath, setLifePath] = useState('');
  const [isPremium, setIsPremium] = useState(false);
  const [journal, setJournal] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generated, setGenerated] = useState(false);

  // Pre-fill from user data
  useEffect(() => {
    if (user?.name) {
      setName(user.name.split(' ')[0]);
    }
    const data = localStorage.getItem('plume_astrale_data');
    if (data) {
      try {
        const parsed = JSON.parse(data);
        if (parsed.prenom) setName(parsed.prenom);
        if (parsed.dateNaissance) {
          const d = new Date(parsed.dateNaissance);
          const signIdx = getZodiacIndex(d);
          if (signIdx >= 0) setSign(SIGNES_FR[signIdx]);
          setLifePath(String(calculateLifePath(d)));
        }
      } catch (e) { /* ignore */ }
    }
    const premiumPaid = localStorage.getItem('plume_premium_paid');
    if (premiumPaid === 'true') setIsPremium(true);
  }, [user]);

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

  const generateJournal = async () => {
    if (!name.trim() || !sign) {
      setError('Veuillez entrer votre prénom et choisir votre signe.');
      return;
    }

    setLoading(true);
    setError('');
    setJournal('');

    try {
      const res = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          sign,
          lifePath: lifePath ? parseInt(lifePath, 10) : undefined,
          tarotCard: getRandomCard(),
          energyScore: getEnergyScore(),
          isPremium,
        }),
      });

      if (!res.ok) {
        throw new Error('Erreur serveur');
      }

      const data = await res.json();
      setJournal(data.journal);
      setGenerated(true);
    } catch (e) {
      console.error('Journal error:', e);
      setError("Une erreur est survenue lors de la génération de votre journal. Veuillez réessayer.");
    }
    setLoading(false);
  };

  const handleRegenerate = () => {
    setGenerated(false);
    setJournal('');
    generateJournal();
  };

  return (
    <div className="min-h-screen relative">
      <SEO path="/journal-cosmique" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">

          <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
          </button>

          {/* Header */}
          <div className="mb-12">
            <p className="section-label">Guidance personnalisée</p>
            <h1
              className="text-3xl md:text-4xl mb-4"
              style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}
            >
              Journal Cosmique
            </h1>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-muted)', lineHeight: '1.8' }}>
              Un message unique, généré par l'intelligence cosmique, rien que pour vous.
              {isPremium && (
                <span className="inline-flex items-center gap-1 ml-2 text-[#A78BFA]">
                  <Sparkles className="w-3 h-3" /> Premium
                </span>
              )}
            </p>
            <p className="text-xs mt-2" style={{ color: 'var(--pa-muted)', opacity: 0.6 }}>
              {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
            </p>
          </div>

          {/* Form - show when not generated */}
          {!generated && !loading && (
            <div className="space-y-6 mb-10 animate-fade-in">
              {/* Name */}
              <div>
                <label className="text-xs tracking-widest uppercase mb-2 block" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  Votre prénom
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Entrez votre prénom"
                  className="w-full px-4 py-3 text-sm rounded-none transition-all duration-300 focus:outline-none"
                  style={{
                    background: 'rgba(42, 31, 85, 0.5)',
                    border: '1px solid rgba(212,180,106,0.2)',
                    color: 'var(--pa-heading)',
                  }}
                  data-testid="journal-name-input"
                />
              </div>

              {/* Sign selector */}
              <div>
                <label className="text-xs tracking-widest uppercase mb-3 block" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  Votre signe astrologique
                </label>
                <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                  {SIGNES_FR.map(s => (
                    <button
                      key={s}
                      onClick={() => setSign(s)}
                      className="py-2.5 px-2 text-center text-sm transition-all duration-300"
                      style={{
                        border: `1px solid ${sign === s ? 'rgba(212,180,106,0.6)' : 'rgba(212,180,106,0.12)'}`,
                        background: sign === s ? 'rgba(212,180,106,0.08)' : 'transparent',
                        color: sign === s ? 'var(--pa-heading)' : 'var(--pa-muted)',
                      }}
                      data-testid={`journal-sign-${s}`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Life path (optional) */}
              <div>
                <label className="text-xs tracking-widest uppercase mb-2 block" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                  Chemin de vie <span style={{ color: 'var(--pa-muted)', opacity: 0.5 }}>(optionnel)</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="33"
                  value={lifePath}
                  onChange={(e) => setLifePath(e.target.value)}
                  placeholder="Ex: 6"
                  className="w-32 px-4 py-3 text-sm rounded-none transition-all duration-300 focus:outline-none"
                  style={{
                    background: 'rgba(42, 31, 85, 0.5)',
                    border: '1px solid rgba(212,180,106,0.2)',
                    color: 'var(--pa-heading)',
                  }}
                  data-testid="journal-lifepath-input"
                />
              </div>

              {/* Premium toggle */}
              <div
                className="flex items-center gap-3 p-4 transition-all duration-300"
                style={{
                  border: '1px solid rgba(167,139,250,0.2)',
                  background: isPremium ? 'rgba(167,139,250,0.06)' : 'transparent',
                }}
              >
                <button
                  onClick={() => setIsPremium(!isPremium)}
                  className="relative w-10 h-5 rounded-full transition-all duration-300"
                  style={{ background: isPremium ? 'rgba(167,139,250,0.5)' : 'rgba(255,255,255,0.1)' }}
                  data-testid="journal-premium-toggle"
                >
                  <span
                    className="absolute top-0.5 w-4 h-4 rounded-full transition-all duration-300"
                    style={{
                      background: isPremium ? '#A78BFA' : 'rgba(255,255,255,0.3)',
                      left: isPremium ? '22px' : '2px',
                    }}
                  />
                </button>
                <div>
                  <p className="text-sm flex items-center gap-1.5" style={{ color: isPremium ? '#A78BFA' : 'var(--pa-muted)' }}>
                    <Sparkles className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Journal Premium
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--pa-muted)', opacity: 0.6 }}>
                    Guidance détaillée, profondeur émotionnelle, conseils puissants
                  </p>
                </div>
              </div>

              {error && (
                <p className="text-xs" style={{ color: '#C97878' }}>{error}</p>
              )}

              {/* Generate button */}
              <button
                onClick={generateJournal}
                className="w-full py-3.5 text-sm tracking-widest uppercase transition-all duration-500 flex items-center justify-center gap-2"
                style={{
                  border: '1px solid rgba(212,180,106,0.5)',
                  color: '#D4B46A',
                  background: 'rgba(212,180,106,0.08)',
                  letterSpacing: '0.12em',
                  fontWeight: 500,
                }}
                data-testid="journal-generate-btn"
              >
                <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                Générer mon journal cosmique
              </button>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
              <Loader2 className="w-8 h-8 animate-spin mb-6" style={{ color: 'var(--pa-accent)' }} />
              <p className="text-sm" style={{ color: 'var(--pa-muted)', fontStyle: 'italic' }}>
                Les astres composent votre message...
              </p>
            </div>
          )}

          {/* Journal result */}
          {generated && journal && !loading && (
            <div className="animate-fade-in">
              <div
                className="p-8 md:p-10 mb-8"
                style={{
                  border: '1px solid rgba(212,180,106,0.12)',
                  background: 'rgba(42, 31, 85, 0.3)',
                }}
                data-testid="journal-result"
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
                  {journal}
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleRegenerate}
                  className="flex-1 py-3 text-xs tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-2"
                  style={{
                    border: '1px solid rgba(212,180,106,0.3)',
                    color: '#D4B46A',
                    letterSpacing: '0.1em',
                  }}
                  data-testid="journal-regenerate-btn"
                >
                  <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Nouveau journal
                </button>

                {!isPremium && (
                  <button
                    onClick={() => {
                      setIsPremium(true);
                      setGenerated(false);
                      setJournal('');
                    }}
                    className="flex-1 py-3 text-xs tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-2"
                    style={{
                      border: '1px solid rgba(167,139,250,0.4)',
                      color: '#A78BFA',
                      background: 'rgba(167,139,250,0.06)',
                      letterSpacing: '0.1em',
                    }}
                    data-testid="journal-upgrade-btn"
                  >
                    <Lock className="w-3.5 h-3.5" strokeWidth={1.5} />
                    Passer en Premium
                  </button>
                )}
              </div>

              {/* Suggestion */}
              <div className="mt-12 pt-8" style={{ borderTop: '1px solid var(--pa-divider)' }}>
                <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                  Approfondir votre guidance
                </p>
                <button
                  onClick={() => navigate('/tarot-oui-non')}
                  className="block w-full text-left group"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm mb-0.5 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                        Tarot Oui/Non
                      </p>
                      <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>Posez votre question aux arcanes</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Journal;
