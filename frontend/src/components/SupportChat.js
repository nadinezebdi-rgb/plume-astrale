import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════════════
   Floating support chat widget
   GET/POST /api/chat/support — IA gpt-5.4 avec contexte Plume
   Fallback : escalade → contact@plume-astrale.fr
   ═══════════════════════════════════════════════════════════ */

const styles = `
  .pac-bubble{position:fixed;bottom:20px;right:20px;z-index:90;
    width:60px;height:60px;border-radius:50%;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 8px 30px rgba(201,162,75,.45),inset 0 1px 0 rgba(255,255,255,.35);
    cursor:pointer;border:none;font-size:28px;font-family:Georgia,serif;
    transition:transform .2s ease;animation:pac-float 4s ease-in-out infinite;}
  .pac-bubble:hover,.pac-bubble:focus{transform:scale(1.08);animation-play-state:paused;}
  @keyframes pac-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
  .pac-bubble-dot{position:absolute;top:-4px;right:-4px;
    min-width:22px;height:22px;padding:0 6px;border-radius:11px;
    background:#ef4444;color:#fff;font-size:11px;font-weight:700;
    font-family:'Helvetica Neue',Arial,sans-serif;
    display:flex;align-items:center;justify-content:center;
    border:2px solid #0b0f24;
    box-shadow:0 2px 8px rgba(239,68,68,.5);
    animation:pac-dot-pulse 1.6s ease-in-out infinite;}
  @keyframes pac-dot-pulse{
    0%,100%{box-shadow:0 2px 8px rgba(239,68,68,.5),0 0 0 0 rgba(239,68,68,.5);}
    50%{box-shadow:0 2px 8px rgba(239,68,68,.5),0 0 0 8px rgba(239,68,68,0);}
  }

  .pac-panel{position:fixed;bottom:20px;right:20px;z-index:100;
    width:min(360px, calc(100vw - 40px));height:min(520px, calc(100vh - 40px));
    background:#0b0f24;border:1px solid rgba(201,162,75,.35);border-radius:18px;
    box-shadow:0 20px 60px rgba(0,0,0,.55);overflow:hidden;
    display:flex;flex-direction:column;font-family:Georgia,serif;color:#e8e6f0;
    animation:pac-slide-in .28s ease-out;}
  @keyframes pac-slide-in{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  .pac-header{background:linear-gradient(180deg,#141a33,#0b0f24);
    padding:16px 18px;border-bottom:1px solid rgba(201,162,75,.2);
    display:flex;align-items:center;gap:10px;}
  .pac-avatar{width:36px;height:36px;border-radius:50%;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:600;}
  .pac-header-t{flex:1;}
  .pac-header-title{font-size:14px;color:#e8e6f0;font-weight:600;}
  .pac-header-sub{font-size:11px;color:#7c7ce5;letter-spacing:.04em;}
  .pac-close{background:transparent;border:none;color:#8a86a0;cursor:pointer;
    font-size:22px;padding:4px 8px;line-height:1;transition:color .18s;}
  .pac-close:hover{color:#f87171;}

  .pac-body{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:12px;}
  .pac-msg{max-width:82%;padding:10px 14px;border-radius:14px;font-size:13px;line-height:1.5;
    word-wrap:break-word;}
  .pac-msg-user{align-self:flex-end;background:rgba(201,162,75,.15);
    border:1px solid rgba(201,162,75,.3);color:#e8e6f0;}
  .pac-msg-bot{align-self:flex-start;background:rgba(20,26,51,.7);
    border:1px solid rgba(255,255,255,.06);color:#e8e6f0;}
  .pac-msg-escalate{border-color:rgba(217,178,106,.4);background:rgba(217,178,106,.08);}
  .pac-msg-human{align-self:flex-start;background:linear-gradient(135deg,rgba(201,162,75,.18),rgba(226,192,124,.1));
    border:1px solid rgba(201,162,75,.45);color:#f5efdf;max-width:88%;padding:12px 14px;
    border-radius:14px;font-size:13px;line-height:1.5;
    box-shadow:0 4px 20px rgba(201,162,75,.15);
    animation:pac-human-in .4s ease-out;}
  @keyframes pac-human-in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
  .pac-msg-human-head{display:flex;align-items:center;gap:6px;margin-bottom:6px;
    padding-bottom:6px;border-bottom:1px dashed rgba(201,162,75,.3);}
  .pac-msg-human-avatar{width:22px;height:22px;border-radius:50%;
    background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;}
  .pac-msg-human-label{font-size:10px;color:#c9a24b;letter-spacing:.08em;
    text-transform:uppercase;font-weight:600;}
  .pac-typing{align-self:flex-start;color:#8a86a0;font-size:12px;font-style:italic;
    padding:8px 14px;}
  .pac-support{margin-top:6px;padding-top:8px;border-top:1px dashed rgba(217,178,106,.25);
    font-size:11px;color:#d9b26a;}
  .pac-support a{color:#d9b26a;text-decoration:none;font-weight:600;
    border-bottom:1px dashed rgba(217,178,106,.4);}

  .pac-footer{border-top:1px solid rgba(255,255,255,.06);padding:12px;
    background:#0b0f24;}
  .pac-inp-wrap{display:flex;gap:8px;align-items:flex-end;}
  .pac-inp{flex:1;background:rgba(11,15,36,.7);border:1px solid rgba(201,162,75,.2);
    color:#e8e6f0;padding:10px 12px;border-radius:12px;font-family:Georgia,serif;
    font-size:13px;resize:none;max-height:100px;min-height:40px;line-height:1.4;}
  .pac-inp:focus{outline:none;border-color:#c9a24b;box-shadow:0 0 0 2px rgba(201,162,75,.15);}
  .pac-send{background:linear-gradient(135deg,#c9a24b,#e2c07c);color:#1a1030;
    border:none;border-radius:12px;padding:0 16px;height:40px;cursor:pointer;
    font-family:Georgia,serif;font-weight:600;font-size:14px;
    box-shadow:0 4px 14px rgba(201,162,75,.35);transition:transform .18s;}
  .pac-send:hover{transform:translateY(-1px);}
  .pac-send:disabled{opacity:.5;cursor:not-allowed;}

  .pac-legal{font-size:10px;color:#7d7a90;text-align:center;margin-top:8px;font-style:italic;}

  .pac-thumbs{display:flex;align-items:center;gap:6px;margin:4px 0 6px 12px;
    font-size:10px;color:#7d7a90;letter-spacing:.02em;}
  .pac-thumb-q{font-style:italic;}
  .pac-thumb-btn{background:transparent;border:1px solid rgba(201,162,75,.25);
    color:#c9a24b;padding:2px 8px;border-radius:12px;cursor:pointer;
    font-size:12px;line-height:1;transition:all .18s;}
  .pac-thumb-btn:hover{background:rgba(201,162,75,.1);border-color:rgba(201,162,75,.5);}
  .pac-thumb-done{color:#4ADE80;font-size:10px;font-style:italic;}`;

