import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Send, Loader2, Sparkles, Trash2, Coins, LogIn, ShoppingBag } from 'lucide-react';
import axios from 'axios';
import SEO from '@/components/SEO';
import { useAuth } from '@/context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL;
const COST_PER_MESSAGE = 2;
const FREE_MESSAGES_ANON = 3;
const FREE_COUNT_KEY = 'pa_chat_free_count';
const SESSION_KEY = 'pa_plume_session_id';

const ChatIA = () => {
  const { isAuthenticated, user, token, creditBalance, refreshBalance } = useAuth();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Bienvenue dans ton sanctuaire. Je suis Plume — pose-moi une question sur ton chemin, tes emotions, ton theme natal, tes liens. Les astres ecoutent.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [freeUsed, setFreeUsed] = useState(0);
  const [sessionId, setSessionId] = useState(null);
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
      setMessages(prev => [
        ...prev,
        {
          role: 'system',
          content: 'cta-credits',
        },
      ]);
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
      const res = await axios.post(
        `${API}/api/plume-chat`,
        {
          message: text,
          session_id: sessionId,
          birth_data: birthData,
        },
        { timeout: 60000 }
      );

      const json = res.data;
      if (json.session_id && json.session_id !== sessionId) {
        setSessionId(json.session_id);
        try { localStorage.setItem(SESSION_KEY, json.session_id); } catch (e) { /* ignore */ }
      }

      if (json.success && json.answer) {
        setMessages(prev => [...prev, { role: 'assistant', content: json.answer }]);
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
  const anonRemaining = Math.max(0, FREE_MESSAGES_ANON - freeUsed);
  const messagesRemaining = isAuthenticated
    ? Math.floor((creditBalance ?? 0) / COST_PER_MESSAGE)
    : anonRemaining;

  const blocked = isAuthenticated
    ? (creditBalance ?? 0) < COST_PER_MESSAGE
    : freeUsed >= FREE_MESSAGES_ANON;

  return (
    <>
      <SEO title="Chat IA Astral — Plume Astrale" description="Pose tes questions aux etoiles avec notre chat IA astrologique en francais." />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0B0B0F 0%, #110E1A 50%, #0B0B0F 100%)',
        paddingTop: 80,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', padding: '24px 16px 12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles style={{ width: 22, height: 22, color: '#D4B46A' }} />
            <h1 style={{
              fontFamily: 'Cinzel, serif',
              fontSize: 'clamp(20px, 4vw, 28px)',
              color: '#D4B46A',
              letterSpacing: '0.12em',
              margin: 0,
            }}>
              Plume — Ton Oracle
            </h1>
          </div>
          <p style={{ color: 'rgba(212,180,106,0.5)', fontSize: 13, letterSpacing: '0.06em', margin: 0 }}>
            Astrologue IA en francais &mdash; alimente par ton vrai theme natal
          </p>

          {/* Quota badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 12,
            padding: '6px 14px',
            borderRadius: 999,
            background: 'rgba(212,180,106,0.08)',
            border: '1px solid rgba(212,180,106,0.2)',
            fontSize: 12,
            color: '#D4B46A',
            letterSpacing: '0.04em',
          }} data-testid="chat-quota-badge">
            <Coins style={{ width: 13, height: 13 }} />
            {isAuthenticated ? (
              <span>{creditBalance ?? 0} credits — {messagesRemaining} message{messagesRemaining > 1 ? 's' : ''} restant{messagesRemaining > 1 ? 's' : ''} ({COST_PER_MESSAGE} cr/msg)</span>
            ) : (
              <span>{anonRemaining} / {FREE_MESSAGES_ANON} message{anonRemaining > 1 ? 's' : ''} gratuit{anonRemaining > 1 ? 's' : ''} restant{anonRemaining > 1 ? 's' : ''}</span>
            )}
          </div>
        </div>

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
                    background: 'linear-gradient(135deg, rgba(212,180,106,0.12), rgba(212,180,106,0.04))',
                    border: '1px solid rgba(212,180,106,0.3)',
                    textAlign: 'center',
                  }} data-testid="cta-signup">
                    <p style={{ color: '#D4B46A', fontSize: 14, margin: '0 0 12px', lineHeight: 1.6 }}>
                      Tu as utilise tes {FREE_MESSAGES_ANON} messages gratuits.<br />
                      <span style={{ color: 'rgba(230,225,218,0.85)' }}>Cree ton compte pour continuer la conversation avec les astres.</span>
                    </p>
                    <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
                      <Link to="/inscription" style={{
                        background: '#D4B46A',
                        color: '#0C0918',
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
                        color: '#D4B46A',
                        padding: '10px 20px',
                        borderRadius: 999,
                        fontSize: 13,
                        textDecoration: 'none',
                        border: '1px solid rgba(212,180,106,0.4)',
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
                    background: 'linear-gradient(135deg, rgba(212,180,106,0.12), rgba(212,180,106,0.04))',
                    border: '1px solid rgba(212,180,106,0.3)',
                    textAlign: 'center',
                  }} data-testid="cta-credits">
                    <p style={{ color: '#D4B46A', fontSize: 14, margin: '0 0 12px', lineHeight: 1.6 }}>
                      Solde insuffisant — il te faut {COST_PER_MESSAGE} credits par message.<br />
                      <span style={{ color: 'rgba(230,225,218,0.85)' }}>Recharge ton solde pour continuer.</span>
                    </p>
                    <Link to="/acheter-credits" style={{
                      background: '#D4B46A',
                      color: '#0C0918',
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
                      ? 'linear-gradient(135deg, rgba(212,180,106,0.18), rgba(212,180,106,0.08))'
                      : 'rgba(255,255,255,0.04)',
                    border: msg.role === 'user'
                      ? '1px solid rgba(212,180,106,0.25)'
                      : '1px solid rgba(255,255,255,0.06)',
                    color: msg.role === 'user' ? '#F4D98C' : 'rgba(230,225,218,0.85)',
                    fontSize: 14,
                    lineHeight: 1.7,
                    letterSpacing: '0.02em',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}>
                    {msg.role === 'assistant' && (
                      <span style={{ color: '#D4B46A', fontSize: 11, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
                        Plume Astrale
                      </span>
                    )}
                    {msg.content}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '14px 18px',
                  borderRadius: '18px 18px 18px 4px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  color: 'rgba(212,180,106,0.6)',
                  fontSize: 13,
                }}>
                  <Loader2 style={{ width: 16, height: 16, animation: 'spin 1s linear infinite' }} />
                  Les astres reflechissent...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div style={{
            display: 'flex',
            gap: 8,
            alignItems: 'flex-end',
            padding: '12px 0',
            borderTop: '1px solid rgba(212,180,106,0.08)',
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
                color: 'rgba(212,180,106,0.4)',
                flexShrink: 0,
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#D4B46A'; e.currentTarget.style.borderColor = 'rgba(212,180,106,0.25)'; }}
              onMouseLeave={e => { e.currentTarget.style.color = 'rgba(212,180,106,0.4)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'; }}
              data-testid="chat-clear-btn"
            >
              <Trash2 style={{ width: 18, height: 18 }} />
            </button>

            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={blocked ? (isAuthenticated ? "Solde insuffisant — recharge tes credits" : "Inscris-toi pour continuer") : "Pose ta question aux etoiles..."}
              rows={1}
              disabled={blocked}
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(212,180,106,0.15)',
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
                opacity: blocked ? 0.5 : 1,
              }}
              onFocus={e => { e.currentTarget.style.borderColor = 'rgba(212,180,106,0.4)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(212,180,106,0.15)'; }}
              data-testid="chat-input"
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim() || blocked}
              style={{
                background: input.trim() && !loading && !blocked
                  ? 'linear-gradient(135deg, rgba(212,180,106,0.25), rgba(212,180,106,0.12))'
                  : 'rgba(255,255,255,0.04)',
                border: '1px solid',
                borderColor: input.trim() && !loading && !blocked ? 'rgba(212,180,106,0.4)' : 'rgba(255,255,255,0.08)',
                borderRadius: 12,
                padding: 10,
                cursor: input.trim() && !loading && !blocked ? 'pointer' : 'not-allowed',
                color: input.trim() && !loading && !blocked ? '#D4B46A' : 'rgba(212,180,106,0.25)',
                flexShrink: 0,
                transition: 'all 0.2s',
              }}
              data-testid="chat-send-btn"
            >
              <Send style={{ width: 18, height: 18 }} />
            </button>
          </div>

          {/* Cost reminder */}
          <p style={{ textAlign: 'center', color: 'rgba(212,180,106,0.35)', fontSize: 11, margin: '8px 0 0', letterSpacing: '0.05em' }}>
            {isAuthenticated
              ? `Chaque message consomme ${COST_PER_MESSAGE} credits`
              : `${FREE_MESSAGES_ANON} messages gratuits, puis inscription requise`}
          </p>
        </div>

        <style>{`
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          textarea::placeholder { color: rgba(212,180,106,0.3); }
          textarea::-webkit-scrollbar { width: 4px; }
          textarea::-webkit-scrollbar-thumb { background: rgba(212,180,106,0.2); border-radius: 4px; }
        `}</style>
      </div>
    </>
  );
};

export default ChatIA;
