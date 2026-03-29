import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, ArrowRight, Coins, LogIn } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import SEO from '@/components/SEO';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;


// ── Traduction des arcanes majeurs (API → Français) ──────────────────────────
const ARCANES_FR = {
  "The Fool": "Le Mat",
  "The Magician": "Le Bateleur",
  "The High Priestess": "La Papesse",
  "The Empress": "L'Impératrice",
  "The Emperor": "L'Empéreur",
  "The Hierophant": "Le Pape",
  "The Lovers": "L'Amoureux",
  "The Chariot": "Le Chariot",
  "Strength": "La Force",
  "The Hermit": "L'Hermite",
  "Wheel of Fortune": "La Roue de Fortune",
  "Justice": "La Justice",
  "The Hanged Man": "Le Pendu",
  "Death": "L'Arcane sans Nom",
  "Temperance": "La Tempérance",
  "The Devil": "Le Diable",
  "The Tower": "La Maison-Dieu",
  "The Star": "L'Étoile",
  "The Moon": "La Lune",
  "The Sun": "Le Soleil",
  "Judgement": "Le Jugement",
  "The World": "Le Monde",
};

const ARCANES_DESC_FR = {
  "The Fool":        "Le Mat symbolise le commencement, la liberté et le saut vers l'inconnu. Il vous invite à faire confiance à votre instinct et à avancer sans peur.",
  "The Magician":    "Le Bateleur incarne la maîtrise, la volonté et la manifestation. L'univers place entre vos mains tous les outils nécessaires pour agir. Passez à l'action.",
  "The High Priestess": "La Papesse représente la sagesse intérieure et l'intuition profonde. Écoutez votre voix intérieure — la réponse est déjà en vous.",
  "The Empress":     "L'Impératrice symbolise l'abondance, la fertilité et la création. Ce qui vous tient à cœur est en train de s'épanouir naturellement.",
  "The Emperor":     "L'Empéreur représente la structure, l'autorité et la stabilité. Affirmez votre pouvoir avec sagesse et construisez sur des bases solides.",
  "The Hierophant":  "Le Pape invite à chercher guidance et sagesse dans les traditions et les valeurs. Faites confiance aux chemins éprouvés.",
  "The Lovers":      "L'Amoureux symbolise le choix, l'union et l'alignement des valeurs. Suivez votre cœur — les décisions prises avec amour portent leurs fruits.",
  "The Chariot":     "Le Chariot représente la victoire, la détermination et la maîtrise de soi. Avancez avec confiance — vous avez la force de surmonter les obstacles.",
  "Strength":        "La Force incarne le courage doux, la patience et la maîtrise intérieure. Votre force réelle vient de la compassion, non de la contrainte.",
  "The Hermit":      "L'Hermite invite à la solitude créatrice et à l'introspection. Retirez-vous du bruit pour trouver votre propre lumière intérieure.",
  "Wheel of Fortune":"La Roue de Fortune symbolise les cycles, le destin et le renouveau. Un tournant favorable se présente — soyez prêt(e) à saisir l'opportunité.",
  "Justice":         "La Justice représente l'équilibre, la vérité et la cause à effet. Agissez avec intégrité — ce que vous semez, vous le récolterez.",
  "The Hanged Man":  "Le Pendu invite à voir les choses différemment et à lâcher prise. Parfois, l'immobilité est le chemin le plus sage.",
  "Death":           "L'Arcane sans Nom symbolise la transformation profonde et le renouveau. Une fin prépare un nouveau commencement plus aligné.",
  "Temperance":      "La Tempérance représente l'harmonie, la patience et la juste mesure. Trouvez l'équilibre entre vos désirs et la réalité.",
  "The Devil":       "Le Diable met en lumière les liens qui vous enchaînent. Reconnaître ce qui vous retient est le premier pas vers la libération.",
  "The Tower":       "La Maison-Dieu annonce un bouleversement libérateur. Ce qui s'effondre était fragile — laissez place à une structure plus vraie.",
  "The Star":        "L'Étoile rayonne d'espoir, de foi et d'inspiration. Vous êtes guidé(e) — continuez d'avancer avec confiance vers votre étoile.",
  "The Moon":        "La Lune invite à naviguer dans l'incertitude avec intuition. Les apparences sont trompeuses — fiez-vous à votre ressenti profond.",
  "The Sun":         "Le Soleil symbolise la joie, la réussite et la clarté. La lumière brille sur votre chemin — célébrez et rayonnez.",
  "Judgement":       "Le Jugement annonce une renaissance et un éveil de conscience. Un appel intérieur résonne — il est temps de répondre à votre vocation.",
  "The World":       "Le Monde symbolise l'accomplissement, la totalité et le succès. Un cycle important touche à sa fin dans la plénitude.",
};

