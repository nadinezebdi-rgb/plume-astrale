import React, { useState } from 'react';
import PageHero from '@/components/PageHero';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight, Coins, LogIn, Hash, Sparkles, BookOpen, Star, Heart, Shield, Zap, Target } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ── Descriptions locales enrichies par nombre ──────────────────────────────
const DESCRIPTIONS_LOCALES = {
  chemin: {
    1: { titre: "Le Pionnier", texte: "Votre chemin de vie 1 vous destine à ouvrir de nouvelles voies. L'indépendance, le leadership et l'originalité sont vos maîtres-mots. Vous êtes ici pour montrer aux autres qu'il est possible de penser différemment et d'agir selon sa propre vérité." },
    2: { titre: "Le Diplomate", texte: "Votre chemin de vie 2 vous appelle à créer l'harmonie et la paix. Vous avez un don naturel pour sentir les besoins des autres et tisser des liens. Votre force n'est pas dans l'action solitaire, mais dans la co-création et la réconciliation." },
    3: { titre: "L'Artiste Solaire", texte: "Votre chemin de vie 3 rayonne de créativité et d'expression. Vous êtes né(e) pour partager joie, beauté et inspiration. Que ce soit par les mots, l'art, la musique ou la présence — votre énergie illumine ceux qui vous entourent." },
    4: { titre: "Le Bâtisseur", texte: "Votre chemin de vie 4 est celui de la fondation et de la solidité. Vous avez la capacité rare de transformer les visions en réalités concrètes. La discipline et la persévérance sont vos alliées les plus puissantes." },
    5: { titre: "L'Aventurier", texte: "Votre chemin de vie 5 est un appel à la liberté et à l'exploration. Vous vous épanouissez dans le mouvement, le changement et la diversité. Chaque expérience est une leçon précieuse sur votre chemin d'évolution." },
    6: { titre: "Le Guérisseur", texte: "Votre chemin de vie 6 est consacré à l'amour, au soin et à la responsabilité. Vous portez naturellement les autres dans votre cœur. Votre mission est de créer des espaces de beauté, d'harmonie et de guérison." },
    7: { titre: "Le Sage", texte: "Votre chemin de vie 7 est celui de la connaissance profonde et de la quête spirituelle. Vous avez besoin de solitude pour vous ressourcer et approfondir votre compréhension du monde invisible." },
    8: { titre: "Le Manifesteur", texte: "Votre chemin de vie 8 vous appelle à maîtriser le monde matériel avec sagesse. Vous avez le pouvoir d'attirer l'abondance et d'exercer une influence considérable. La clé : agir en service de quelque chose de plus grand que vous." },
    9: { titre: "L'Humanitaire", texte: "Votre chemin de vie 9 est celui du don universel. Vous portez en vous la sagesse de nombreuses vies et êtes ici pour partager, guérir et aider à l'évolution collective. Apprendre à lâcher prise est votre plus grande leçon." },
    11: { titre: "L'Illuminé", texte: "Votre chemin maître 11 est rare et puissant. Vous êtes un canal de lumière spirituelle, ici pour inspirer et éveiller les consciences. Votre sensibilité extrême est à la fois votre défi et votre plus grand don." },
    22: { titre: "Le Maître Bâtisseur", texte: "Votre chemin maître 22 vous confère un potentiel de réalisation exceptionnel. Vous pouvez concrétiser des rêves à grande échelle et laisser une empreinte durable dans le monde." },
    33: { titre: "Le Maître Guérisseur", texte: "Votre chemin maître 33 est celui de l'amour inconditionnel et de l'enseignement par l'exemple. Rare et précieux, il demande une grande dévotion envers l'évolution de l'âme collective." },
  },
  ame: {
    1: "Votre âme aspire à l'autonomie totale et à l'originalité. Ce qui vous fait vibrer profondément, c'est d'être unique, de tracer votre propre chemin sans dépendre de personne.",
    2: "Votre âme cherche la connexion intime et l'harmonie. Ce que vous désirez le plus profondément, c'est d'être vraiment compris(e) et d'appartenir à quelque chose de beau.",
    3: "Votre âme veut s'exprimer librement et répandre de la joie. Ce qui vous nourrit vraiment, c'est créer, rire, partager et voir les autres s'illuminer grâce à vous.",
    4: "Votre âme aspire à la stabilité et à la construction durable. Au fond de vous, vous voulez créer quelque chose qui durera — une œuvre, une famille, un héritage.",
    5: "Votre âme est assoiffée de liberté et d'expériences variées. Ce qui vous fait vibrer, c'est la nouveauté, les voyages intérieurs ou extérieurs, et la diversité des rencontres.",
    6: "Votre âme est mue par l'amour et le désir de prendre soin. Ce qui vous comble profondément, c'est nourrir, embellir et protéger ceux que vous aimez.",
    7: "Votre âme cherche la vérité cachée et la profondeur. Vous désirez comprendre ce que les autres ne voient pas et trouver le sens ultime de votre existence.",
    8: "Votre âme désire le pouvoir utilisé avec sagesse et l'abondance méritée. Vous voulez avoir un impact réel et tangible dans le monde matériel.",
    9: "Votre âme aspire à la transcendance et au service universel. Ce qui vous comble, c'est de contribuer à quelque chose de plus grand que vous.",
  },
  expression: {
    1: "Vous vous exprimez avec autorité et originalité. Le monde vous perçoit comme un(e) leader naturel(le) et une source d'inspiration.",
    2: "Vous exprimez une douceur et une sensibilité remarquables. Vous êtes perçu(e) comme un(e) médiateur(trice) et une présence apaisante.",
    3: "Vous vous exprimez avec charme, créativité et enthousiasme. Votre présence est lumineuse et communicative — les gens vous trouvent naturellement magnétique.",
    4: "Vous vous exprimez avec sérieux, fiabilité et compétence. Le monde vous perçoit comme quelqu'un de sérieux et de digne de confiance.",
    5: "Vous vous exprimez avec énergie, curiosité et liberté. Vous êtes perçu(e) comme quelqu'un de dynamique, d'adaptable et toujours en mouvement.",
    6: "Vous vous exprimez avec chaleur, soin et responsabilité. Le monde vous voit comme une personne bienveillante et fiable sur laquelle on peut compter.",
    7: "Vous vous exprimez avec profondeur, mystère et intelligence. Vous êtes perçu(e) comme quelqu'un d'introverti mais profondément sage.",
    8: "Vous vous exprimez avec ambition, efficacité et autorité naturelle. Le monde vous perçoit comme quelqu'un de capable et déterminé.",
    9: "Vous vous exprimez avec générosité, sagesse et compassion. Le monde vous voit comme une âme sage et altruiste.",
  },
};

