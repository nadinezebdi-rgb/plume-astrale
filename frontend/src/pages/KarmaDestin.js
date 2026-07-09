import React, { useState, useEffect } from 'react';
import PageHero from '@/components/PageHero';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, Sparkles, Moon, Sun, Star, Infinity, ArrowRight, Coins, LogIn } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const KarmaDestin = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [formData, setFormData] = useState({ prenom: '', dateNaissance: '', heureNaissance: '12:00', ville: 'Paris', pays: 'France' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const saved = localStorage.getItem('plume_astrale_data');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        setFormData(prev => ({
          ...prev,
          prenom: data.prenom || prev.prenom,
          dateNaissance: data.dateNaissance || prev.dateNaissance,
          heureNaissance: data.heureNaissance || prev.heureNaissance,
          ville: data.ville || prev.ville,
        }));
      } catch(e) {}
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.prenom || !formData.dateNaissance) return;
    setError('');

    if (!unlocked) {
      try {
        await axios.post(`${API_URL}/api/credits/use`,
          { service_id: 'karma_destin' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await refreshBalance();
        setUnlocked(true);
      } catch (err) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('insuffisants')) { navigate('/acheter-credits'); return; }
        setError(detail || 'Erreur lors de la déduction des crédits');
        return;
      }
    }

    setLoading(true);
    try {
      // Fetch karma-destiny from backend (uses v3 ephemeride internally)
      const birthDate = new Date(formData.dateNaissance);
      const [hh, mm] = (formData.heureNaissance || '12:00').split(':');

      const karmaPromise = fetch(`${API_URL}/api/astrology/karma-destiny`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      }).then(r => r.json()).catch(() => null);

      // Fetch natal positions via v3 (precis Swiss Ephemeris)
      const natalPromise = fetch(`${API_URL}/api/astrology/v3/positions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          person: {
            name: formData.prenom,
            year: birthDate.getFullYear(),
            month: birthDate.getMonth() + 1,
            day: birthDate.getDate(),
            hour: parseInt(hh) || 12,
            minute: parseInt(mm) || 0,
            city: formData.ville,
            country_code: 'FR',
          },
        }),
      }).then(r => r.json()).catch(() => null);

      const [karmaData, natalData] = await Promise.all([karmaPromise, natalPromise]);

      if (karmaData?.success) {
        // Enrich karma with natal positions (Soleil, Lune, Ascendant, autres planetes)
        if (natalData?.success && natalData?.data) {
          const pts = natalData.data.points || natalData.data.positions || natalData.data.planets || [];
          const findSign = (n) => {
            const p = (Array.isArray(pts) ? pts : []).find(x => (x.name || x.point || '').toLowerCase() === n);
            if (!p) return null;
            const signRaw = p.sign || p.position?.sign || '';
            return { signe: signRaw, retrograde: !!(p.retrograde || p.is_retro) };
          };
          karmaData.natal_chart = {
            soleil: findSign('sun') || (karmaData.data.soleil_signe ? { signe: karmaData.data.soleil_signe } : null),
            lune: findSign('moon') || (karmaData.data.lune_signe ? { signe: karmaData.data.lune_signe } : null),
            ascendant: findSign('ascendant'),
            planetes: (Array.isArray(pts) ? pts : []).slice(0, 9).map(p => ({
              nom: p.name || p.point || '',
              signe: p.sign || p.position?.sign || '',
              retrograde: !!(p.retrograde || p.is_retro),
            })),
          };
        } else if (karmaData.data?.soleil_signe || karmaData.data?.lune_signe) {
          karmaData.natal_chart = {
            soleil: karmaData.data.soleil_signe ? { signe: karmaData.data.soleil_signe } : null,
            lune: karmaData.data.lune_signe ? { signe: karmaData.data.lune_signe } : null,
            ascendant: null,
            planetes: [],
          };
        }
        setResult(karmaData);
      } else {
        setError(karmaData?.detail || 'Une erreur est survenue. Veuillez réessayer.');
      }
    } catch (e) {
      setError('Une erreur est survenue. Veuillez réessayer.');
    }
    setLoading(false);
  };

  // ── Section éducative ───────────────────────────────────────────────────────
  const InfoCard = ({ icon, title, desc, color }) => (
    <div className="flex gap-4 items-start p-4 rounded-xl transition-all duration-300"
         style={{ background: 'rgba(255,255,255,0.02)', border: `1px solid ${color}18` }}>
      <div className="mt-0.5 text-xl flex-shrink-0">{icon}</div>
      <div>
        <h4 className="text-sm mb-1 font-medium" style={{ color }}>{title}</h4>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>{desc}</p>
      </div>
    </div>
  );

  // ── Gate non connecté ───────────────────────────────────────────────────────
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative">
      <PageHero
        image="/images/astrale/image-astrale-4.jpg"
        title="Karma & Destin"
        subtitle="Nœud Nord · Mission karmique · Chemin de vie"
      />
        <SEO path="/karma-destin" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
            </button>
            <div className="mb-10">
              <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Lecture Akashique</p>
              <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
                Karma & Destin
              </h1>
              <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
                Découvrez votre karma karmique, votre mission de vie et vos nœuds lunaires
              </p>
            </div>
            <div className="rounded-2xl p-8 text-center" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <LogIn className="w-9 h-9 mx-auto mb-5" style={{ color: '#B8961F' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Connexion requise</h2>
              <p className="text-sm mb-1" style={{ color: 'var(--pa-muted)' }}>Connectez-vous pour accéder à votre lecture Karma & Destin.</p>
              <p className="text-sm mb-7" style={{ color: '#B8961F' }}>15 crédits · 20 crédits offerts à l'inscription</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full hover:bg-[rgba(184,150,31,0.08)] transition-all" style={{ border: '1px solid rgba(184,150,31,0.5)', color: '#B8961F', letterSpacing: '0.1em' }}>Se connecter</button>
                <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full transition-all" style={{ border: '1px solid #B8961F', color: '#0C0918', background: '#B8961F', letterSpacing: '0.1em', fontWeight: 600 }}>Créer un compte</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <SEO path="/karma-destin" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">

          <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
          </button>

          {/* En-tête */}
          <div className="mb-10">
            <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Lecture Akashique</p>
            <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
              Karma &amp; Destin
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
              Plongez dans les archives akashiques de votre âme pour révéler votre karma, votre mission de vie et vos nœuds lunaires
            </p>
          </div>

          {/* Section éducative */}
          {!result && !showForm && (
            <div className="space-y-8 mb-10 animate-fade-in">
              <div className="space-y-3">
                <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                  Qu'est-ce que la lecture Karma & Destin ?
                </h2>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.9' }}>
                  Chaque âme arrive sur Terre avec un programme précis : des dettes karmiques à solder, des leçons à intégrer et une mission unique à accomplir. Cette lecture décode ce programme à partir de votre date et heure de naissance.
                </p>
              </div>

              <div className="space-y-3">
                {[
                  { icon: '☿', title: 'Votre Karma Principal', desc: 'Le thème karmique central de cette incarnation — ce que votre âme est venue guérir, transformer ou apprendre.', color: '#A78BFA' },
                  { icon: '✦', title: 'Mission de Vie', desc: 'Votre raison d\'être profonde dans cette vie. Ce que l\'univers attend de vous spécifiquement.', color: '#B8961F' },
                  { icon: '☽', title: 'Nœuds Lunaires', desc: 'Le Nœud Nord indique votre direction évolutive ; le Nœud Sud révèle vos acquis des vies passées à dépasser.', color: '#6BB5E8' },
                  { icon: '∞', title: 'Don Caché', desc: 'Le talent naturel que vous portez depuis des vies et qui, une fois conscientisé, devient votre plus grande force.', color: '#7CB88A' },
                ].map((item, i) => (
                  <InfoCard key={i} {...item} />
                ))}
              </div>

              {/* CTA */}
              <div className="text-center pt-4">
                <p className="text-sm mb-5" style={{ color: 'var(--pa-muted)' }}>
                  <Coins className="w-4 h-4 inline mr-1" style={{ color: '#B8961F' }} strokeWidth={1.5} />
                  <span style={{ color: '#B8961F' }}>15 crédits</span> · Solde actuel : {creditBalance} crédits
                </p>
                <button
                  onClick={() => setShowForm(true)}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-xl text-sm tracking-widest uppercase transition-all duration-300"
                  style={{ background: '#B8961F', color: '#0C0918', fontWeight: 600, letterSpacing: '0.12em' }}
                >
                  <Sparkles className="w-4 h-4" />
                  Révéler mon Karma & Destin
                </button>
              </div>
            </div>
          )}

          {/* Formulaire */}
          {showForm && !result && (
            <div className="rounded-2xl p-6 md:p-8 mb-8 animate-fade-in" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <h2 className="text-xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Vos données de naissance
              </h2>
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Prénom</label>
                  <input type="text" value={formData.prenom} onChange={e => setFormData(p => ({...p, prenom: e.target.value}))}
                    placeholder="Votre prénom"
                    className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
                    style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Date de naissance</label>
                    <input type="date" value={formData.dateNaissance} onChange={e => setFormData(p => ({...p, dateNaissance: e.target.value}))}
                      className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
                      style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                  </div>
                  <div>
                    <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Heure de naissance</label>
                    <input type="time" value={formData.heureNaissance} onChange={e => setFormData(p => ({...p, heureNaissance: e.target.value}))}
                      className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
                      style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                  </div>
                </div>
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Ville de naissance</label>
                  <input type="text" value={formData.ville} onChange={e => setFormData(p => ({...p, ville: e.target.value}))}
                    placeholder="Ex : Lyon"
                    className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
                    style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                </div>
                {error && <p className="text-xs" style={{ color: '#fca5a5' }}>{error}</p>}
                <button type="submit" disabled={loading || !formData.prenom || !formData.dateNaissance}
                  className="w-full flex items-center justify-center gap-3 py-4 rounded-xl text-sm tracking-widest uppercase transition-all duration-300 disabled:opacity-30"
                  style={{ background: '#B8961F', color: '#0C0918', fontWeight: 600, letterSpacing: '0.12em' }}>
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Consultation des archives akashiques...</> : <><Sparkles className="w-4 h-4" /> Révéler mon Karma & Destin (15 crédits)</>}
                </button>
              </form>
            </div>
          )}

          {/* ── RÉSULTATS ── */}
          {result && (
            <div className="space-y-6 animate-fade-in">

              {/* Karma Principal */}
              {result.data?.karma_principal && (
                <div className="rounded-2xl p-6 md:p-8" style={{ background: 'var(--pa-surface)', border: '1px solid rgba(167,139,250,0.25)' }}>
                  <div className="flex items-center gap-3 mb-5">
                    <span className="text-3xl">{result.data.karma_principal.icon}</span>
                    <div>
                      <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#A78BFA', letterSpacing: '0.12em' }}>Karma Principal</p>
                      <h2 className="text-xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                        {result.data.karma_principal.theme}
                      </h2>
                    </div>
                  </div>
                  <p className="text-base mb-5" style={{ color: 'var(--pa-body)', lineHeight: '1.9', fontFamily: 'Cormorant Garamond, serif', fontSize: '16px' }}>
                    {result.data.karma_principal.description}
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.15)' }}>
                      <p className="text-xs uppercase tracking-widest mb-2" style={{ color: '#A78BFA', letterSpacing: '0.1em' }}>Leçon de vie</p>
                      <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: 1.7 }}>{result.data.karma_principal.lecon}</p>
                    </div>
                    <div className="p-4 rounded-xl" style={{ background: 'rgba(124,184,138,0.06)', border: '1px solid rgba(124,184,138,0.15)' }}>
                      <p className="text-xs uppercase tracking-widest mb-2" style={{ color: '#7CB88A', letterSpacing: '0.1em' }}>Don caché</p>
                      <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: 1.7 }}>{result.data.karma_principal.don_cache}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Mission de vie */}
              {result.data?.mission_de_vie && (
                <div className="rounded-2xl p-6 md:p-8" style={{ background: 'var(--pa-surface)', border: '1px solid rgba(184,150,31,0.25)' }}>
                  <p className="text-xs tracking-widest uppercase mb-2" style={{ color: '#B8961F', letterSpacing: '0.12em' }}>✦ Mission de Vie</p>
                  <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                    {result.data.mission_de_vie.mission}
                  </h2>
                  <p className="text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.95', fontFamily: 'Cormorant Garamond, serif', fontSize: '16px' }}>
                    {result.data.mission_de_vie.description}
                  </p>
                </div>
              )}

              {/* Nœuds lunaires */}
              {result.data?.noeuds_lunaires && (
                <div className="rounded-2xl p-6 md:p-8" style={{ background: 'var(--pa-surface)', border: '1px solid rgba(107,181,232,0.25)' }}>
                  <div className="flex items-center gap-2 mb-4">
                    <Moon className="w-5 h-5" style={{ color: '#6BB5E8' }} strokeWidth={1.5} />
                    <p className="text-xs tracking-widest uppercase" style={{ color: '#6BB5E8', letterSpacing: '0.12em' }}>Nœuds Lunaires</p>
                  </div>
                  <p className="text-sm mb-1" style={{ color: '#B8961F', fontWeight: 500 }}>
                    Nœud Nord en {result.data.noeuds_lunaires.noeud_nord}
                  </p>
                  <p className="text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9', fontFamily: 'Cormorant Garamond, serif', fontSize: '16px' }}>
                    {result.data.noeuds_lunaires.message}
                  </p>
                </div>
              )}

              {/* Nombre karmique + message akashique */}
              {result.data?.message_akashique && (
                <div className="rounded-2xl p-6 md:p-8" style={{ background: 'rgba(184,150,31,0.04)', border: '1px solid rgba(184,150,31,0.15)' }}>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="w-12 h-12 rounded-full flex items-center justify-center text-xl font-light flex-shrink-0"
                      style={{ background: 'rgba(184,150,31,0.12)', border: '1px solid rgba(184,150,31,0.3)', color: '#B8961F', fontFamily: 'Cormorant Garamond, serif' }}>
                      {result.data.nombre_karmique}
                    </span>
                    <p className="text-xs tracking-widest uppercase" style={{ color: '#B8961F', letterSpacing: '0.12em' }}>Message des Archives Akashiques</p>
                  </div>
                  <p className="text-base" style={{ color: 'var(--pa-body)', lineHeight: '1.9', fontFamily: 'Cormorant Garamond, serif', fontSize: '16px', fontStyle: 'italic' }}>
                    « {result.data.message_akashique} »
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4">

              {/* Natal Chart from Astrology API */}
              {result.natal_chart && (
                <div className="rounded-2xl p-6 md:p-8 w-full" style={{ background: 'var(--pa-surface)', border: '1px solid rgba(184,150,31,0.2)' }}>
                  <p className="text-xs tracking-widest uppercase mb-4" style={{ color: '#B8961F', letterSpacing: '0.12em' }}>
                    ☿ Carte Natale — Astrology API
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    {result.natal_chart.soleil && (
                      <div className="p-3 rounded-xl" style={{ background: 'rgba(184,150,31,0.06)', border: '1px solid rgba(184,150,31,0.15)' }}>
                        <p className="text-xs uppercase tracking-widest mb-1" style={{ color: '#B8961F' }}>☉ Soleil</p>
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>{result.natal_chart.soleil.signe}</p>
                      </div>
                    )}
                    {result.natal_chart.lune && (
                      <div className="p-3 rounded-xl" style={{ background: 'rgba(107,181,232,0.06)', border: '1px solid rgba(107,181,232,0.15)' }}>
                        <p className="text-xs uppercase tracking-widest mb-1" style={{ color: '#6BB5E8' }}>☽ Lune</p>
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>{result.natal_chart.lune.signe}</p>
                      </div>
                    )}
                    {result.natal_chart.ascendant && (
                      <div className="p-3 rounded-xl" style={{ background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.15)' }}>
                        <p className="text-xs uppercase tracking-widest mb-1" style={{ color: '#A78BFA' }}>↑ Ascendant</p>
                        <p className="text-sm" style={{ color: 'var(--pa-heading)' }}>{result.natal_chart.ascendant.signe}</p>
                      </div>
                    )}
                  </div>
                  {result.natal_chart.planetes && (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {result.natal_chart.planetes.slice(0, 9).map((p, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs" style={{ color: 'var(--pa-body)' }}>
                          <span style={{ color: '#B8961F' }}>{p.nom}</span>
                          <span style={{ color: 'var(--pa-muted)' }}>→</span>
                          <span>{p.signe}</span>
                          {p.retrograde && <span className="text-red-400">℞</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              </div>
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <button onClick={() => { setResult(null); setShowForm(true); setUnlocked(false); }}
                  className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest transition-all hover:bg-[rgba(184,150,31,0.08)]"
                  style={{ border: '1px solid rgba(184,150,31,0.3)', color: '#B8961F', letterSpacing: '0.12em' }}>
                  Nouvelle consultation
                </button>
                <button onClick={() => navigate('/numerologie')}
                  className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest transition-all"
                  style={{ border: '1px solid #B8961F', color: '#0C0918', background: '#B8961F', fontWeight: 600, letterSpacing: '0.12em' }}>
                  Numérologie approfondie
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KarmaDestin;
