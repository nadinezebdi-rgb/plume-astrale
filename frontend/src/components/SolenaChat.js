import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Loader2, Sparkles, X, MessageCircle } from 'lucide-react';
import axios from 'axios';
import { SOLENA } from '../lib/solena';

const API = process.env.REACT_APP_BACKEND_URL;
const BIRTH_KEY = 'pa_birth_data';
const SESSION_KEY = 'pa_solena_session_id';

/**
 * SolenaChat — Fenêtre de chat inline avec Solena.
 * Activée par CustomEvent 'pa:open-solena-chat' ou par le bouton "Ouvrir la conversation".
 * Utilise localStorage 'pa_birth_data' pour personnaliser la réponse via /api/plume-chat.
 */
export default function SolenaChat() {
  const [open, setOpen] = useState(false);
  const [birthData, setBirthData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const scrollRef = useRef(null);

  // Init session
  useEffect(() => {
    let sid = null;
    try { sid = localStorage.getItem(SESSION_KEY); } catch (e) { /* ignore */ }
    if (!sid) {
      sid = `solena-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      try { localStorage.setItem(SESSION_KEY, sid); } catch (e) { /* ignore */ }
    }
    setSessionId(sid);
  }, []);

  // Read stored birth data (may or may not exist)
  const loadBirth = useCallback(() => {
    try {
      const raw = localStorage.getItem(BIRTH_KEY);
      if (raw) setBirthData(JSON.parse(raw));
    } catch (e) { /* ignore */ }
  }, []);

  useEffect(() => { loadBirth(); }, [loadBirth]);

  // Listen for external open events (from Hero form submission)
  // Uses a ref to always call the current openChat and avoid stale closures with StrictMode.
  const openChatRef = useRef(null);
  useEffect(() => {
    const handler = (e) => {
      if (openChatRef.current) openChatRef.current(e.detail);
    };
    window.addEventListener('pa:open-solena-chat', handler);
    return () => window.removeEventListener('pa:open-solena-chat', handler);
  }, []);

  // Auto-scroll on new message
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const openChat = async (data) => {
    setOpen(true);
    if (data) {
      setBirthData(data);
      try { localStorage.setItem(BIRTH_KEY, JSON.stringify(data)); } catch (err) { /* ignore */ }
    }
    // Si aucune message n'existe encore, on lance la conversation
    if (messages.length === 0) {
      const bd = data || birthData;
      await sendFirstGreeting(bd);
    }
  };

  // Keep the ref pointing to the latest openChat closure (avoids stale state with StrictMode)
  openChatRef.current = openChat;

  const sendFirstGreeting = async (bd) => {
    if (!bd) {
      setMessages([{
        role: 'assistant',
        content: "Bonjour, je suis Solena. Pour commencer, peux-tu me dire ta date de naissance ? Cela m'aide à lire ton ciel avec précision.",
      }]);
      return;
    }
    setLoading(true);
    try {
      const seedMsg = `Bonjour Solena. Je viens de te confier ma date de naissance : ${bd.day}/${bd.month}/${bd.year} à ${String(bd.hour).padStart(2,'0')}h${String(bd.min ?? bd.minute ?? 0).padStart(2,'0')} à ${bd.place}. Que révèle mon ciel de naissance sur mes cycles d'amour à venir ?`;
      const res = await axios.post(`${API}/api/plume-chat`, {
        message: seedMsg,
        session_id: sessionId,
        birth_data: bd,
      }, { timeout: 45000 });
      if (res.data?.success) {
        setMessages([
          { role: 'user', content: seedMsg, hidden: true }, // hidden from UI, but sent for context
          { role: 'assistant', content: res.data.answer },
        ]);
      } else {
        setMessages([{ role: 'assistant', content: res.data?.message || "Les astres sont un peu bavards. Réessaie dans un instant." }]);
      }
    } catch (e) {
      setMessages([{ role: 'assistant', content: "Une perturbation cosmique — réessaie dans quelques instants." }]);
    } finally {
      setLoading(false);
    }
  };

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/plume-chat`, {
        message: text,
        session_id: sessionId,
        birth_data: birthData,
      }, { timeout: 45000 });
      if (res.data?.success) {
        setMessages((prev) => [...prev, { role: 'assistant', content: res.data.answer }]);
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', content: res.data?.message || "Réessaie dans un instant." }]);
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'assistant', content: "Une perturbation cosmique — réessaie dans quelques instants." }]);
    } finally {
      setLoading(false);
    }
  };

  const visibleMessages = messages.filter((m) => !m.hidden);
  const hasBirth = !!birthData;

  return (
    <div id="solena-chat-anchor" data-testid="solena-chat-panel">
      {/* CTA card qui ouvre le chat */}
      {!open && (
        <button
          type="button"
          onClick={() => openChat(birthData)}
          className="w-full rounded-3xl p-6 md:p-8 text-left transition-all hover:scale-[1.01] group"
          style={{
            background: 'linear-gradient(135deg, rgba(212,180,106,0.14) 0%, rgba(20,15,40,0.6) 100%)',
            border: '1px solid rgba(212,180,106,0.45)',
            backdropFilter: 'blur(14px)',
            boxShadow: '0 20px 60px rgba(212,180,106,0.15), 0 0 40px rgba(212,180,106,0.10)',
            cursor: 'pointer',
          }}
          data-testid="open-solena-chat-btn"
        >
          <div className="flex items-start gap-4">
            <div style={{
              flexShrink: 0,
              width: 60, height: 60, borderRadius: '50%', overflow: 'hidden',
              border: '2px solid rgba(212,180,106,0.55)',
              boxShadow: '0 0 24px rgba(212,180,106,0.35)',
            }}>
              <img src={SOLENA.portrait} alt="Solena" style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 20%' }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] uppercase" style={{ color: '#D4B46A', letterSpacing: '0.25em', fontWeight: 500 }}>
                  Solena · en ligne
                </span>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ADE80', boxShadow: '0 0 8px #4ADE80' }} />
              </div>
              <div style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '1.15rem',
                color: '#F4E8D2',
                lineHeight: 1.4,
                fontStyle: 'italic',
              }}>
                « {hasBirth
                  ? 'Ton ciel est prêt. Ouvre la conversation quand tu veux, je t\'attends…'
                  : 'Confie-moi ta date de naissance pour lire ton ciel — ou pose-moi ta question directement.'} »
              </div>
              <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full text-[11px] uppercase"
                style={{
                  background: 'linear-gradient(135deg, #D4B46A, #F4D98C)',
                  color: '#0C0918', letterSpacing: '0.2em', fontWeight: 700,
                }}>
                <MessageCircle style={{ width: 12, height: 12 }} strokeWidth={2} />
                Ouvrir la conversation
              </div>
            </div>
          </div>
        </button>
      )}

      {/* Chat window */}
      {open && (
        <div
          className="rounded-3xl overflow-hidden flex flex-col"
          style={{
            background: 'linear-gradient(180deg, rgba(20,15,40,0.95), rgba(6,8,26,0.98))',
            border: '1px solid rgba(212,180,106,0.45)',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 30px 90px rgba(212,180,106,0.20), 0 0 60px rgba(212,180,106,0.10)',
            height: 560,
          }}
          data-testid="solena-chat-window"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: 'rgba(212,180,106,0.18)' }}>
            <div className="flex items-center gap-3">
              <div style={{
                width: 42, height: 42, borderRadius: '50%', overflow: 'hidden',
                border: '2px solid rgba(212,180,106,0.55)',
              }}>
                <img src={SOLENA.portrait} alt="Solena" style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 20%' }} />
              </div>
              <div>
                <div className="text-sm" style={{ color: '#F4E8D2', fontFamily: 'Cormorant Garamond, serif', fontWeight: 500, letterSpacing: '0.05em' }}>
                  Solena
                </div>
                <div className="flex items-center gap-1.5 text-[10px] uppercase" style={{ color: 'rgba(212,180,106,0.7)', letterSpacing: '0.2em' }}>
                  <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#4ADE80', boxShadow: '0 0 6px #4ADE80' }} />
                  Astrologue · en ligne
                </div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-[10px] uppercase opacity-60 hover:opacity-100"
              style={{ color: '#D4B46A', letterSpacing: '0.2em', background: 'transparent', border: 'none', cursor: 'pointer', padding: 4 }}
              data-testid="close-solena-chat-btn"
              aria-label="Fermer"
            >
              <X style={{ width: 18, height: 18 }} strokeWidth={1.5} />
            </button>
          </div>

          {/* Messages */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto px-5 py-6 space-y-4"
            style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(212,180,106,0.3) transparent' }}
            data-testid="solena-chat-messages"
          >
            {visibleMessages.length === 0 && !loading && (
              <div className="text-center py-12" style={{ color: 'rgba(244,232,210,0.4)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                Solena consulte ton ciel…
              </div>
            )}
            {visibleMessages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  style={{
                    maxWidth: '85%',
                    padding: '12px 16px',
                    borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                    background: m.role === 'user'
                      ? 'linear-gradient(135deg, rgba(212,180,106,0.20), rgba(212,180,106,0.10))'
                      : 'rgba(255,255,255,0.04)',
                    border: m.role === 'user'
                      ? '1px solid rgba(212,180,106,0.35)'
                      : '1px solid rgba(255,255,255,0.06)',
                    color: '#F4E8D2',
                    fontSize: '0.95rem',
                    lineHeight: 1.55,
                    fontFamily: m.role === 'assistant' ? 'Cormorant Garamond, serif' : 'inherit',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div style={{
                  padding: '12px 16px',
                  borderRadius: '18px 18px 18px 4px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  color: 'rgba(244,232,210,0.6)',
                  fontSize: '0.9rem',
                  display: 'flex', alignItems: 'center', gap: 8,
                  fontStyle: 'italic',
                }}>
                  <Loader2 className="animate-spin" style={{ width: 14, height: 14, color: '#D4B46A' }} strokeWidth={2} />
                  Solena consulte les étoiles…
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4" style={{ borderColor: 'rgba(212,180,106,0.18)' }}>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                placeholder="Pose ta question à Solena…"
                disabled={loading}
                className="flex-1 py-3 px-4 outline-none text-white placeholder-white/30"
                style={{
                  background: 'rgba(0,0,0,0.4)',
                  border: '1px solid rgba(212,180,106,0.25)',
                  borderRadius: 999,
                  fontSize: 14,
                  fontFamily: 'Cormorant Garamond, serif',
                }}
                data-testid="solena-chat-input"
              />
              <button
                onClick={send}
                disabled={loading || !input.trim()}
                className="rounded-full flex items-center justify-center transition-all hover:scale-105 disabled:opacity-40"
                style={{
                  width: 44, height: 44,
                  background: 'linear-gradient(135deg, #D4B46A, #F4D98C)',
                  color: '#0C0918',
                  border: 'none',
                  cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                  boxShadow: '0 6px 20px rgba(212,180,106,0.35)',
                }}
                data-testid="solena-chat-send-btn"
                aria-label="Envoyer"
              >
                {loading ? <Loader2 className="animate-spin" style={{ width: 16, height: 16 }} strokeWidth={2} /> : <Send style={{ width: 16, height: 16 }} strokeWidth={2} />}
              </button>
            </div>
            <div className="text-[9px] uppercase mt-3 text-center opacity-50" style={{ color: '#D4B46A', letterSpacing: '0.2em' }}>
              <Sparkles style={{ width: 9, height: 9, display: 'inline', marginRight: 4 }} strokeWidth={1.5} />
              Solena · propulsée par une IA divinatoire
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
