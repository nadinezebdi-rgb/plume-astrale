import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles, Moon, Heart, Briefcase, Coins, Leaf,
  Sun, RefreshCw, ArrowRight, ChevronDown, Eye, Wand2,
  CircleDot, HelpCircle, LogIn, Download, ArrowUp,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { asset } from '../lib/assets';
import LibraryImage from '@/components/LibraryImage';
import TarotCardBack from '@/components/TarotCardBack';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import SEOServiceEnrich from '@/components/SEOServiceEnrich';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const DOMAINES = {
  amour:     { nom: 'Amour & Relations',       icone: Heart,      couleur: 'text-rose-600' },
  travail:   { nom: 'Carrière & Travail',      icone: Briefcase,  couleur: 'text-blue-700' },
  argent:    { nom: 'Finances & Abondance',    icone: Coins,      couleur: 'text-amber-700' },
  sante:     { nom: 'Santé & Bien-être',       icone: Leaf,       couleur: 'text-emerald-700' },
  spirituel: { nom: 'Spiritualité',             icone: Sun,        couleur: 'text-purple-700' },
  general:   { nom: 'Question Générale',        icone: CircleDot,  couleur: 'text-[#B58F3F]' },
};

const POSITIONS_MARSEILLE = ['Passé', 'Présent', 'Futur'];
const POSITIONS_CELTIQUE = [
  "La Situation Présente", "L'Obstacle ou le Défi", "Le Fondement",
  "Le Passé Récent", "La Couronne — Le Meilleur Possible",
  "Le Futur Proche", "Votre Attitude", "L'Environnement",
  "Espoirs et Craintes", "Le Résultat Final",
];

const ALL_ARCANES = [
  'Le Mat','Le Bateleur','La Papesse',"L'Impératrice","L'Empereur",
  'Le Pape','Les Amoureux','Le Chariot','La Justice',"L'Hermite",
  'La Roue de Fortune','La Force','Le Pendu',"L'Arcane sans Nom",
  'La Tempérance','Le Diable','La Maison Dieu',"L'Étoile",'La Lune',
  'Le Soleil','Le Jugement','Le Monde',
];