const translateCarte = (nom) => ARCANES_FR[nom] || nom;
const getDescFr = (nom, descApi) => ARCANES_DESC_FR[nom] || descApi;

const TarotOuiNon = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, creditBalance, refreshBalance } = useAuth();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [freeUsed, setFreeUsed] = useState(null); // null=loading, true/false
  const [creditError, setCreditError] = useState('');

  // Check free tarot status on mount
  useEffect(() => {
    if (!isAuthenticated || !token) { setFreeUsed(false); return; }
    axios.get(`${API_URL}/api/credits/check-free-tarot`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => setFreeUsed(r.data.free_used)).catch(() => setFreeUsed(false));
  }, [isAuthenticated, token]);

  const currentCost = freeUsed ? 2 : 0;

  const handleTirage = async () => {
    if (!question.trim()) return;

    // Must be authenticated
    if (!isAuthenticated) return;

    // Deduct credits first (server-side)
    setCreditError('');
    setLoading(true);
    try {
      const creditRes = await axios.post(`${API_URL}/api/credits/use`,
        { service_id: 'tarot_oui_non' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Update free status
      if (creditRes.data.free_draw) {
        setFreeUsed(true);
      }
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (detail.includes('insuffisants')) {
        setCreditError('insufficient');
      } else {
        setCreditError(detail || 'Erreur lors de la déduction des crédits');
      }
      setLoading(false);
      return;
    }

    // Now do the actual tarot draw
    setResult(null);
    setIsRevealed(false);
    try {
      const res = await fetch(`${API_URL}/api/tarot/oui-non`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      });
      const data = await res.json();
      setResult(data);
      await refreshBalance();
      setTimeout(() => setIsRevealed(true), 1500);
    } catch (e) {
      console.error('Tarot error:', e);
    }
    setLoading(false);
  };

  const getOrientationStyle = (orientation) => {
    if (orientation === 'oui') return { color: '#7CB88A', label: 'OUI' };
    if (orientation === 'non') return { color: '#C97878', label: 'NON' };
    return { color: 'var(--pa-accent)', label: 'NEUTRE' };
  };

  // Not authenticated gate
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative">
        <SEO path="/tarot-oui-non" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
            </button>
            <div className="mb-12 flex items-start gap-6">
              <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/fupfyxdu_img2.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-lg opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
              <div>
                <p className="section-label">Tirage sacr&eacute;</p>
                <h1 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
                  Tarot Oui / Non
                </h1>
                <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
                  Posez votre question et laissez les Arcanes Majeurs vous r&eacute;pondre
                </p>
              </div>
            </div>
            <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-login">
              <LogIn className="w-8 h-8 mb-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Connexion requise
              </h2>
              <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
                Connectez-vous pour acc&eacute;der au Tarot Oui / Non.
              </p>
              <p className="text-sm mb-6" style={{ color: '#C5A059' }}>
                1er tirage gratuit &middot; puis 2 cr&eacute;dits &middot; 20 cr&eacute;dits offerts &agrave; l'inscription
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button onClick={() => navigate('/connexion')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300" style={{ border: '1px solid rgba(197,160,89,0.5)', color: '#C5A059', letterSpacing: '0.1em' }} data-testid="gate-login-btn">
                  Se connecter
                </button>
                <button onClick={() => navigate('/inscription')} className="text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-300" style={{ border: '1px solid rgba(197,160,89,0.3)', color: '#C5A059', background: 'rgba(197,160,89,0.08)', letterSpacing: '0.1em' }} data-testid="gate-register-btn">
                  Cr&eacute;er un compte
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Insufficient credits gate
  if (creditError === 'insufficient') {
    return (
      <div className="min-h-screen relative">
        <SEO path="/tarot-oui-non" />
        <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
          <div className="max-w-xl mx-auto">
            <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
              <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
            </button>
            <div className="flex flex-col items-center justify-center py-12 text-center" data-testid="credit-gate-insufficient">
              <Coins className="w-8 h-8 mb-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)', fontWeight: 400 }}>
                Cr&eacute;dits insuffisants
              </h2>
              <p className="text-sm mb-2" style={{ color: 'var(--pa-muted)' }}>
                Ce tirage co&ucirc;te <span style={{ color: '#C5A059', fontWeight: 600 }}>2 cr&eacute;dits</span>.
              </p>
              <p className="text-sm mb-6" style={{ color: 'var(--pa-muted)' }}>
                Votre solde : <span style={{ color: '#C5A059' }}>{creditBalance} cr&eacute;dits</span>
              </p>
              <button onClick={() => navigate('/acheter-credits')} className="flex items-center gap-2 text-xs uppercase tracking-widest px-6 py-2.5 rounded-full transition-all duration-500" style={{ border: '1px solid #C5A059', color: '#0C0918', background: '#C5A059', letterSpacing: '0.1em', fontWeight: 600 }} data-testid="gate-buy-credits-btn">
                Acheter des cr&eacute;dits <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <SEO path="/tarot-oui-non" />
      <div className="relative z-10 px-6 md:px-8 py-20 md:py-28">
      <div className="max-w-xl mx-auto">

        {/* Back */}
        <button onClick={() => navigate('/')} className="link-editorial text-xs mb-12" data-testid="back-btn">
          <ArrowLeft className="w-3.5 h-3.5" strokeWidth={1.5} /> Accueil
        </button>

        {/* Header */}
        <div className="mb-12 flex items-start gap-6">
          <img src="https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/fupfyxdu_img2.png" alt="" className="w-20 md:w-28 flex-shrink-0 rounded-lg opacity-80" style={{ filter: 'drop-shadow(0 0 20px rgba(197,160,89,0.15))' }} />
          <div>
            <p className="section-label">Tirage sacr&eacute;</p>
            <h1 className="text-3xl md:text-4xl mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, color: 'var(--pa-heading)' }}>
              Tarot Oui / Non
            </h1>
            <p className="text-sm" style={{ color: 'var(--pa-muted)' }}>
              Posez votre question et laissez les Arcanes Majeurs vous r&eacute;pondre
            </p>
          </div>
        </div>

        {/* Credit cost info */}
        <div className="mb-8 flex items-center gap-2" data-testid="tirage-counter">
          <Coins className="w-4 h-4" style={{ color: '#C5A059' }} strokeWidth={1.5} />
          <span className="text-xs tracking-widest" style={{ color: 'var(--pa-accent)', letterSpacing: '0.1em' }}>
            {freeUsed === false
              ? '1er tirage gratuit'
              : `2 cr\u00e9dits par tirage \u00b7 Solde : ${creditBalance} cr\u00e9dits`
            }
          </span>
        </div>

        {/* Question */}
        <div className="mb-8" data-testid="question-form">
          <label className="block text-xs tracking-widest uppercase mb-3" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
            Votre question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Posez votre question ici..."
            className="input-boxed resize-none h-24 w-full"
            data-testid="question-input"
          />
          {creditError && creditError !== 'insufficient' && (
            <p className="text-xs mt-2" style={{ color: '#fca5a5' }}>{creditError}</p>
          )}
          <button
            onClick={handleTirage}
            disabled={loading || !question.trim()}
            className="btn-editorial mt-6 disabled:opacity-30"
            data-testid="tirage-btn"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Consultation des Arcanes...</>
            ) : (
              <>{freeUsed === false ? 'Tirer une carte (gratuit)' : 'Tirer une carte (2 cr\u00e9dits)'}</>
            )}
          </button>
        </div>

        {/* Result */}
        {result && isRevealed && (
          <div className="mt-12 pt-12 animate-fade-in" style={{ borderTop: '1px solid var(--pa-divider)' }}>

            {/* Card */}
            <div className="text-center mb-12" data-testid="carte-result">
              <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                Arcane tir&eacute;
              </p>

              <div className="w-28 h-40 mx-auto mb-6 rounded-lg overflow-hidden"
                   style={{ border: '1px solid var(--pa-divider)' }}>
                {result.carte?.image ? (
                  <img src={`${API_URL}${result.carte.image}`} alt={result.carte.nom} className="w-full h-full object-cover" data-testid="carte-image" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center" style={{ background: 'var(--pa-surface)' }}>
                    <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-accent)' }}>
                      {result.carte?.numero === 0 ? '0' : result.carte?.numero}
                    </span>
                  </div>
                )}
              </div>

              <h2 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'var(--pa-heading)' }}>
                {translateCarte(result.carte?.nom || "")}
              </h2>
              <p className="text-xs mb-6" style={{ color: 'var(--pa-muted)' }}>{translateCarte(result.carte?.energie || "")}</p>

              {(() => {
                const style = getOrientationStyle(result.orientation);
                return (
                  <span
                    className="inline-block px-6 py-2 text-sm tracking-widest uppercase"
                    style={{ color: style.color, border: `1px solid ${style.color}30`, letterSpacing: '0.15em' }}
                    data-testid="orientation-badge"
                  >
                    {style.label}
                  </span>
                );
              })()}
            </div>

            {/* Message */}
            <div className="mb-12" data-testid="message-result">
              <p className="text-xs tracking-widest uppercase mb-4" style={{ color: 'var(--pa-accent)', letterSpacing: '0.12em' }}>
                Message des Arcanes
              </p>
              <p className="text-base leading-relaxed" style={{ color: 'var(--pa-body)', lineHeight: '2' }}>
                {getDescFr(result.carte?.nom, result.reponse)}
              </p>
            </div>

            {/* Suggestions */}
            <div className="pt-10" style={{ borderTop: '1px solid var(--pa-divider)' }}>
              <p className="text-xs tracking-widest uppercase mb-6" style={{ color: 'var(--pa-muted)', letterSpacing: '0.12em' }}>
                Pour aller plus loin
              </p>
              <div className="space-y-6" data-testid="upsell-tarologie">
                <button onClick={() => navigate('/tirage-tarot')} className="block w-full text-left group">
                  <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                    Lecture Tarot approfondie &mdash; 10 cr&eacute;dits
                  </p>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    Tirage Marseille ou Croix Celtique avec interpr&eacute;tation compl&egrave;te
                  </p>
                </button>
                <button onClick={() => navigate('/formulaire')} className="block w-full text-left group">
                  <p className="text-sm mb-1 transition-colors duration-300 group-hover:text-[#C5A059]" style={{ color: 'var(--pa-heading)' }}>
                    Votre Th&egrave;me Astral Complet
                  </p>
                  <p className="text-xs" style={{ color: 'var(--pa-muted)' }}>
                    Carte du ciel, aspects plan&eacute;taires et pr&eacute;visions 2026
                  </p>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  );
};

export default TarotOuiNon;