const Numerologie = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [formData, setFormData] = useState({ prenom: '', dateNaissance: '', heureNaissance: '12:00', ville: 'Paris' });
  const [result, setResult] = useState(null);
  const [deepResult, setDeepResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingDeep, setLoadingDeep] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [activeTab, setActiveTab] = useState('base'); // 'base' | 'deep'

  React.useEffect(() => {
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

    if (!unlocked) {
      try {
        await axios.post(`${API_URL}/api/credits/use`,
          { service_id: 'numerologie' },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await refreshBalance();
        setUnlocked(true);
      } catch (err) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('insuffisants')) { navigate('/acheter-credits'); return; }
        alert(detail || 'Erreur');
        return;
      }
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/numerology/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.success) setResult(data.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const handleDeepProfile = async () => {
    setLoadingDeep(true);
    try {
      const res = await fetch(`${API_URL}/api/numerology/deep-profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.success) {
        setDeepResult(data.data);
        setActiveTab('deep');
      }
    } catch (e) { console.error(e); }
    setLoadingDeep(false);
  };

  // ── Couleurs par nombre ──────────────────────────────────────────────────────
  const numColor = (n) => {
    const colors = { 1:'#F87171',2:'#60A5FA',3:'#FBBF24',4:'#34D399',5:'#A78BFA',6:'#F472B6',7:'#38BDF8',8:'#FB923C',9:'#A3E635',11:'#E879F9',22:'#D4AF37',33:'#FDE68A' };
    return colors[n] || '#D4AF37';
  };

  // ── Helper: obtenir description FR pour un nombre ──────────────────────────
  const getLocalDesc = (type, nombre) => {
    if (!nombre) return null;
    return DESCRIPTIONS_LOCALES[type]?.[nombre] || null;
  };

  // ── Carte de nombre ──────────────────────────────────────────────────────────
  const NombreCard = ({ label, nombre, descApi, localDesc, icon, color }) => {
    const col = color || numColor(nombre);
    const titre = typeof localDesc === 'object' ? localDesc?.titre : null;
    const texte = typeof localDesc === 'object' ? localDesc?.texte : (typeof localDesc === 'string' ? localDesc : descApi);
    return (
      <div className="rounded-2xl p-5 md:p-6 transition-all duration-300"
           style={{ background: 'var(--pa-surface)', border: `1px solid ${col}20` }}>
        <div className="flex items-start gap-4 mb-4">
          <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-2xl font-light"
               style={{ background: `${col}15`, border: `2px solid ${col}40`, color: col, fontFamily: 'Cormorant Garamond, serif' }}>
            {nombre || '?'}
          </div>
          <div>
            <p className="text-xs tracking-widest uppercase mb-1" style={{ color, letterSpacing: '0.1em' }}>{label}</p>
            {titre && <h3 className="text-lg" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>{titre}</h3>}
          </div>
        </div>
        {texte && <p className="text-sm leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.85' }}>{texte}</p>}
      </div>
    );
  };

  // ── Gate non connecté ────────────────────────────────────────────────────────
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative">
      <PageHero
        image="/images/astrale/image-astrale-7.jpg"
        title="Numérologie"
        subtitle="Chiffres de vie · Destin · Âme · Personnalité"
      />
        <SEO path="/numerologie" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
            </button>
            <div className="mb-10">
              <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Science des Nombres</p>
              <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
                Numérologie — Chemin d'Âme
              </h1>
              <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
                Découvrez les nombres sacrés qui révèlent votre mission de vie
              </p>
            </div>
            <div className="rounded-2xl p-8 text-center" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <LogIn className="w-9 h-9 mx-auto mb-5" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Connexion requise</h2>
              <p className="text-sm mb-1" style={{ color: 'var(--pa-muted)' }}>Connectez-vous pour accéder à votre profil numérologique.</p>
              <p className="text-sm mb-7" style={{ color: '#D4AF37' }}>10 crédits · 20 crédits offerts à l'inscription</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full hover:bg-[rgba(212,175,55,0.08)] transition-all" style={{ border: '1px solid rgba(212,175,55,0.5)', color: '#D4AF37', letterSpacing: '0.1em' }}>Se connecter</button>
                <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-7 py-3 rounded-full transition-all" style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', letterSpacing: '0.1em', fontWeight: 600 }}>Créer un compte</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <SEO path="/numerologie" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
        <div className="max-w-2xl mx-auto">

          <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12 flex items-center gap-2">
            <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
          </button>

          {/* En-tête */}
          <div className="mb-10">
            <p className="text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.14em' }}>Science des Nombres</p>
            <h1 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)', lineHeight: 1.15 }}>
              Numérologie — Chemin d'Âme
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)', lineHeight: 1.8 }}>
              Découvrez les nombres sacrés qui révèlent votre mission de vie, vos désirs profonds et vos talents cachés
            </p>
          </div>

          {/* Info crédits */}
          <div className="mb-8 flex items-center gap-2">
            <Coins className="w-4 h-4 flex-shrink-0" style={{ color: '#D4AF37' }} strokeWidth={1.5} />
            <span className="text-xs" style={{ color: 'var(--pa-accent)', letterSpacing: '0.08em' }}>
              10 crédits · Solde : {creditBalance} crédits
            </span>
          </div>

          {/* Section éducative */}
          {!result && !showForm && (
            <div className="space-y-8 mb-10 animate-fade-in">
              <div>
                <h2 className="text-xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Les 6 nombres de votre profil</h2>
                <div className="space-y-3">
                  {[
                    { icon: <Star className="w-4 h-4" strokeWidth={1.5} />, title: 'Chemin de Vie', desc: 'Le nombre le plus important. Calculé à partir de votre date de naissance, il révèle votre mission fondamentale et les leçons à apprendre dans cette vie.', color: '#A78BFA' },
                    { icon: <Heart className="w-4 h-4" strokeWidth={1.5} />, title: "Nombre de l'Âme", desc: 'Dérivé des voyelles de votre prénom, il exprime vos désirs les plus profonds et ce que votre âme cherche véritablement.', color: '#C97878' },
                    { icon: <BookOpen className="w-4 h-4" strokeWidth={1.5} />, title: "Nombre d'Expression", desc: 'Calculé à partir de toutes les lettres de votre prénom, il décrit vos talents naturels et l\'image que vous projetez dans le monde.', color: '#7CB88A' },
                    { icon: <Shield className="w-4 h-4" strokeWidth={1.5} />, title: 'Nombres Défis', desc: 'Les obstacles spécifiques que vous êtes venu(e) surmonter. Connaître ses défis, c\'est avoir la moitié de la solution.', color: '#6BB5E8' },
                    { icon: <Sparkles className="w-4 h-4" strokeWidth={1.5} />, title: 'Année Personnelle 2026', desc: "Ce cycle annuel révèle l'énergie dominante de votre année en cours et les thèmes à travailler.", color: '#D4AF37' },
                    { icon: <Zap className="w-4 h-4" strokeWidth={1.5} />, title: 'Nombre de Personnalité', desc: 'La première impression que vous laissez aux autres — votre façade naturelle et votre magnétisme social.', color: '#FB923C' },
                  ].map((item, i) => (
                    <div key={i} className="flex gap-4 items-start p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)', border: `1px solid ${item.color}15` }}>
                      <div className="mt-0.5" style={{ color: item.color }}>{item.icon}</div>
                      <div>
                        <h4 className="text-sm mb-1 font-medium" style={{ color: item.color }}>{item.title}</h4>
                        <p className="text-xs leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '1.8' }}>{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* CTA */}
              <div className="text-center pt-4">
                <button onClick={() => setShowForm(true)}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-xl text-sm tracking-widest uppercase transition-all duration-300"
                  style={{ background: '#D4AF37', color: '#111625', fontWeight: 600, letterSpacing: '0.12em' }}>
                  <Hash className="w-4 h-4" />
                  Découvrir mon profil numérologique
                </button>
              </div>
            </div>
          )}

          {/* Formulaire */}
          {showForm && !result && (
            <div className="rounded-2xl p-6 md:p-8 mb-8 animate-fade-in" style={{ background: 'var(--pa-surface)', border: '1px solid var(--pa-divider)' }}>
              <h2 className="text-xl mb-6" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>Vos données de naissance</h2>
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Prénom</label>
                  <input type="text" value={formData.prenom} onChange={e => setFormData(p => ({...p, prenom: e.target.value}))}
                    placeholder="Votre prénom complet"
                    className="w-full rounded-xl px-4 py-3 text-sm outline-none"
                    style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Date de naissance</label>
                    <input type="date" value={formData.dateNaissance} onChange={e => setFormData(p => ({...p, dateNaissance: e.target.value}))}
                      className="w-full rounded-xl px-4 py-3 text-sm outline-none"
                      style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                  </div>
                  <div>
                    <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Heure de naissance</label>
                    <input type="time" value={formData.heureNaissance} onChange={e => setFormData(p => ({...p, heureNaissance: e.target.value}))}
                      className="w-full rounded-xl px-4 py-3 text-sm outline-none"
                      style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                  </div>
                </div>
                <div>
                  <label className="block text-xs tracking-widest uppercase mb-2" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>Ville de naissance</label>
                  <input type="text" value={formData.ville} onChange={e => setFormData(p => ({...p, ville: e.target.value}))}
                    placeholder="Ex : Bordeaux"
                    className="w-full rounded-xl px-4 py-3 text-sm outline-none"
                    style={{ background: 'var(--pa-bg)', border: '1px solid var(--pa-divider)', color: 'var(--pa-body)' }} />
                </div>
                <button type="submit" disabled={loading || !formData.prenom || !formData.dateNaissance}
                  className="w-full flex items-center justify-center gap-3 py-4 rounded-xl text-sm tracking-widest uppercase transition-all disabled:opacity-30"
                  style={{ background: '#D4AF37', color: '#111625', fontWeight: 600, letterSpacing: '0.12em' }}>
                  {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Calcul des nombres sacrés...</> : <><Hash className="w-4 h-4" /> Calculer mon profil (10 crédits)</>}
                </button>
              </form>
            </div>
          )}

          {/* ── RÉSULTATS ── */}
          {result && (
            <div className="animate-fade-in">

              {/* Onglets Base / Approfondi */}
              <div className="flex gap-1 mb-8 p-1 rounded-xl" style={{ background: 'var(--pa-surface)' }}>
                {[
                  { key: 'base', label: 'Profil de base' },
                  { key: 'deep', label: '✦ Profil approfondi' },
                ].map(tab => (
                  <button key={tab.key} onClick={() => { setActiveTab(tab.key); if (tab.key === 'deep' && !deepResult) handleDeepProfile(); }}
                    className="flex-1 py-3 rounded-lg text-xs uppercase tracking-widest transition-all duration-300"
                    style={{
                      background: activeTab === tab.key ? '#D4AF37' : 'transparent',
                      color: activeTab === tab.key ? '#111625' : 'var(--pa-muted)',
                      fontWeight: activeTab === tab.key ? 600 : 400,
                      letterSpacing: '0.1em',
                    }}>
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* ── Onglet BASE ── */}
              {activeTab === 'base' && (
                <div className="space-y-5">
                  {/* Chemin de vie — le plus important */}
                  {result.chemin_de_vie?.nombre && (
                    <NombreCard
                      label="✦ Chemin de Vie"
                      nombre={result.chemin_de_vie.nombre}
                      localDesc={getLocalDesc('chemin', result.chemin_de_vie.nombre)}
                      descApi={result.chemin_de_vie.description}
                      color="#A78BFA"
                    />
                  )}
                  {/* Grille des autres nombres */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.nombre_ame?.nombre && (
                      <NombreCard label="Nombre de l'Âme" nombre={result.nombre_ame.nombre}
                        localDesc={getLocalDesc('ame', result.nombre_ame.nombre)}
                        descApi={result.nombre_ame.description} color="#C97878" />
                    )}
                    {result.nombre_expression?.nombre && (
                      <NombreCard label="Nombre d'Expression" nombre={result.nombre_expression.nombre}
                        localDesc={getLocalDesc('expression', result.nombre_expression.nombre)}
                        descApi={result.nombre_expression.description} color="#7CB88A" />
                    )}
                    {result.nombre_personnalite?.nombre && (
                      <NombreCard label="Nombre de Personnalité" nombre={result.nombre_personnalite.nombre}
                        descApi={result.nombre_personnalite.description} color="#FB923C" />
                    )}
                    {result.nombre_anniversaire?.nombre && (
                      <NombreCard label="Nombre d'Anniversaire" nombre={result.nombre_anniversaire.nombre}
                        descApi={result.nombre_anniversaire.description} color="#6BB5E8" />
                    )}
                  </div>
                  {/* Année personnelle 2026 */}
                  {result.annee_personnelle_2026 && (
                    <div className="rounded-2xl p-5" style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.18)' }}>
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-2xl font-light" style={{ color: '#D4AF37', fontFamily: 'Cormorant Garamond, serif' }}>
                          {result.annee_personnelle_2026.nombre || result.annee_personnelle_2026}
                        </span>
                        <p className="text-xs tracking-widest uppercase" style={{ color: '#D4AF37', letterSpacing: '0.12em' }}>Année Personnelle 2026</p>
                      </div>
                      <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.85' }}>
                        {result.annee_personnelle_2026.theme || result.annee_personnelle_2026.description}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* ── Onglet APPROFONDI ── */}
              {activeTab === 'deep' && (
                <div className="space-y-5">
                  {loadingDeep && (
                    <div className="flex items-center justify-center py-16 gap-3">
                      <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#D4AF37' }} />
                      <span className="text-sm" style={{ color: 'var(--pa-muted)' }}>Consultation des archives numériques...</span>
                    </div>
                  )}
                  {deepResult && !loadingDeep && (
                    <>
                      {deepResult.chemin_de_vie?.nombre && (
                        <NombreCard label="✦ Chemin de Vie (API)" nombre={deepResult.chemin_de_vie.nombre}
                          localDesc={getLocalDesc('chemin', deepResult.chemin_de_vie.nombre)}
                          descApi={deepResult.chemin_de_vie.description_api} color="#A78BFA" />
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {deepResult.nombre_ame?.nombre && (
                          <NombreCard label="Nombre de l'Âme (API)" nombre={deepResult.nombre_ame.nombre}
                            localDesc={getLocalDesc('ame', deepResult.nombre_ame.nombre)}
                            descApi={deepResult.nombre_ame.description_api} color="#C97878" />
                        )}
                        {deepResult.nombre_expression?.nombre && (
                          <NombreCard label="Nombre d'Expression (API)" nombre={deepResult.nombre_expression.nombre}
                            localDesc={getLocalDesc('expression', deepResult.nombre_expression.nombre)}
                            descApi={deepResult.nombre_expression.description_api} color="#7CB88A" />
                        )}
                      </div>
                      {deepResult.nombres_defis && (
                        <div className="rounded-2xl p-5" style={{ background: 'var(--pa-surface)', border: '1px solid rgba(107,181,232,0.2)' }}>
                          <p className="text-xs tracking-widest uppercase mb-3" style={{ color: '#6BB5E8', letterSpacing: '0.12em' }}>Nombres Défis — Vos obstacles karmiques</p>
                          <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.85' }}>
                            Vos nombres défis indiquent les domaines où vous rencontrerez les plus grandes résistances — et donc les plus grandes opportunités de croissance.
                          </p>
                          <pre className="text-xs mt-3 p-3 rounded-lg overflow-auto" style={{ background: 'var(--pa-bg)', color: 'var(--pa-muted)' }}>
                            {JSON.stringify(deepResult.nombres_defis, null, 2)}
                          </pre>
                        </div>
                      )}
                      {deepResult.annee_personnelle_2026 && (
                        <div className="rounded-2xl p-5" style={{ background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.18)' }}>
                          <div className="flex items-center gap-3 mb-3">
                            <span className="text-2xl font-light" style={{ color: '#D4AF37', fontFamily: 'Cormorant Garamond, serif' }}>{deepResult.annee_personnelle_2026.nombre}</span>
                            <p className="text-xs tracking-widest uppercase" style={{ color: '#D4AF37', letterSpacing: '0.12em' }}>Année Personnelle 2026</p>
                          </div>
                          <p className="text-sm" style={{ color: 'var(--pa-body)', lineHeight: '1.85' }}>{deepResult.annee_personnelle_2026.theme}</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 mt-8 pt-6" style={{ borderTop: '1px solid var(--pa-divider)' }}>
                <button onClick={() => { setResult(null); setDeepResult(null); setShowForm(true); setUnlocked(false); setActiveTab('base'); }}
                  className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest hover:bg-[rgba(212,175,55,0.08)] transition-all"
                  style={{ border: '1px solid rgba(212,175,55,0.3)', color: '#D4AF37', letterSpacing: '0.12em' }}>
                  Nouvelle analyse
                </button>
                <button onClick={() => navigate('/karma-destin')}
                  className="flex-1 py-3 rounded-xl text-xs uppercase tracking-widest transition-all"
                  style={{ border: '1px solid #D4AF37', color: '#111625', background: '#D4AF37', fontWeight: 600, letterSpacing: '0.12em' }}>
                  Karma &amp; Destin →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Numerologie;
