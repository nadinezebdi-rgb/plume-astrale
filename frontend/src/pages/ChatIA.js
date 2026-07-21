import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Send, Loader2, Sparkles, Trash2, Coins, LogIn, ShoppingBag } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import NatalEssentials from '@/components/NatalEssentials';
import CreditsPaywallModal from '@/components/CreditsPaywallModal';
import SolenaThinkingBubble from '@/components/SolenaThinkingBubble';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;
const COST_PER_MESSAGE = 10;
const FREE_MESSAGES_ANON = 3;
const FREE_COUNT_KEY = 'pa_chat_free_count';
const SESSION_KEY = 'pa_plume_session_id';

// Garde-fou : detecte une fuite d'appel d'outil JSON dans la reponse du modele
function isToolLeak(text) {
  if (!text || typeof text !== 'string' || text.length > 3000) return false;
  const s = text.trim();
  if (!s.startsWith('{') || !s.endsWith('}')) return false;
  try {
    const o = JSON.parse(s);
    return !!(o && (o.action || o.action_input));
  } catch { return false; }
}
const LEAK_FALLBACK = "Les astres sont un peu bavards ce soir. Peux-tu reformuler ta question ?";

const ChatIA = () => {
  const { isAuthenticated, user, token, creditBalance, refreshBalance } = useAuth();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Bienvenue dans ton sanctuaire. Je suis Soléna — pose-moi une question sur ton chemin, tes émotions, ton thème natal, tes liens. Les astres écoutent.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [freeUsed, setFreeUsed] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [paywallOpen, setPaywallOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Init or restore session ID (pour conversation multi-tour persistante)
  useEffect(() => {
    let sid = null;
    try {
      sid = localStorage.getItem(SESSION_KEY);
    } catch (e) { /* ignore */ }
    if (!sid) {
      sid = `plume-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      try { localStorage.setItem(SESSION_KEY, sid); } catch (e) { /* ignore */ }
    }
    setSessionId(sid);
  }, []);

  // Load anonymous free counter
  useEffect(() => {
    if (!isAuthenticated) {
      const stored = parseInt(localStorage.getItem(FREE_COUNT_KEY) || '0', 10);
      setFreeUsed(Number.isFinite(stored) ? stored : 0);
    }
  }, [isAuthenticated]);

  // Pre-fill input from mood-orb seed on home page
  useEffect(() => {
    try {
      const seed = localStorage.getItem('pa_chat_seed');
      if (seed) {
        setInput(seed);
        localStorage.removeItem('pa_chat_seed');
        setTimeout(() => inputRef.current?.focus(), 200);
      }
    } catch (e) { /* ignore */ }
  }, []);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Build birth data : priority = profil utilisateur connecté, fallback = formulaire localStorage
  const getBirthData = () => {
    let name = 'Voyageur';
    let day = 15, month = 5, year = 1992;
    let hour = 14, minute = 30;
    let lat = '48.8566', lon = '2.3522';
    let place = 'Paris', country = 'FR';
    let gender = 'female';

    // 1) Priorité : profil utilisateur connecté
    if (user) {
      if (user.email) name = user.email.split('@')[0];
      if (user.birth_date) {
        const d = new Date(user.birth_date);
        if (!isNaN(d.getTime())) {
          day = d.getDate();
          month = d.getMonth() + 1;
          year = d.getFullYear();
        }
      }
      if (user.birth_place) place = user.birth_place;
      if (user.birth_country) country = user.birth_country;
    if (user.gender) gender = user.gender;
    if (user.birth_time) {
      const [h, m] = String(user.birth_time).split(':');
      if (h !== undefined) hour = parseInt(h, 10);
      if (m !== undefined) minute = parseInt(m, 10);
    }
    if (user.latitude != null) lat = String(user.latitude);
    if (user.longitude != null) lon = String(user.longitude);
    }

    // 2) Fallback : formulaire stocké en localStorage (pour heure + coordonnées)
    try {
      const raw = localStorage.getItem('pa_formData');
      if (raw) {
        const data = JSON.parse(raw);
        if (data.prenom) name = data.prenom;
        if (!user?.birth_date && data.dateNaissance) {
          const d = new Date(data.dateNaissance);
          if (!isNaN(d.getTime())) {
            day = d.getDate();
            month = d.getMonth() + 1;
            year = d.getFullYear();
          }
        }
        if (data.heureNaissance) {
          const [h, m] = data.heureNaissance.split(':');
          hour = parseInt(h, 10) || hour;
          minute = parseInt(m, 10) || minute;
        }
        if (data.latitude) lat = String(data.latitude);
        if (data.longitude) lon = String(data.longitude);
        if (data.lieuNaissance) place = data.lieuNaissance;
      }
    } catch (e) { /* ignore */ }

    return {
      name, day, month, year, hour, min: minute,
      lat, lon, tzone: '1', gender, place, country,
    };
  };

  const incrementFreeUsed = () => {
    const next = freeUsed + 1;
    setFreeUsed(next);
    localStorage.setItem(FREE_COUNT_KEY, String(next));
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // --- Gating : anonymes 3 messages max ---
    if (!isAuthenticated && freeUsed >= FREE_MESSAGES_ANON) {
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: 'cta-signup',
        },
      ]);
      return;
    }

    // --- Gating : utilisateurs connectés avec solde insuffisant ---
    if (isAuthenticated && (creditBalance ?? 0) < COST_PER_MESSAGE) {
      setPaywallOpen(true);
      return;
    }

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);

    try {
      // --- Si connecté : déduire 2 crédits AVANT l'appel API ---
      if (isAuthenticated) {
        try {
          await axios.post(
            `${API}/api/credits/use`,
            { service_id: 'chat_astral', amount: COST_PER_MESSAGE },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          await refreshBalance();
        } catch (e) {
          setMessages(prev => [...prev, { role: 'assistant', content: "Impossible de deduire les credits. Reessaie." }]);
          setLoading(false);
          return;
        }
      }

      const birthData = getBirthData();
      // V3 Chat astrologique (natif, accès direct au thème natal) si user connecté avec données natales
      let usedV3 = false;
      let v3Answer = null;
      if (isAuthenticated && user?.birth_date) {
        try {
          const history = messages
            .filter(m => m.role === 'user' || m.role === 'assistant')
            .slice(-10)
            .map(m => ({ role: m.role, content: m.content }));
          const r3 = await axios.post(
            `${API}/api/astrology/v3/chat`,
            { message: text, session_id: sessionId, history },
            { headers: { Authorization: `Bearer ${token}` }, timeout: 95000 }
          );
          if (r3.data?.success && r3.data?.reply) {
            usedV3 = true;
            v3Answer = r3.data.reply;
            if (r3.data.session_id && r3.data.session_id !== sessionId) {
              setSessionId(r3.data.session_id);
              try { localStorage.setItem(SESSION_KEY, r3.data.session_id); } catch (e) { /* ignore */ }
            }
          }
        } catch (e) {
          // Si 402 (solde insuffisant), on redirige
          if (e.response?.status === 402) {
            setLoading(false);
            setPaywallOpen(true);
            return;
          }
          // fallback silencieux vers /api/plume-chat (LLM generique) pour les autres erreurs
        }
      }

      let json;
      if (usedV3) {
        json = { success: true, answer: v3Answer };
      } else {
        const res = await axios.post(
          `${API}/api/plume-chat`,
          {
            message: text,
            session_id: sessionId,
            birth_data: birthData,
          },
          { timeout: 95000 }
        );
        json = res.data;
        if (json.session_id && json.session_id !== sessionId) {
          setSessionId(json.session_id);
          try { localStorage.setItem(SESSION_KEY, json.session_id); } catch (e) { /* ignore */ }
        }
      }

      if (json.success && json.answer) {
        const safeAnswer = isToolLeak(json.answer) ? LEAK_FALLBACK : json.answer;
        setMessages(prev => [...prev, { role: 'assistant', content: safeAnswer }]);
        if (!isAuthenticated) incrementFreeUsed();
      } else {
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: json.message || "Les astres sont momentanement voiles. Reessaie dans un instant." },
        ]);
      }
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: "Une perturbation cosmique empeche la connexion. Verifie ta connexion et reessaie." },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: "Conversation reinitialisee. Pose-moi une nouvelle question, les etoiles sont pretes.",
      },
    ]);
    // Nouvelle session pour repartir de zero
    const newSid = `plume-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setSessionId(newSid);
    try { localStorage.setItem(SESSION_KEY, newSid); } catch (e) { /* ignore */ }
  };

  // Quotas restants
  const messagesRemaining = isAuthenticated
    ? Math.floor((creditBalance ?? 0) / COST_PER_MESSAGE)
    : 0;

  const blocked = isAuthenticated && (creditBalance ?? 0) < COST_PER_MESSAGE;

  // ═══ GATE : utilisateur non connecte → on bloque l'acces avec une offre d'inscription ═══
  if (!isAuthenticated) {
    return (
      <>
        <SEO title="Discussion avec Soléna — Plume Astrale" description="Inscris-toi et reçois 20 crédits offerts pour démarrer ta conversation personnalisée avec Soléna." />
        <div style={{
          minHeight: '100vh',
          background: 'linear-gradient(180deg, #131840 0%, #1B2150 50%, #131840 100%)',
          paddingTop: 80,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '80px 16px 32px',
        }} data-testid="consultation-gate">
          <div style={{
            maxWidth: 560, width: '100%', padding: '36px 28px',
            borderRadius: 20,
            background: 'linear-gradient(180deg, rgba(6,8,26,0.85) 0%, rgba(11,14,40,0.75) 100%)',
            border: '1px solid rgba(212,175,55,0.30)',
            boxShadow: '0 8px 40px rgba(0,0,0,0.5)',
            backdropFilter: 'blur(20px)',
            textAlign: 'center',
          }}>
            {/* Badge offre */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '5px 14px', marginBottom: 18,
              borderRadius: 999,
              background: 'rgba(212,175,55,0.15)',
              border: '1px solid rgba(212,175,55,0.4)',
              fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase',
              color: '#E8C766', fontFamily: 'Cinzel, serif',
            }}>
              <Sparkles style={{ width: 11, height: 11 }} />
              Offre de lancement
            </div>

            <h1 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 'clamp(28px, 5vw, 38px)', color: '#F4E4BC',
              lineHeight: 1.2, marginBottom: 14, fontWeight: 400,
            }}>
              Inscris-toi et reçois<br />
              <span style={{ color: '#D4AF37' }}>20 crédits gratuits</span>
            </h1>

            <p style={{
              color: 'rgba(255,255,255,0.7)', fontSize: 15, lineHeight: 1.6,
              marginBottom: 24, maxWidth: 440, margin: '0 auto 24px',
            }}>
              Ta consultation est <strong style={{ color: '#E8C766' }}>nourrie par ton thème natal réel</strong> —
              calcul précis de ton Soleil, ta Lune, ton Ascendant et tes planètes.
              Pour démarrer, j&apos;ai besoin de ta date, heure et lieu de naissance.
            </p>

            {/* Liste des avantages */}
            <div style={{
              textAlign: 'left', maxWidth: 380, margin: '0 auto 28px',
              display: 'flex', flexDirection: 'column', gap: 10,
            }}>
              {[
                '10 consultations offertes à l\'inscription',
                'Calcul précis de ton thème natal',
                'Réponses personnalisées en français',
                'Historique de tes conversations',
              ].map((t, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  fontSize: 13, color: 'rgba(255,255,255,0.8)',
                }}>
                  <span style={{ color: '#D4AF37', fontSize: 14 }}>✦</span>
                  {t}
                </div>
              ))}
            </div>

            {/* CTAs */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button onClick={() => navigate('/inscription')}
                data-testid="gate-register-btn"
                style={{
                  padding: '14px 28px', borderRadius: 999,
                  background: '#D4AF37', border: 'none', color: '#0F1230',
                  fontFamily: 'Cinzel, serif', fontSize: 12, fontWeight: 600,
                  letterSpacing: '0.18em', textTransform: 'uppercase', cursor: 'pointer',
                  boxShadow: '0 4px 20px rgba(212,175,55,0.3)',
                }}>
                Recevoir mes 20 crédits
              </button>
              <button onClick={() => navigate('/connexion')}
                data-testid="gate-login-btn"
                style={{
                  padding: '10px 24px', borderRadius: 999,
                  background: 'transparent', border: '1px solid rgba(212,175,55,0.3)',
                  color: 'rgba(212,175,55,0.85)',
                  fontFamily: 'Cinzel, serif', fontSize: 11,
                  letterSpacing: '0.15em', textTransform: 'uppercase', cursor: 'pointer',
                }}>
                J&apos;ai déjà un compte
              </button>
            </div>

            {/* Trust badge */}
            <div style={{
              marginTop: 28, paddingTop: 20,
              borderTop: '1px solid rgba(212,175,55,0.1)',
              fontSize: 11, color: 'rgba(255,255,255,0.4)', lineHeight: 1.5,
            }}>
              Calculs astrologiques propulsés par <strong style={{ color: 'rgba(212,175,55,0.85)' }}>AstrologyAPI</strong> —
              utilisée par des plateformes spécialisées dans le monde entier.
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <CreditsPaywallModal
        open={paywallOpen}
        onClose={() => setPaywallOpen(false)}
        context="chat_out"
      />
      <SEO title="Discussion avec Soléna — Plume Astrale" description="Pose toutes tes questions à Soléna en français. Une guidance personnalisée, alimentée par ta carte du ciel réelle." />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #131840 0%, #1B2150 50%, #131840 100%)',
        paddingTop: 80,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', padding: '24px 16px 12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles style={{ width: 22, height: 22, color: '#D4AF37' }} />
            <h1 style={{
              fontFamily: 'Cinzel, serif',
              fontSize: 'clamp(20px, 4vw, 28px)',
              color: '#D4AF37',
              letterSpacing: '0.12em',
              margin: 0,
            }}>
              Consultation astrale personnalisée avec Soléna
            </h1>
          </div>
          <p style={{ color: 'rgba(212,175,55,0.5)', fontSize: 13, letterSpacing: '0.06em', margin: 0 }}>
            Une lecture moderne et personnalisée de votre ciel astral
          </p>

          {/* Quota badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 12,
            padding: '6px 14px',
            borderRadius: 999,
            background: 'rgba(212,175,55,0.08)',
            border: '1px solid rgba(212,175,55,0.2)',
            fontSize: 12,
            color: '#D4AF37',
            letterSpacing: '0.04em',
          }} data-testid="chat-quota-badge">
            <Coins style={{ width: 13, height: 13 }} />
            <span>{creditBalance ?? 0} credits — {messagesRemaining} message{messagesRemaining > 1 ? 's' : ''} restant{messagesRemaining > 1 ? 's' : ''} ({COST_PER_MESSAGE} cr/msg)</span>
          </div>
        </div>

        {/* Bloc Comment Soléna t'écoute — affiché uniquement si user connecté avec données natales */}
        {isAuthenticated && token && <NatalEssentials token={token} prenom={user?.prenom} />}

        {/* Chat container */}
        <div style={{
          flex: 1,
          maxWidth: 720,
          width: '100%',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          padding: '0 16px 16px',
        }}>
          {/* Messages area */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px 0',
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
            minHeight: 'calc(100vh - 340px)',
          }}>
            {messages.map((msg, i) => {
              // Inline CTAs systeme
              if (msg.role === 'system' && msg.content === 'cta-signup') {
                return (
                  <div key={i} style={{
                    padding: '18px 20px',
                    borderRadius: 18,
                    background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(212,175,55,0.04))',
                    border: '1px solid rgba(212,175,55,0.3)',
                    textAlign: 'center',
                  }} data-testid="cta-signup">
                    <p style={{ color: '#D4AF37', fontSize: 14, margin: '0 0 12px', lineHeight: 1.6 }}>
                      Tu as utilise tes {FREE_MESSAGES_ANON} messages gratuits.<br />
                      <span style={{ color: 'rgba(230,225,218,0.85)' }}>Cree ton compte pour continuer la conversation avec les astres.</span>
                    </p>
                    <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
                      <Link to="/inscription" style={{
                        background: '#D4AF37',
                        color: '#111625',
                        padding: '10px 20px',
                        borderRadius: 999,
                        fontSize: 13,
                        fontWeight: 600,
                        textDecoration: 'none',
                        letterSpacing: '0.05em',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                      }}>
                        <Sparkles style={{ width: 14, height: 14 }} /> Creer mon compte (20 credits offerts)
                      </Link>
                      <Link to="/connexion" style={{
                        background: 'transparent',
                        color: '#D4AF37',
                        padding: '10px 20px',
                        borderRadius: 999,
                        fontSize: 13,
                        textDecoration: 'none',
                        border: '1px solid rgba(212,175,55,0.4)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                      }}>
                        <LogIn style={{ width: 14, height: 14 }} /> Se connecter
                      </Link>
                    </div>
                  </div>
                );
              }
              if (msg.role === 'system' && msg.content === 'cta-credits') {
                return (
                  <div key={i} style={{
                    padding: '18px 20px',
                    borderRadius: 18,
                    background: 'linear-gradient(135deg, rgba(212,175,55,0.12), rgba(212,175,55,0.04))',
                    border: '1px solid rgba(212,175,55,0.3)',
                    textAlign: 'center',
                  }} data-testid="cta-credits">
                    <p style={{ color: '#D4AF37', fontSize: 14, margin: '0 0 12px', lineHeight: 1.6 }}>
                      Solde insuffisant — il te faut {COST_PER_MESSAGE} credits par message.<br />
                      <span style={{ color: 'rgba(230,225,218,0.85)' }}>Recharge ton solde pour continuer.</span>
                    </p>
                    <Link to="/acheter-credits" style={{
                      background: '#D4AF37',
                      color: '#111625',
                      padding: '10px 20px',
                      borderRadius: 999,
                      fontSize: 13,
                      fontWeight: 600,
                      textDecoration: 'none',
                      letterSpacing: '0.05em',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6,
                    }}>
                      <ShoppingBag style={{ width: 14, height: 14 }} /> Acheter des credits
                    </Link>
                  </div>
                );
              }

              return (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div style={{
                    maxWidth: '85%',
                    padding: '14px 18px',
                    borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                    background: msg.role === 'user'
                      ? 'linear-gradient(135deg, rgba(212,175,55,0.18), rgba(212,175,55,0.08))'
                      : 'rgba(255,255,255,0.04)',
                    border: msg.role === 'user'
                      ? '1px solid rgba(212,175,55,0.25)'
                      : '1px solid rgba(255,255,255,0.06)',
                    color: msg.role === 'user' ? '#E8C766' : 'rgba(230,225,218,0.85)',
                    fontSize: 14,
                    lineHeight: 1.7,
                    letterSpacing: '0.02em',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}>
                    {msg.role === 'assistant' && (
                      <span style={{ color: '#D4AF37', fontSize: 11, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                        Soléna
                      </span>
                    )}
                    {msg.content}
                  </div>
                </div>
              );
            })}

            {loading && <SolenaThinkingBubble testId="chat-loading-bubble" />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div style={{
            display: 'flex',
            gap: 8,
            alignItems: 'flex-end',
            padding: '12px 0',
            borderTop: '1px solid rgba(212,175,55,0.08)',
          }}>
            <button
              onClick={clearChat}
              title="Nouvelle conversation"
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 12,
                padding: 10,
                cursor: 'pointer',
                color: 'rgba(212,175,55,0.4)',
                flexShrink: 0,
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#D4AF37'; e.currentTarget.style.borderColor = 'rgba(212,175,55,0.25)'; }}
              onMouseLeave={e => { e.currentTarget.style.color = 'rgba(212,175,55,0.4)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'; }}
              data-testid="chat-clear-btn"
            >
              <Trash2 style={{ width: 18, height: 18 }} />
            </button>

            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={e => {
                e.currentTarget.style.borderColor = 'rgba(212,175,55,0.4)';
                if (blocked) setPaywallOpen(true);
              }}
              placeholder={blocked ? (isAuthenticated ? "Solde insuffisant — recharge tes credits" : "Inscris-toi pour continuer") : "Pose ta question aux etoiles..."}
              rows={1}
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(212,175,55,0.15)',
                borderRadius: 14,
                padding: '12px 16px',
                color: '#E6E1DA',
                fontSize: 14,
                resize: 'none',
                outline: 'none',
                fontFamily: 'inherit',
                lineHeight: 1.5,
                maxHeight: 120,
                transition: 'border-color 0.2s',
                opacity: blocked ? 0.55 : 1,
                cursor: blocked ? 'pointer' : 'text',
              }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(212,175,55,0.15)'; }}
              data-testid="chat-input"
            />

            <button
              onClick={() => { if (blocked) { setPaywallOpen(true); return; } sendMessage(); }}
              disabled={loading || (!input.trim() && !blocked)}
              style={{
                background: input.trim() && !loading && !blocked
                  ? 'linear-gradient(135deg, rgba(212,175,55,0.25), rgba(212,175,55,0.12))'
                  : 'rgba(255,255,255,0.04)',
                border: '1px solid',
                borderColor: input.trim() && !loading && !blocked ? 'rgba(212,175,55,0.4)' : 'rgba(255,255,255,0.08)',
                borderRadius: 12,
                padding: 10,
                cursor: input.trim() && !loading && !blocked ? 'pointer' : 'not-allowed',
                color: input.trim() && !loading && !blocked ? '#D4AF37' : 'rgba(212,175,55,0.25)',
                flexShrink: 0,
                transition: 'all 0.2s',
              }}
              data-testid="chat-send-btn"
            >
              <Send style={{ width: 18, height: 18 }} />
            </button>
          </div>

          {/* Cost reminder */}
          <p style={{ textAlign: 'center', color: 'rgba(212,175,55,0.35)', fontSize: 11, margin: '8px 0 0', letterSpacing: '0.05em' }}>
            {isAuthenticated
              ? `Chaque message consomme ${COST_PER_MESSAGE} credits`
              : `${FREE_MESSAGES_ANON} messages gratuits, puis inscription requise`}
          </p>
        </div>

        <style>{`
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          textarea::placeholder { color: rgba(212,175,55,0.3); }
          textarea::-webkit-scrollbar { width: 4px; }
          textarea::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.2); border-radius: 4px; }
        `}</style>
      </div>
    </>
  );
};

export default ChatIA;
