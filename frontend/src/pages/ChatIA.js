import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, Sparkles, Trash2 } from 'lucide-react';
import SEO from '@/components/SEO';

const ChatIA = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Bienvenue dans le Chat Astral. Pose-moi une question sur ton avenir, ta compatibilite, ton theme natal ou tout ce qui touche aux etoiles. Les astres sont a ton ecoute.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const getBirthData = () => {
    try {
      const raw = localStorage.getItem('pa_formData');
      if (raw) {
        const data = JSON.parse(raw);
        const d = data.dateNaissance ? new Date(data.dateNaissance) : null;
        if (d) {
          return {
            name: data.prenom || 'Utilisateur',
            day: d.getDate(),
            month: d.getMonth() + 1,
            year: d.getFullYear(),
            hour: data.heureNaissance ? parseInt(data.heureNaissance.split(':')[0]) : 12,
            min: data.heureNaissance ? parseInt(data.heureNaissance.split(':')[1]) : 0,
            lat: parseFloat(data.latitude) || 48.8566,
            lon: parseFloat(data.longitude) || 2.3522,
            tzone: 1,
          };
        }
      }
    } catch (e) { /* ignore */ }
    return {
      name: 'Utilisateur',
      day: 15, month: 5, year: 1992,
      hour: 14, min: 30,
      lat: 48.8566, lon: 2.3522, tzone: 1,
    };
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);

    try {
      const birthData = getBirthData();
      const res = await fetch('/api/astrology/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          ...birthData,
          lang: 'fr',
        }),
      });

      const json = await res.json();

      if (json.success && json.data) {
        const reply = typeof json.data === 'string'
          ? json.data
          : json.data.response || json.data.message || json.data.answer || JSON.stringify(json.data);
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "Les astres sont momentanement voiles. Reessaie dans un instant." }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: "Une perturbation cosmique empeche la connexion. Verifie ta connexion et reessaie." }]);
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
        content: "Conversation reinitialise. Pose-moi une nouvelle question, les etoiles sont pretes.",
      },
    ]);
  };

  return (
    <>
      <SEO title="Chat IA Astral — Plume Astrale" description="Pose tes questions aux etoiles avec notre chat IA astrologique." />
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0B0B0F 0%, #110E1A 50%, #0B0B0F 100%)',
        paddingTop: 80,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', padding: '24px 16px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles style={{ width: 22, height: 22, color: '#D4B46A' }} />
            <h1 style={{
              fontFamily: 'Cinzel, serif',
              fontSize: 'clamp(20px, 4vw, 28px)',
              color: '#D4B46A',
              letterSpacing: '0.12em',
              margin: 0,
            }}>
              Chat Astral IA
            </h1>
          </div>
          <p style={{
            color: 'rgba(212,180,106,0.5)',
            fontSize: 13,
            letterSpacing: '0.06em',
            margin: 0,
          }}>
            Interroge les astres — pose ta question a l'univers
          </p>
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
            minHeight: 'calc(100vh - 320px)',
          }}>
            {messages.map((msg, i) => (
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
            ))}

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
            >
              <Trash2 style={{ width: 18, height: 18 }} />
            </button>

            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Pose ta question aux etoiles..."
              rows={1}
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
              }}
              onFocus={e => { e.currentTarget.style.borderColor = 'rgba(212,180,106,0.4)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(212,180,106,0.15)'; }}
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                background: input.trim() && !loading
                  ? 'linear-gradient(135deg, rgba(212,180,106,0.25), rgba(212,180,106,0.12))'
                  : 'rgba(255,255,255,0.04)',
                border: '1px solid',
                borderColor: input.trim() && !loading ? 'rgba(212,180,106,0.4)' : 'rgba(255,255,255,0.08)',
                borderRadius: 12,
                padding: 10,
                cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                color: input.trim() && !loading ? '#D4B46A' : 'rgba(212,180,106,0.25)',
                flexShrink: 0,
                transition: 'all 0.2s',
              }}
            >
              <Send style={{ width: 18, height: 18 }} />
            </button>
          </div>
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