const TirageTarot = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();

  const [step, setStep] = useState(0);
  const [question, setQuestion] = useState('');
  const [domaine, setDomaine] = useState('general');
  const [typeTirage, setTypeTirage] = useState('marseille');
  const [isLoading, setIsLoading] = useState(false);
  const [tirageData, setTirageData] = useState(null);
  const [revealedCards, setRevealedCards] = useState([]);
  const [currentRevealIndex, setCurrentRevealIndex] = useState(-1);
  const [isRevealing, setIsRevealing] = useState(false);
  const [showDomaines, setShowDomaines] = useState(false);
  const [creditUnlocked, setCreditUnlocked] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const syntheseRef = useRef(null);

  // ─── Credit unlock ──────────────────────────────────────
  const handleCreditUnlock = async () => {
    try {
      await axios.post(
        `${API_URL}/api/credits/use`,
        { service_id: 'lecture_tarot' },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      await refreshBalance();
      setCreditUnlocked(true);
      setStep(1);
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (detail.includes('insuffisants')) {
        navigate('/acheter-credits');
      } else {
        alert(detail || 'Erreur');
      }
    }
  };

  // ─── Lancer le tirage ───────────────────────────────────
  const lancerTirage = async () => {
    if (question.length < 5) {
      alert("Veuillez formuler une question d'au moins 5 caractères");
      return;
    }
    setIsLoading(true);
    try {
      const endpoint = typeTirage === 'marseille'
        ? `${API_URL}/api/tarot/marseille`
        : `${API_URL}/api/tarot/celtique`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, domaine }),
      });
      const data = await res.json();
      if (data.success) {
        setTirageData(data.data);
        setStep(2);
        setRevealedCards([]);
        setCurrentRevealIndex(-1);
      } else {
        alert('Erreur lors du tirage. Veuillez réessayer.');
      }
    } catch (e) {
      console.error(e);
      alert('Erreur de connexion. Veuillez réessayer.');
    } finally {
      setIsLoading(false);
    }
  };

  // ─── Révélation progressive ─────────────────────────────
  const startReveal = () => {
    setIsRevealing(true);
    setCurrentRevealIndex(0);
  };

  useEffect(() => {
    if (!isRevealing || currentRevealIndex < 0 || !tirageData) return;
    const maxCards = typeTirage === 'marseille' ? 3 : 10;
    if (currentRevealIndex >= maxCards) {
      setIsRevealing(false);
      setTimeout(() => setStep(3), 900);
      return;
    }
    const t = setTimeout(() => {
      setRevealedCards(prev => [...prev, currentRevealIndex]);
      setCurrentRevealIndex(prev => prev + 1);
    }, 1100);
    return () => clearTimeout(t);
  }, [currentRevealIndex, isRevealing, tirageData, typeTirage]);

  const revealCard = (i) => {
    if (!revealedCards.includes(i)) setRevealedCards(prev => [...prev, i]);
  };

  const recommencer = () => {
    setStep(creditUnlocked ? 1 : 0);
    setQuestion('');
    setTirageData(null);
    setRevealedCards([]);
    setCurrentRevealIndex(-1);
    setIsRevealing(false);
    if (!creditUnlocked) setCreditUnlocked(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ─── Téléchargement PDF de la synthèse ──────────────────
  const telechargerPDF = async () => {
    setPdfLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tarot/pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          type: typeTirage,
          question,
          domaine,
          data: tirageData,
        }),
      });
      if (!res.ok) throw new Error('PDF generation failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const name = typeTirage === 'marseille' ? 'tarot-marseille' : 'croix-celtique';
      a.download = `${name}-plume-astrale.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Impossible de générer le PDF pour le moment. Réessayez dans un instant.");
    } finally {
      setPdfLoading(false);
    }
  };

  // ─── Rendu d'une carte (étape 2) avec vraie image ───────
  const renderCard = (carte, index, isRevealed) => {
    const positionLabel = typeTirage === 'marseille'
      ? POSITIONS_MARSEILLE[index]
      : POSITIONS_CELTIQUE[index];
    const isReversed = (carte.orientation || '').toLowerCase() === 'renverse';

    return (
      <div
        key={index}
        onClick={() => !isRevealing && revealCard(index)}
        data-testid={`tarot-card-${index}`}
        className={`relative rounded-xl p-4 border transition-all duration-500 cursor-pointer ${
          isRevealed
            ? 'bg-white/90 border-[#C9A24B]/40 shadow-xl shadow-[#C9A24B]/15'
            : 'bg-gradient-to-b from-[#f8f1e3] to-[#f0e5cc] border-[#C9A24B]/25 hover:border-[#C9A24B] hover:-translate-y-1 shadow-md'
        }`}
      >
        {/* Position */}
        <p className="text-[#C9A24B] uppercase tracking-[0.22em] text-[10px] mb-3 font-semibold text-center" style={{ fontFamily: 'Cinzel, serif' }}>
          {positionLabel}
        </p>

        {isRevealed ? (
          <div className="flex flex-col items-center">
            <div
              className="relative mx-auto mb-3 overflow-hidden rounded-lg"
              style={{
                width: 150, height: 230,
                border: `2px solid ${isReversed ? 'rgba(184,169,232,0.6)' : 'rgba(201,162,75,0.6)'}`,
                boxShadow: '0 8px 24px rgba(201,162,75,0.2)',
                transform: isReversed ? 'rotate(180deg)' : 'none',
              }}
            >
              <LibraryImage
                type="tarot"
                name={carte.nom}
                size={230}
                alt={carte.nom}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                data-testid={`tarot-card-img-${index}`}
              />
            </div>

            <h3 className="text-lg mb-2 text-center" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
              {carte.nom}
            </h3>

            <span className={`inline-flex items-center gap-1 text-[10px] px-3 py-0.5 rounded-full mb-3 ${
              isReversed
                ? 'bg-[#B8A9E8]/15 text-[#8878C8] border border-[#B8A9E8]/40'
                : 'bg-[#C9A24B]/15 text-[#8B6914] border border-[#C9A24B]/40'
            }`}>
              {isReversed ? <><Moon className="w-3 h-3" /> Renversée</> : <><Sun className="w-3 h-3" /> Droite</>}
            </span>

            {carte.mots_cles?.length > 0 && (
              <div className="flex flex-wrap justify-center gap-1 mb-3">
                {carte.mots_cles.slice(0, 3).map((m, i) => (
                  <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-[#0F1A3C]/5 text-[#0F1A3C]/75 border border-[#0F1A3C]/10">
                    {m}
                  </span>
                ))}
              </div>
            )}

            {(carte.element || carte.planete) && (
              <div className="flex justify-center gap-3 text-[10px] text-[#0F1A3C]/60 mb-3">
                {carte.element && <span>◆ {carte.element}</span>}
                {carte.planete && <span>☆ {carte.planete}</span>}
              </div>
            )}

            {carte.interpretation && (
              <p className="text-[#232323]/85 text-xs leading-relaxed text-center px-1 mb-3 font-light">
                {carte.interpretation.length > 180 ? `${carte.interpretation.slice(0, 180)}…` : carte.interpretation}
              </p>
            )}

            {carte.conseil && (
              <div className="w-full bg-gradient-to-r from-[#C9A24B]/5 via-[#C9A24B]/15 to-[#C9A24B]/5 rounded-md p-2 border border-[#C9A24B]/20 mt-auto">
                <p className="text-[#8B6914] text-[11px] italic text-center leading-snug">
                  « {carte.conseil} »
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center py-4">
            <TarotCardBack size={{ width: 130, height: 200 }} testId={`tarot-back-${index}`} />
            {!isRevealing && (
              <p className="text-[#C9A24B]/80 text-[11px] mt-3 animate-pulse" style={{ fontFamily: 'Cinzel, serif', letterSpacing: '0.1em' }}>
                Cliquez pour révéler
              </p>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <PsPageShell background="light">
      <SEO path="/services/tarot" />
      <div className="min-h-screen relative">
        <div
          className="fixed inset-0 opacity-5 pointer-events-none"
          style={{
            backgroundImage: `url('${asset('images/tarot/tarot_cards_2.png')}')`,
            backgroundSize: 'cover', backgroundPosition: 'center',
          }}
        />

        <div className="px-6 md:px-8 py-20 md:py-28 relative z-10">
          <div className="max-w-6xl mx-auto">

            {/* ═══════ ÉTAPE 0 : credit gate ═══════ */}
            {step === 0 && (
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-10">
                  <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-sm mb-4 font-light">Tirage de Tarot</p>
                  <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                    Consultez les Arcanes
                  </h1>
                  <p className="text-lg text-[#232323]/70 font-light">Lecture Tarot approfondie</p>
                </div>

                <div className="flex justify-center gap-4 mb-10" data-testid="tarot-teaser-backs">
                  <div style={{ transform: 'rotate(-6deg)' }}><TarotCardBack size={{ width: 110, height: 160 }} /></div>
                  <div style={{ transform: 'translateY(-8px)' }}><TarotCardBack size={{ width: 120, height: 175 }} /></div>
                  <div style={{ transform: 'rotate(6deg)' }}><TarotCardBack size={{ width: 110, height: 160 }} /></div>
                </div>

                {!isAuthenticated ? (
                  <div className="flex flex-col items-center justify-center py-10 text-center" data-testid="credit-gate-login">
                    <LogIn className="w-8 h-8 mb-4 text-[#C9A24B]" strokeWidth={1.5} />
                    <h2 className="text-xl mb-2" style={{ fontFamily: 'Playfair Display, serif', color: 'var(--pa-heading)' }}>
                      Connexion requise
                    </h2>
                    <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
                      Connectez-vous pour accéder au tirage de Tarot.<br />
                      <span className="text-[#C9A24B]">10 crédits · 20 crédits offerts à l'inscription</span>
                    </p>
                    <div className="flex gap-3">
                      <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full border border-[#C9A24B]/50 text-[#C9A24B]" data-testid="gate-login-btn">Se connecter</button>
                      <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full border border-[#C9A24B]/30 text-[#C9A24B] bg-[#C9A24B]/10" data-testid="gate-register-btn">Créer un compte</button>
                    </div>
                  </div>
                ) : creditBalance < 10 ? (
                  <div className="flex flex-col items-center justify-center py-10 text-center" data-testid="credit-gate-insufficient">
                    <Coins className="w-8 h-8 mb-4 text-[#C9A24B]" strokeWidth={1.5} />
                    <h2 className="text-xl mb-2" style={{ fontFamily: 'Playfair Display, serif', color: 'var(--pa-heading)' }}>Crédits insuffisants</h2>
                    <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>Le tirage coûte <span className="text-[#C9A24B] font-semibold">10 crédits</span>.</p>
                    <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>Solde : <span className="text-[#C9A24B]">{creditBalance} crédits</span></p>
                    <button onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full bg-[#C9A24B] text-[#111625] font-semibold" data-testid="gate-buy-credits-btn">
                      Acheter des crédits <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-10 text-center" data-testid="credit-gate-unlock">
                    <Coins className="w-7 h-7 mb-3 text-[#C9A24B]" strokeWidth={1.5} />
                    <p className="text-sm mb-1" style={{ color: 'var(--pa-body)' }}>Lecture Tarot approfondie</p>
                    <p className="text-xs mb-5" style={{ color: 'var(--pa-muted)' }}>
                      Coût : <span className="text-[#C9A24B]">10 crédits</span> · Solde : <span className="text-[#C9A24B]">{creditBalance} crédits</span>
                    </p>
                    <button onClick={handleCreditUnlock} className="text-xs uppercase tracking-widest px-8 py-2.5 rounded-full border border-[#C9A24B]/50 text-[#C9A24B]" data-testid="gate-unlock-btn">
                      Utiliser 10 crédits
                    </button>
                  </div>
                )}

                {/* Vitrine 22 arcanes */}
                <div className="mt-14 text-center" data-testid="tarot-deck-preview">
                  <p className="text-[#C9A24B] uppercase tracking-[0.28em] text-[11px] mb-3" style={{ fontFamily: 'Cinzel, serif' }}>
                    ✦ Les 22 arcanes peints à la main ✦
                  </p>
                  <h3 className="mb-2" style={{ fontFamily: 'Playfair Display, serif', fontSize: 'clamp(1.3rem, 2.6vw, 1.8rem)', color: '#0F1A3C' }}>
                    Un jeu unique, dessiné pour Plume Astrale
                  </h3>
                  <p className="text-[#232323]/70 text-sm max-w-xl mx-auto mb-7 font-light">
                    Chaque arcane a été composé à la main dans l'esprit du Tarot de Marseille — or profond sur nuit d'encre, aucun visuel standard IA.
                  </p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {ALL_ARCANES.map((name, idx) => (
                      <div key={name} title={name} data-testid={`deck-preview-${idx}`} style={{
                        width: 58, height: 87, borderRadius: 4, overflow: 'hidden',
                        border: '1px solid rgba(201,162,75,0.35)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.45)', background: '#0e0a24',
                      }}>
                        <LibraryImage type="tarot" name={name} size={87} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ═══════ ÉTAPE 1 : question ═══════ */}
            {step === 1 && (
              <div className="max-w-2xl mx-auto">
                <div className="text-center mb-10">
                  <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-sm mb-4 font-light">Tirage de Tarot</p>
                  <h1 className="text-3xl md:text-5xl mb-4" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                    Formulez votre question
                  </h1>
                  <p className="text-lg text-[#232323]/70 font-light">Choisissez votre tirage et confiez-nous ce qui vous habite</p>
                </div>

                <div className="grid md:grid-cols-2 gap-4 mb-8">
                  <div onClick={() => setTypeTirage('marseille')} data-testid="select-marseille"
                       className={`rounded-xl p-5 border cursor-pointer transition-all ${
                         typeTirage === 'marseille'
                           ? 'bg-[#C9A24B]/10 border-[#C9A24B] shadow-md'
                           : 'bg-white/70 border-[#C9A24B]/25 hover:border-[#C9A24B]/60'
                       }`}>
                    <div className="text-center py-2">
                      <div className="flex justify-center gap-2 mb-3">
                        {[1,2,3].map(i => (
                          <div key={i} className="w-8 h-12 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#C9A24B]/40" />
                        ))}
                      </div>
                      <h3 className="text-lg mb-1" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>Tirage Marseille</h3>
                      <p className="text-[#232323]/65 text-sm">3 cartes · Passé, Présent, Futur</p>
                      <p className="text-[#C9A24B] text-lg font-semibold mt-2">Inclus</p>
                    </div>
                  </div>

                  <div onClick={() => setTypeTirage('celtique')} data-testid="select-celtique"
                       className={`rounded-xl p-5 border cursor-pointer transition-all ${
                         typeTirage === 'celtique'
                           ? 'bg-[#C9A24B]/10 border-[#C9A24B] shadow-md'
                           : 'bg-white/70 border-[#C9A24B]/25 hover:border-[#C9A24B]/60'
                       }`}>
                    <div className="text-center py-2">
                      <div className="flex justify-center gap-1 mb-3 flex-wrap mx-auto" style={{ maxWidth: 120 }}>
                        {[1,2,3,4,5,6,7,8,9,10].map(i => (
                          <div key={i} className="w-4 h-6 rounded bg-gradient-to-b from-[#2D1F4B] to-[#1C1735] border border-[#C9A24B]/40" />
                        ))}
                      </div>
                      <h3 className="text-lg mb-1" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>Croix Celtique</h3>
                      <p className="text-[#232323]/65 text-sm">10 cartes · Analyse complète</p>
                      <p className="text-[#C9A24B] text-lg font-semibold mt-2">Inclus</p>
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <label className="block text-[#232323]/80 text-sm mb-2 font-light">Domaine de votre question</label>
                  <div className="rounded-xl p-3 border border-[#C9A24B]/25 bg-white/70 cursor-pointer" onClick={() => setShowDomaines(!showDomaines)}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {React.createElement(DOMAINES[domaine].icone, { className: `w-5 h-5 ${DOMAINES[domaine].couleur}`, strokeWidth: 1.5 })}
                        <span className="text-[#0F1A3C] font-medium">{DOMAINES[domaine].nom}</span>
                      </div>
                      <ChevronDown className={`w-5 h-5 text-[#C9A24B] transition-transform ${showDomaines ? 'rotate-180' : ''}`} />
                    </div>
                  </div>
                  {showDomaines && (
                    <div className="mt-2 rounded-xl border border-[#C9A24B]/25 bg-white/90 divide-y divide-[#C9A24B]/10">
                      {Object.entries(DOMAINES).map(([key, value]) => (
                        <div key={key}
                          className={`flex items-center gap-3 py-3 px-4 cursor-pointer hover:bg-[#C9A24B]/10 transition-colors ${domaine === key ? 'bg-[#C9A24B]/10' : ''}`}
                          onClick={() => { setDomaine(key); setShowDomaines(false); }}>
                          {React.createElement(value.icone, { className: `w-5 h-5 ${value.couleur}`, strokeWidth: 1.5 })}
                          <span className="text-[#0F1A3C]">{value.nom}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mb-8">
                  <label className="block text-[#232323]/80 text-sm mb-2 font-light">Votre question</label>
                  <div className="relative">
                    <HelpCircle className="absolute left-4 top-4 w-5 h-5 text-[#C9A24B]/50" strokeWidth={1.5} />
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Formulez votre question avec clarté et sincérité…"
                      className="w-full bg-white border border-[#0F1A3C]/25 rounded-xl py-4 pl-12 pr-4 text-[#0F1A3C] placeholder-[#0F1A3C]/40 focus:outline-none focus:border-[#C9A24B] transition-colors resize-none"
                      rows={4}
                      data-testid="input-question"
                    />
                  </div>
                  <p className="text-[#232323]/70 text-xs mt-2">
                    Exemples : « Vais-je trouver l'amour cette année ? » · « Mon projet professionnel va-t-il aboutir ? »
                  </p>
                </div>

                <button
                  onClick={lancerTirage}
                  disabled={isLoading || question.length < 5}
                  className={`w-full btn-mystical-filled rounded-xl py-4 flex items-center justify-center gap-3 text-lg ${question.length < 5 ? 'opacity-50 cursor-not-allowed' : ''}`}
                  data-testid="btn-lancer-tirage"
                >
                  {isLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-[#1C1735] border-t-transparent rounded-full animate-spin" />
                      Préparation du tirage…
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-5 h-5" strokeWidth={1.5} />
                      Consulter les Arcanes
                      <ArrowRight className="w-5 h-5" strokeWidth={1.5} />
                    </>
                  )}
                </button>
              </div>
            )}

            {/* ═══════ ÉTAPE 2 : révélation ═══════ */}
            {step === 2 && tirageData && (
              <div>
                <div className="text-center mb-10">
                  <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-sm mb-4 font-light">
                    {typeTirage === 'marseille' ? 'Tirage Marseille' : 'Croix Celtique'}
                  </p>
                  <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                    Les cartes sont tirées
                  </h1>
                  <p className="text-[#232323]/70 font-light max-w-xl mx-auto italic">« {question} »</p>
                </div>

                {!isRevealing && revealedCards.length === 0 && (
                  <div className="text-center mb-8">
                    <button onClick={startReveal} className="btn-mystical-filled rounded-xl py-4 px-8 flex items-center gap-3 mx-auto text-lg" data-testid="btn-reveal-all">
                      <Eye className="w-5 h-5" strokeWidth={1.5} />
                      Révéler les cartes une par une
                      <Sparkles className="w-5 h-5" strokeWidth={1.5} />
                    </button>
                    <p className="text-[#0F1A3C]/55 text-sm mt-3">Ou cliquez sur chaque carte pour la révéler manuellement</p>
                  </div>
                )}

                {isRevealing && (
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-3 bg-[#C9A24B]/20 px-6 py-3 rounded-full">
                      <div className="w-4 h-4 border-2 border-[#C9A24B] border-t-transparent rounded-full animate-spin" />
                      <span className="text-[#8B6914]">
                        Révélation en cours… Carte {revealedCards.length + 1} / {typeTirage === 'marseille' ? 3 : 10}
                      </span>
                    </div>
                  </div>
                )}

                <div className={`grid gap-5 ${
                  typeTirage === 'marseille' ? 'md:grid-cols-3' : 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5'
                }`}>
                  {tirageData.cartes.map((carte, index) =>
                    renderCard(carte, index, revealedCards.includes(index)),
                  )}
                </div>

                {revealedCards.length === tirageData.cartes.length && !isRevealing && (
                  <div className="text-center mt-10">
                    <button
                      onClick={() => { setStep(3); setTimeout(() => syntheseRef.current?.scrollIntoView({ behavior: 'smooth' }), 100); }}
                      className="btn-mystical-filled rounded-xl py-4 px-8 flex items-center gap-3 mx-auto text-lg"
                      data-testid="btn-voir-synthese"
                    >
                      Voir la synthèse complète <ArrowRight className="w-5 h-5" strokeWidth={1.5} />
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* ═══════ ÉTAPE 3 : synthèse ═══════ */}
            {step === 3 && tirageData && (
              <div className="max-w-4xl mx-auto" ref={syntheseRef}>
                <div className="text-center mb-10">
                  <p className="text-[#C9A24B] uppercase tracking-[0.3em] text-sm mb-4 font-light">Synthèse de votre tirage</p>
                  <h1 className="text-2xl md:text-4xl mb-4" style={{ fontFamily: 'Playfair Display, serif', color: '#0F1A3C' }}>
                    L'interprétation des Arcanes
                  </h1>
                </div>

                <div className="rounded-xl p-5 bg-[#C9A24B]/10 border border-[#C9A24B]/30 mb-8">
                  <p className="text-center">
                    <span className="text-[#232323]/65 text-sm">Votre question : </span>
                    <span className="text-[#0F1A3C] italic">« {question} »</span>
                  </p>
                </div>

                {/* Résumé visuel : 3 cartes clés */}
                <div className="grid grid-cols-3 gap-3 mb-10">
                  {tirageData.cartes.slice(0, 3).map((carte, i) => {
                    const posLabels = typeTirage === 'marseille'
                      ? POSITIONS_MARSEILLE
                      : ['Situation', 'Défi', 'Fondement'];
                    const isReversed = (carte.orientation || '').toLowerCase() === 'renverse';
                    return (
                      <div key={i} className="text-center" data-testid={`synth-key-${i}`}>
                        <p className="text-[#C9A24B] uppercase tracking-[0.2em] text-[10px] mb-2" style={{ fontFamily: 'Cinzel, serif' }}>
                          {posLabels[i]}
                        </p>
                        <div
                          className="mx-auto overflow-hidden rounded-md"
                          style={{
                            width: 90, height: 140,
                            border: `1.5px solid ${isReversed ? 'rgba(184,169,232,0.5)' : 'rgba(201,162,75,0.5)'}`,
                            transform: isReversed ? 'rotate(180deg)' : 'none',
                          }}
                        >
                          <LibraryImage
                            type="tarot" name={carte.nom} size={140}
                            alt={carte.nom}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          />
                        </div>
                        <p className="text-[#0F1A3C] text-xs mt-2 font-medium" style={{ fontFamily: 'Playfair Display, serif' }}>
                          {carte.nom}
                        </p>
                      </div>
                    );
                  })}
                </div>

                {/* Synthèse Marseille */}
                {typeTirage === 'marseille' && tirageData.synthese && (
                  <div className="space-y-6">
                    {tirageData.synthese.tendance_generale && (
                      <div className="rounded-xl p-6 bg-white/80 border border-[#C9A24B]/20 shadow-sm">
                        <h3 className="text-xl mb-3 text-[#C9A24B]" style={{ fontFamily: 'Playfair Display, serif' }}>
                          Tendance Générale : {tirageData.synthese.tendance_generale}
                        </h3>
                        {tirageData.synthese.fil_conducteur && (
                          <p className="text-[#232323]/80 leading-relaxed">{tirageData.synthese.fil_conducteur}</p>
                        )}
                      </div>
                    )}

                    {(tirageData.synthese.message_passe || tirageData.synthese.message_present || tirageData.synthese.message_futur) && (
                      <div className="grid md:grid-cols-3 gap-4">
                        {['message_passe', 'message_present', 'message_futur'].map((k, i) => (
                          tirageData.synthese[k] ? (
                            <div key={k} className="rounded-xl p-5 bg-white/80 border border-[#C9A24B]/20">
                              <h4 className="text-[#C9A24B] mb-2 font-semibold" style={{ fontFamily: 'Playfair Display, serif' }}>
                                {POSITIONS_MARSEILLE[i]}
                              </h4>
                              <p className="text-[#232323]/80 text-sm leading-relaxed">{tirageData.synthese[k]}</p>
                            </div>
                          ) : null
                        ))}
                      </div>
                    )}

                    {tirageData.conseil_final && (
                      <div className="rounded-xl p-6 bg-gradient-to-br from-[#C9A24B]/15 to-[#C9A24B]/5 border border-[#C9A24B]/40">
                        <div className="flex items-start gap-4">
                          <Sparkles className="w-8 h-8 text-[#C9A24B] flex-shrink-0 mt-1" strokeWidth={1} />
                          <div>
                            <h4 className="text-[#8B6914] text-lg mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
                              Conseil des Arcanes
                            </h4>
                            <p className="text-[#0F1A3C] italic leading-relaxed">{tirageData.conseil_final}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Synthèse Celtique */}
                {typeTirage === 'celtique' && tirageData.analyse && (
                  <div className="space-y-6">
                    {tirageData.analyse.energie_globale && (
                      <div className="rounded-xl p-6 bg-white/80 border border-[#C9A24B]/20 shadow-sm">
                        <h3 className="text-xl mb-4 text-[#C9A24B]" style={{ fontFamily: 'Playfair Display, serif' }}>Énergie Globale</h3>
                        <p className="text-[#0F1A3C] mb-4 leading-relaxed">{tirageData.analyse.energie_globale}</p>
                        <div className="flex flex-wrap gap-4 text-sm">
                          {typeof tirageData.analyse.cartes_droites === 'number' && (
                            <span className="text-emerald-700">✓ {tirageData.analyse.cartes_droites} droites</span>
                          )}
                          {typeof tirageData.analyse.cartes_renversees === 'number' && (
                            <span className="text-rose-700">↻ {tirageData.analyse.cartes_renversees} renversées</span>
                          )}
                          {tirageData.analyse.element_dominant && (
                            <span className="text-[#B58F3F]">◆ Élément dominant : {tirageData.analyse.element_dominant}</span>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="grid md:grid-cols-2 gap-4">
                      {['situation_actuelle', 'obstacle_principal', 'fondement', 'resultat_probable'].map(k => {
                        const bloc = tirageData.analyse[k];
                        if (!bloc?.carte && !bloc?.message) return null;
                        const titles = {
                          situation_actuelle: 'Situation Actuelle',
                          obstacle_principal: 'Obstacle Principal',
                          fondement: 'Fondement',
                          resultat_probable: 'Résultat Probable',
                        };
                        return (
                          <div key={k} className="rounded-xl p-5 bg-white/80 border border-[#C9A24B]/20">
                            <h4 className="text-[#C9A24B] mb-2 font-semibold" style={{ fontFamily: 'Playfair Display, serif' }}>{titles[k]}</h4>
                            {bloc.carte && <p className="text-[#0F1A3C] font-semibold mb-1">{bloc.carte}</p>}
                            {bloc.message && <p className="text-[#232323]/80 text-sm leading-relaxed">{bloc.message}</p>}
                          </div>
                        );
                      })}
                    </div>

                    {tirageData.analyse.synthese_finale && (
                      <div className="rounded-xl p-6 bg-white/80 border border-[#C9A24B]/20">
                        <h4 className="text-[#C9A24B] text-lg mb-3" style={{ fontFamily: 'Playfair Display, serif' }}>Synthèse Finale</h4>
                        <p className="text-[#232323]/85 whitespace-pre-line leading-relaxed">{tirageData.analyse.synthese_finale}</p>
                      </div>
                    )}

                    {tirageData.analyse.conseil_action && (
                      <div className="rounded-xl p-6 bg-gradient-to-br from-[#C9A24B]/15 to-[#C9A24B]/5 border border-[#C9A24B]/40">
                        <div className="flex items-start gap-4">
                          <Sparkles className="w-8 h-8 text-[#C9A24B] flex-shrink-0 mt-1" strokeWidth={1} />
                          <div>
                            <h4 className="text-[#8B6914] text-lg mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>Conseil d'Action</h4>
                            <p className="text-[#0F1A3C] whitespace-pre-line leading-relaxed">{tirageData.analyse.conseil_action}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Actions finales */}
                <div className="flex flex-col md:flex-row gap-4 justify-center mt-12">
                  <button
                    onClick={telechargerPDF}
                    disabled={pdfLoading}
                    className="btn-mystical-filled rounded-xl py-3 px-8 flex items-center justify-center gap-2"
                    data-testid="btn-download-pdf"
                  >
                    {pdfLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-[#1C1735] border-t-transparent rounded-full animate-spin" />
                        Préparation du PDF…
                      </>
                    ) : (
                      <>
                        <Download className="w-5 h-5" strokeWidth={1.5} />
                        Télécharger ma synthèse PDF
                      </>
                    )}
                  </button>
                  <button
                    onClick={recommencer}
                    className="btn-mystical rounded-xl py-3 px-8 flex items-center justify-center gap-2"
                    data-testid="btn-nouveau-tirage"
                  >
                    <RefreshCw className="w-5 h-5" strokeWidth={1.5} /> Nouveau tirage
                  </button>
                  <button
                    onClick={() => { window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    className="btn-mystical rounded-xl py-3 px-8 flex items-center justify-center gap-2"
                    data-testid="btn-scroll-top"
                  >
                    <ArrowUp className="w-5 h-5" strokeWidth={1.5} /> Revoir les cartes
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <SEOServiceEnrich slug="tarot" />
    </PsPageShell>
  );
};

export default TirageTarot;