const INITIAL_MESSAGE = {
  role: 'assistant',
  content: "Bonjour ! Je suis l'assistante virtuelle de Plume Astrale. Je peux te renseigner sur la lecture complète, la garantie, ton compte ou l'astrologie chez Soléna. Que puis-je t'expliquer ?",
  escalate: false,
};

const SESSION_KEY = 'plume_chat_session_id';
const LAST_SEEN_KEY = 'plume_chat_last_seen_at';

export default function SupportChat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    try { return localStorage.getItem(SESSION_KEY); } catch (_e) { return null; }
  });
  const [lastAdminReplyAt, setLastAdminReplyAt] = useState(() => {
    try { return localStorage.getItem(LAST_SEEN_KEY); } catch (_e) { return null; }
  });
  const [unreadCount, setUnreadCount] = useState(0);
  const bodyRef = useRef(null);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [messages, busy]);

  // Persiste sessionId au localStorage dès qu'on en obtient un
  useEffect(() => {
    if (sessionId) {
      try { localStorage.setItem(SESSION_KEY, sessionId); } catch (_e) { /* ok */ }
    }
  }, [sessionId]);

  // Poll pour recuperer les reponses humaines de Soléna
  // Tourne même quand le panel est fermé, tant qu'on a un sessionId
  useEffect(() => {
    if (!sessionId) return;
    let cancel = false;
    const tick = async () => {
      try {
        const url = new URL(`${API}/api/chat/session-updates`);
        url.searchParams.set('session_id', sessionId);
        if (lastAdminReplyAt) url.searchParams.set('since', lastAdminReplyAt);
        const r = await fetch(url.toString());
        const d = await r.json();
        if (cancel) return;
        const fresh = d?.messages || [];
        if (fresh.length > 0) {
          if (open) {
            // Panel ouvert : injecte les messages ET marque comme vu
            setMessages((cur) => [...cur, ...fresh.map((m) => ({
              role: 'human',
              content: m.message,
              author: m.author,
              at: m.at,
            }))]);
            const lastAt = fresh[fresh.length - 1].at;
            setLastAdminReplyAt(lastAt);
            try { localStorage.setItem(LAST_SEEN_KEY, lastAt); } catch (_e) { /* ok */ }
          } else {
            // Panel fermé : incrémente le badge, ne consomme pas encore
            setUnreadCount((n) => n + fresh.length);
          }
        }
      } catch (_e) { /* silent */ }
    };
    // Interval : 20s si panel ouvert, 45s si fermé (moins agressif)
    const intervalMs = open ? 20000 : 45000;
    tick();
    const id = setInterval(tick, intervalMs);
    return () => { cancel = true; clearInterval(id); };
  }, [sessionId, open, lastAdminReplyAt]);

  // Consomme le badge et charge les messages non lus au ouverture
  const openPanel = async () => {
    setOpen(true);
    if (!sessionId || unreadCount === 0) return;
    // Fetch les non-lus depuis last_seen et les injecte
    try {
      const url = new URL(`${API}/api/chat/session-updates`);
      url.searchParams.set('session_id', sessionId);
      if (lastAdminReplyAt) url.searchParams.set('since', lastAdminReplyAt);
      const r = await fetch(url.toString());
      const d = await r.json();
      const fresh = d?.messages || [];
      if (fresh.length > 0) {
        setMessages((cur) => [...cur, ...fresh.map((m) => ({
          role: 'human',
          content: m.message,
          author: m.author,
          at: m.at,
        }))]);
        const lastAt = fresh[fresh.length - 1].at;
        setLastAdminReplyAt(lastAt);
        try { localStorage.setItem(LAST_SEEN_KEY, lastAt); } catch (_e) { /* ok */ }
      }
    } catch (_e) { /* silent */ }
    setUnreadCount(0);
  };

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;
    const userMsg = { role: 'user', content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput('');
    setBusy(true);
    try {
      const history = messages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .map((m) => ({ role: m.role, content: m.content }));
      const r = await axios.post(`${API}/api/chat/support`, {
        message: text,
        session_id: sessionId,
        history,
      });
      if (!sessionId && r.data?.session_id) setSessionId(r.data.session_id);
      setMessages((cur) => [...cur, {
        role: 'assistant',
        content: r.data?.reply || 'Erreur inattendue.',
        escalate: !!r.data?.escalate,
        support_email: r.data?.support_email,
        exchange_uid: r.data?.exchange_uid,
        session_id: r.data?.session_id,
        helpful: null,
      }]);
    } catch (e) {
      setMessages((cur) => [...cur, {
        role: 'assistant',
        content: "Je n'arrive pas à te répondre pour le moment. Écris-nous à contact@plume-astrale.fr, on te répond en quelques heures.",
        escalate: true,
        support_email: 'contact@plume-astrale.fr',
      }]);
    } finally {
      setBusy(false);
    }
  };

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const sendFeedback = async (msgIdx, helpful) => {
    const msg = messages[msgIdx];
    if (!msg || !msg.exchange_uid || !msg.session_id) return;
    if (msg.helpful !== null && msg.helpful !== undefined) return; // Déjà voté
    try {
      await axios.post(`${API}/api/chat/feedback`, {
        session_id: msg.session_id,
        exchange_uid: msg.exchange_uid,
        helpful,
      });
      setMessages((cur) => cur.map((m, i) => i === msgIdx ? { ...m, helpful } : m));
    } catch (_e) { /* silent */ }
  };

  return (
    <>
      <style>{styles}</style>
      {!open && (
        <button
          type="button"
          className="pac-bubble"
          onClick={openPanel}
          data-testid="support-chat-bubble"
          aria-label={unreadCount > 0
            ? `Ouvrir le chat de support (${unreadCount} nouvelle${unreadCount > 1 ? 's' : ''} réponse${unreadCount > 1 ? 's' : ''})`
            : 'Ouvrir le chat de support'}
        >
          ✦
          {unreadCount > 0 && (
            <span className="pac-bubble-dot" data-testid="support-chat-unread-dot">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      )}
      {open && (
        <div className="pac-panel" data-testid="support-chat-panel">
          <div className="pac-header">
            <div className="pac-avatar" aria-hidden="true">✦</div>
            <div className="pac-header-t">
              <div className="pac-header-title">Assistante Plume Astrale</div>
              <div className="pac-header-sub">IA · réponse en quelques secondes</div>
            </div>
            <button
              type="button"
              className="pac-close"
              onClick={() => setOpen(false)}
              data-testid="support-chat-close"
              aria-label="Fermer"
            >
              ✕
            </button>
          </div>
          <div className="pac-body" ref={bodyRef} data-testid="support-chat-body">
            {messages.map((m, i) => (
              <div key={i}>
                {m.role === 'human' ? (
                  <div
                    className="pac-msg pac-msg-human"
                    data-testid="support-chat-msg-human"
                  >
                    <div className="pac-msg-human-head">
                      <span className="pac-msg-human-avatar">S</span>
                      <span className="pac-msg-human-label">
                        {m.author || 'Plume Astrale'} · support
                      </span>
                    </div>
                    <div>{m.content}</div>
                  </div>
                ) : (
                  <div
                    className={`pac-msg ${m.role === 'user' ? 'pac-msg-user' : 'pac-msg-bot'} ${m.escalate ? 'pac-msg-escalate' : ''}`}
                    data-testid={`support-chat-msg-${m.role}`}
                  >
                    {m.content}
                    {m.escalate && m.support_email && (
                      <div className="pac-support">
                        Contact humain :{' '}
                        <a href={`mailto:${m.support_email}?subject=Plume Astrale - Support`}
                          data-testid="support-chat-escalate-mail">
                          {m.support_email}
                        </a>
                      </div>
                    )}
                  </div>
                )}
                {/* FAQ Bridge : thumbs sur les réponses IA (skip la 1ere = welcome) */}
                {m.role === 'assistant' && m.exchange_uid && (
                  <div className="pac-thumbs" data-testid={`support-chat-thumbs-${i}`}>
                    {m.helpful === true ? (
                      <span className="pac-thumb-done">✓ Merci pour ton retour</span>
                    ) : m.helpful === false ? (
                      <span className="pac-thumb-done">✓ Retour noté</span>
                    ) : (
                      <>
                        <span className="pac-thumb-q">Cette réponse a-t-elle aidé ?</span>
                        <button type="button" className="pac-thumb-btn"
                          onClick={() => sendFeedback(i, true)}
                          data-testid={`support-chat-thumb-up-${i}`}
                          aria-label="Oui, réponse utile">👍</button>
                        <button type="button" className="pac-thumb-btn"
                          onClick={() => sendFeedback(i, false)}
                          data-testid={`support-chat-thumb-down-${i}`}
                          aria-label="Non, réponse à améliorer">👎</button>
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <div className="pac-typing" data-testid="support-chat-typing">L'assistante écrit…</div>
            )}
          </div>
          <div className="pac-footer">
            <div className="pac-inp-wrap">
              <textarea
                className="pac-inp"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKey}
                placeholder="Écris ta question…"
                rows={1}
                data-testid="support-chat-input"
                disabled={busy}
              />
              <button
                type="button"
                className="pac-send"
                onClick={send}
                disabled={busy || !input.trim()}
                data-testid="support-chat-send"
              >
                ➤
              </button>
            </div>
            <div className="pac-legal">
              Guidance à visée informative · Pour un contact humain :{' '}
              <a href="mailto:contact@plume-astrale.fr" style={{ color: '#d9b26a' }}>
                contact@plume-astrale.fr
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
