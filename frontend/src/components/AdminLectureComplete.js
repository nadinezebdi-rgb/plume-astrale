import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { RefreshCw, CheckCircle2, XCircle, Clock, AlertTriangle, Mail, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';

const API = process.env.REACT_APP_BACKEND_URL;

const KIND_LABEL = {
  theme_natal_pdf_oneshot: 'Thème Natal',
  karma_destin_analysis: 'Karma & Destinée',
  kabbale_arbre_de_vie: 'Arbre de Vie Kabbale',
  fenetre_rencontre_avancee: 'Fenêtres Rencontre',
  rencontres_ultime: 'Rencontres Ultime',
};

const StatusPill = ({ status, ready, error }) => {
  if (error) {
    return (
      <span title={error} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#f87171', fontSize: 12 }}>
        <XCircle className="w-3.5 h-3.5" /> échec
      </span>
    );
  }
  if (ready || status === 'success') {
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#4ADE80', fontSize: 12 }}>
        <CheckCircle2 className="w-3.5 h-3.5" /> prêt
      </span>
    );
  }
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#d9b26a', fontSize: 12 }}>
      <Clock className="w-3.5 h-3.5" /> en cours
    </span>
  );
};

export default function AdminLectureComplete({ token }) {
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [abStats, setAbStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [redispatching, setRedispatching] = useState(null);
  const [refunding, setRefunding] = useState(null);
  const [expandedTimeline, setExpandedTimeline] = useState(null);

  // Modal refund state
  const [refundModalOpen, setRefundModalOpen] = useState(false);
  const [refundTarget, setRefundTarget] = useState(null);  // {sid, email, amount, admin_bypass}
  const [refundReason, setRefundReason] = useState('');
  const [refundSkipStripe, setRefundSkipStripe] = useState(false);
  const [refundPartial, setRefundPartial] = useState(false);
  const [refundAmount, setRefundAmount] = useState('');
  const [refundError, setRefundError] = useState(null);
  const [refundSuccess, setRefundSuccess] = useState(null);
  const [ctrLoading, setCtrLoading] = useState(false);
  const [suggestedPartial, setSuggestedPartial] = useState(null);
  const [suspendNotifications, setSuspendNotifications] = useState(true);
  // Filtres export CSV
  const [exportFilters, setExportFilters] = useState({
    since: '', until: '', payment_status: '', include_bypass: true, refunded_only: false,
  });
  const [slackTesting, setSlackTesting] = useState(false);
  const [slackResult, setSlackResult] = useState(null);
  const [slackWebhookInput, setSlackWebhookInput] = useState('');
  // Settings: A/B force winner + historique alertes
  const [forcedVariant, setForcedVariant] = useState(null);   // 'question' | 'invitation' | null
  const [alertsHistory, setAlertsHistory] = useState([]);
  const [showAlertsHistory, setShowAlertsHistory] = useState(false);
  const [settingsBusy, setSettingsBusy] = useState(false);
  // AI Enrichment toggle (transversal PDFs)
  const [aiEnrichmentEnabled, setAiEnrichmentEnabled] = useState(true);
  const [aiToggleBusy, setAiToggleBusy] = useState(false);
  // LLM usage / cost gauge
  const [llmUsage, setLlmUsage] = useState(null);
  // Weekly recap
  const [recapBusy, setRecapBusy] = useState(false);
  const [recapResult, setRecapResult] = useState(null);
  // SVG cache stats
  const [svgStats, setSvgStats] = useState(null);
  const [svgStatsBusy, setSvgStatsBusy] = useState(false);
  // Testimonials admin validator
  const [testimonialsAdmin, setTestimonialsAdmin] = useState(null);
  const [testimonialsBusy, setTestimonialsBusy] = useState(false);
  // A/B hero panel
  const [heroAbStats, setHeroAbStats] = useState(null);
  const [heroAbBusy, setHeroAbBusy] = useState(false);
  // Chat escalations reply
  const [chatEscalations, setChatEscalations] = useState(null);
  const [chatEscalationsBusy, setChatEscalationsBusy] = useState(false);
  const [chatAnalyticsSummary, setChatAnalyticsSummary] = useState(null);
  const [replyDrafts, setReplyDrafts] = useState({});
  const [showResolved, setShowResolved] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [ordersRes, abRes, settingsRes, llmRes] = await Promise.all([
        axios.get(`${API}/api/lecture-complete/admin/orders`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        axios.get(`${API}/api/lecture-complete/admin/ab-stats`, {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => ({ data: null })),
        axios.get(`${API}/api/lecture-complete/admin/settings`, {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => ({ data: null })),
        axios.get(`${API}/api/lecture-complete/admin/llm-usage`, {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => ({ data: null })),
      ]);
      setOrders(ordersRes.data?.orders || []);
      setStats(ordersRes.data?.stats || null);
      setAbStats(abRes.data || null);
      if (settingsRes.data) {
        setForcedVariant(settingsRes.data.forced_j30_variant || null);
        setAlertsHistory(settingsRes.data.alerts_history || []);
        if (typeof settingsRes.data.ai_enrichment_enabled === 'boolean') {
          setAiEnrichmentEnabled(settingsRes.data.ai_enrichment_enabled);
        }
      }
      setLlmUsage(llmRes.data || null);
    } catch (e) {
      setError(e.response?.data?.detail || 'Chargement impossible.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const redispatch = async (sid) => {
    if (!window.confirm(`Relancer la génération du bundle ${sid} ? (Les 5 PDFs seront régénérés)`)) return;
    setRedispatching(sid);
    try {
      await axios.post(`${API}/api/lecture-complete/admin/redispatch/${sid}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await load();
    } catch (e) {
      alert(e.response?.data?.detail || 'Erreur redispatch');
    } finally {
      setRedispatching(null);
    }
  };

  const openRefundModal = (order) => {
    setRefundTarget({
      sid: order.session_id,
      email: order.email,
      amount: order.amount,
      admin_bypass: order.admin_bypass,
    });
    setRefundReason('');
    setRefundSkipStripe(!!order.admin_bypass);
    setRefundPartial(false);
    setRefundAmount('');
    setRefundError(null);
    setRefundSuccess(null);
    setSuggestedPartial(null);
    setSuspendNotifications(true);
    setRefundModalOpen(true);
  };

  // Detection heuristique : si la raison mentionne un seul PDF defectueux,
  // suggerer un refund partiel de 1/5 (le bundle contient 5 PDFs).
  const detectPartialSuggestion = (reason, order) => {
    if (!reason || !order || order.admin_bypass) return null;
    const txt = reason.toLowerCase();
    // Patterns : "un pdf", "1 pdf", "un seul", "seul rapport", "seule lecture", "juste un", "1 rapport"
    const singlePdfPatterns = [
      /\b(un|1|une)\s+seul(e)?\s+(pdf|rapport|lecture)/,
      /\b(un|1|une)\s+(pdf|rapport|lecture)\s+(défectueux|manquant|cassé|casse|vide|corrompu|illisible|erreur|absent|marche pas|fonctionne pas)/,
      /\bjuste\s+(un|1|une)\s+(pdf|rapport|lecture)/,
      /\b(pdf|rapport|lecture)\s+(défectueux|manquant|cassé|casse|vide|corrompu|illisible)/,
    ];
    const matched = singlePdfPatterns.some((rx) => rx.test(txt));
    if (matched) {
      const suggested = +(order.amount / 5).toFixed(2);
      return {
        amount: suggested,
        note: `Un seul PDF concerné détecté — 1/5 du bundle = ${suggested}€ suggéré.`,
      };
    }
    return null;
  };

  // Watcher : recompute la suggestion des que la raison change
  React.useEffect(() => {
    if (refundModalOpen && refundTarget && !refundPartial) {
      const sugg = detectPartialSuggestion(refundReason, refundTarget);
      setSuggestedPartial(sugg);
    } else if (!refundReason) {
      setSuggestedPartial(null);
    }
  }, [refundReason, refundModalOpen, refundTarget, refundPartial]);

  const confirmRefund = async () => {
    if (!refundTarget) return;
    // Validation refund partiel
    let amount_cents = null;
    if (refundPartial) {
      const parsed = parseFloat(refundAmount);
      if (!parsed || parsed <= 0 || parsed > refundTarget.amount) {
        setRefundError(`Montant invalide (entre 0 et ${refundTarget.amount}€).`);
        return;
      }
      amount_cents = Math.round(parsed * 100);
    }
    setRefunding(refundTarget.sid);
    setRefundError(null);
    try {
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/refund/${refundTarget.sid}`,
        {
          reason: refundReason || undefined,
          skip_stripe: refundSkipStripe,
          amount_cents,
          suspend_notifications: suspendNotifications,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRefundSuccess(r.data);
      await load();
      setTimeout(() => {
        setRefundModalOpen(false);
        setRefundTarget(null);
        setRefundSuccess(null);
      }, 1500);
    } catch (e) {
      setRefundError(e.response?.data?.detail || 'Erreur refund');
    } finally {
      setRefunding(null);
    }
  };

  const loadCTR = async () => {
    if (!token) return;
    setCtrLoading(true);
    try {
      const r = await axios.get(
        `${API}/api/lecture-complete/admin/ab-stats?include_ctr=true`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAbStats(r.data);
    } catch (e) {
      // silent, garde les anciens stats
    } finally {
      setCtrLoading(false);
    }
  };

  const exportCSV = () => {
    const params = new URLSearchParams();
    if (exportFilters.since) params.append('since', exportFilters.since);
    if (exportFilters.until) params.append('until', exportFilters.until);
    if (exportFilters.payment_status) params.append('payment_status', exportFilters.payment_status);
    if (!exportFilters.include_bypass) params.append('include_bypass', 'false');
    if (exportFilters.refunded_only) params.append('refunded_only', 'true');
    const qs = params.toString();
    axios
      .get(`${API}/api/lecture-complete/admin/orders/export${qs ? '?' + qs : ''}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      })
      .then((res) => {
        const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
        const a = document.createElement('a');
        a.href = url;
        a.download = `plume-astrale-commandes-${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      })
      .catch((e) => alert(e.response?.data?.detail || 'Export impossible'));
  };

  const testSlack = async () => {
    setSlackTesting(true);
    setSlackResult(null);
    try {
      const body = slackWebhookInput.trim() ? { webhook_url: slackWebhookInput.trim() } : {};
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/test-slack`, body,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSlackResult(r.data);
      // Recharge l'historique alertes pour voir le log du test
      load();
    } catch (e) {
      setSlackResult({ success: false, reason: e.response?.data?.detail || 'Erreur reseau' });
    } finally {
      setSlackTesting(false);
      setTimeout(() => setSlackResult(null), 6000);
    }
  };

  const toggleAiEnrichment = async () => {
    if (aiToggleBusy) return;
    const nextValue = !aiEnrichmentEnabled;
    if (!nextValue && !window.confirm(
      "Désactiver l'enrichissement IA transversal des PDFs ?\n\n" +
      "Les rapports générés utiliseront un texte statique riche pré-rédigé " +
      "à la voix de Soléna (pages toujours étoffées, aucun appel LLM).\n\n" +
      "Réactive-le dès que ton budget LLM le permet."
    )) return;
    setAiToggleBusy(true);
    try {
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/set-ai-enrichment`,
        { enabled: nextValue },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAiEnrichmentEnabled(!!r.data.ai_enrichment_enabled);
    } catch (e) {
      alert(e.response?.data?.detail || 'Impossible de basculer le toggle IA.');
    } finally {
      setAiToggleBusy(false);
    }
  };

  const setForcedVariantHandler = async (variant) => {
    if (settingsBusy) return;
    if (variant && !window.confirm(
      `Forcer 100% des envois J+30 sur la variante "${variant}" ?\n\n` +
      `Toutes les nouvelles séquences J+30 utiliseront exclusivement cette version.`
    )) return;
    setSettingsBusy(true);
    try {
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/set-forced-variant`,
        { variant },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setForcedVariant(r.data.forced_j30_variant || null);
    } catch (e) {
      alert(e.response?.data?.detail || 'Impossible de forcer la variante.');
    } finally {
      setSettingsBusy(false);
    }
  };

  const sendWeeklyRecapNow = async () => {
    if (recapBusy) return;
    if (!window.confirm('Envoyer le recap hebdo maintenant à tous les admins ?')) return;
    setRecapBusy(true);
    setRecapResult(null);
    try {
      const r = await axios.post(
        `${API}/api/lecture-complete/admin/weekly-recap-now`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecapResult(r.data);
      load();
    } catch (e) {
      setRecapResult({ error: e.response?.data?.detail || 'Erreur' });
    } finally {
      setRecapBusy(false);
      setTimeout(() => setRecapResult(null), 8000);
    }
  };

  const loadSvgStats = async () => {
    if (svgStatsBusy) return;
    setSvgStatsBusy(true);
    try {
      const r = await axios.get(
        `${API}/api/admin/cache/svg/stats`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSvgStats(r.data);
    } catch (e) {
      setSvgStats({ error: e.response?.data?.detail || 'Erreur' });
    } finally {
      setSvgStatsBusy(false);
    }
  };

  const loadTestimonialsAdmin = useCallback(async () => {
    if (!token) return;
    setTestimonialsBusy(true);
    try {
      const r = await axios.get(
        `${API}/api/landing/testimonials/admin`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTestimonialsAdmin(r.data?.testimonials || []);
    } catch (_e) {
      setTestimonialsAdmin([]);
    } finally {
      setTestimonialsBusy(false);
    }
  }, [token]);

  const approveTestimonial = async (id) => {
    try {
      await axios.post(
        `${API}/api/landing/testimonials/${id}/approve`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadTestimonialsAdmin();
    } catch (e) { alert(e.response?.data?.detail || 'Erreur'); }
  };

  const deleteTestimonial = async (id) => {
    if (!window.confirm('Supprimer définitivement ce témoignage ?')) return;
    try {
      await axios.delete(
        `${API}/api/landing/testimonials/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadTestimonialsAdmin();
    } catch (e) { alert(e.response?.data?.detail || 'Erreur'); }
  };

  const loadHeroAbStats = useCallback(async () => {
    if (!token) return;
    setHeroAbBusy(true);
    try {
      const r = await axios.get(
        `${API}/api/landing/ab/stats`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setHeroAbStats(r.data);
    } catch (_e) {
      setHeroAbStats(null);
    } finally {
      setHeroAbBusy(false);
    }
  }, [token]);

  const setHeroForcedVariant = async (variant) => {
    if (variant && !window.confirm(
      `Verrouiller 100% du trafic hero sur la variante "${variant}" ?`
    )) return;
    try {
      const r = await axios.post(
        `${API}/api/landing/ab/set-forced-variant`,
        { variant },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setHeroAbStats((s) => s ? { ...s, forced_variant: r.data.forced_variant } : s);
      loadHeroAbStats();
    } catch (e) { alert(e.response?.data?.detail || 'Erreur'); }
  };

  const loadChatEscalations = useCallback(async () => {
    if (!token) return;
    setChatEscalationsBusy(true);
    try {
      const r = await axios.get(
        `${API}/api/chat/analytics`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setChatEscalations(r.data?.escalations || []);
      setChatAnalyticsSummary({
        total_exchanges: r.data?.total_exchanges || 0,
        unique_sessions: r.data?.unique_sessions || 0,
        escalate_rate_pct: r.data?.escalate_rate_pct || 0,
        helpful_rate_pct: r.data?.helpful_rate_pct,
        positive_feedback: r.data?.positive_feedback || 0,
        negative_feedback: r.data?.negative_feedback || 0,
        faq_gaps: r.data?.faq_gaps || [],
      });
    } catch (_e) {
      setChatEscalations([]);
      setChatAnalyticsSummary(null);
    } finally {
      setChatEscalationsBusy(false);
    }
  }, [token]);

  const sendAdminReply = async (sessionId) => {
    const msg = (replyDrafts[sessionId] || '').trim();
    if (msg.length < 2) { alert('Message trop court.'); return; }
    try {
      await axios.post(
        `${API}/api/chat/admin-reply`,
        { session_id: sessionId, message: msg },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setReplyDrafts((d) => ({ ...d, [sessionId]: '' }));
      loadChatEscalations();
      alert('Réponse envoyée à l\'utilisatrice — elle la verra dans son chat.');
    } catch (e) { alert(e.response?.data?.detail || 'Erreur envoi.'); }
  };

  const resolveEscalation = async (sessionId) => {
    try {
      await axios.post(
        `${API}/api/chat/escalation/${sessionId}/resolve`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadChatEscalations();
    } catch (e) { alert(e.response?.data?.detail || 'Erreur'); }
  };

  const reopenEscalation = async (sessionId) => {
    try {
      await axios.post(
        `${API}/api/chat/escalation/${sessionId}/reopen`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadChatEscalations();
    } catch (e) { alert(e.response?.data?.detail || 'Erreur'); }
  };

  // Auto-load admin panels sur mount une fois le token dispo
  React.useEffect(() => {
    if (token) {
      loadTestimonialsAdmin();
      loadHeroAbStats();
      loadChatEscalations();
    }
  }, [token, loadTestimonialsAdmin, loadHeroAbStats, loadChatEscalations]);

  return (
    <div data-testid="admin-lecture-complete-panel">
      {/* ═══ Chat Analytics Card (top summary) ═══ */}
      {chatAnalyticsSummary && chatAnalyticsSummary.total_exchanges > 0 && (
        <div
          data-testid="admin-lc-chat-analytics-card"
          style={{
            marginBottom: 16, padding: 16, borderRadius: 12,
            background: 'linear-gradient(135deg, rgba(167,139,250,0.06), rgba(201,162,75,0.04))',
            border: '1px solid rgba(167,139,250,0.25)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <span style={{ fontSize: 20 }}>✦</span>
            <span style={{ color: '#A78BFA', fontSize: 11, letterSpacing: '.14em',
              textTransform: 'uppercase', fontWeight: 600 }}>
              Chat IA — Insights
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 12, marginBottom: 12 }}>
            <div data-testid="admin-lc-chat-analytics-total" style={{ padding: 10, background: 'rgba(11,16,32,0.4)', borderRadius: 8 }}>
              <div style={{ fontSize: 9, color: '#8a86a0', textTransform: 'uppercase', letterSpacing: '.08em' }}>Échanges</div>
              <div style={{ fontSize: 20, color: '#e8e6f0', fontWeight: 600 }}>{chatAnalyticsSummary.total_exchanges}</div>
            </div>
            <div data-testid="admin-lc-chat-analytics-sessions" style={{ padding: 10, background: 'rgba(11,16,32,0.4)', borderRadius: 8 }}>
              <div style={{ fontSize: 9, color: '#8a86a0', textTransform: 'uppercase', letterSpacing: '.08em' }}>Sessions</div>
              <div style={{ fontSize: 20, color: '#e8e6f0', fontWeight: 600 }}>{chatAnalyticsSummary.unique_sessions}</div>
            </div>
            <div data-testid="admin-lc-chat-analytics-escalate" style={{ padding: 10, background: 'rgba(11,16,32,0.4)', borderRadius: 8 }}>
              <div style={{ fontSize: 9, color: '#8a86a0', textTransform: 'uppercase', letterSpacing: '.08em' }}>Escalate rate</div>
              <div style={{ fontSize: 20, color: chatAnalyticsSummary.escalate_rate_pct > 15 ? '#f87171' : '#e8e6f0', fontWeight: 600 }}>
                {chatAnalyticsSummary.escalate_rate_pct}%
              </div>
            </div>
            <div data-testid="admin-lc-chat-analytics-helpful" style={{ padding: 10, background: 'rgba(11,16,32,0.4)', borderRadius: 8 }}>
              <div style={{ fontSize: 9, color: '#8a86a0', textTransform: 'uppercase', letterSpacing: '.08em' }}>Utile</div>
              <div style={{ fontSize: 20, color: '#4ADE80', fontWeight: 600 }}>
                {chatAnalyticsSummary.helpful_rate_pct != null ? `${chatAnalyticsSummary.helpful_rate_pct}%` : '—'}
              </div>
              <div style={{ fontSize: 9, color: '#8a86a0', marginTop: 2 }}>
                👍 {chatAnalyticsSummary.positive_feedback} · 👎 {chatAnalyticsSummary.negative_feedback}
              </div>
            </div>
          </div>
          {chatAnalyticsSummary.faq_gaps.length > 0 && (
            <div>
              <div style={{ fontSize: 10, color: '#d9b26a', letterSpacing: '.08em',
                textTransform: 'uppercase', marginBottom: 6 }}>
                🎯 Top 3 questions à améliorer
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {chatAnalyticsSummary.faq_gaps.slice(0, 3).map((g, i) => (
                  <div
                    key={i}
                    data-testid={`admin-lc-chat-analytics-gap-${i}`}
                    style={{
                      fontSize: 11, color: '#e8e6f0', fontStyle: 'italic',
                      padding: '6px 10px', background: 'rgba(11,16,32,0.35)', borderRadius: 6,
                      borderLeft: '2px solid rgba(248,113,113,0.4)',
                    }}
                  >
                    « {g.user_message} »
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ fontSize: 22, color: '#d9b26a', margin: 0 }}>
          Lecture Complète — Commandes 97€
        </h2>
        <button
          onClick={load}
          disabled={loading}
          data-testid="admin-lc-refresh"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 14px', borderRadius: 20,
            background: 'rgba(217,178,106,0.12)',
            color: '#d9b26a',
            border: '1px solid rgba(217,178,106,0.35)',
            cursor: 'pointer', fontSize: 12, letterSpacing: '.1em',
            textTransform: 'uppercase',
          }}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Rafraîchir
        </button>
        <button
          onClick={exportCSV}
          data-testid="admin-lc-export-csv"
          style={{
            marginLeft: 8,
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '8px 14px', borderRadius: 20,
            background: 'transparent',
            color: '#A78BFA',
            border: '1px solid rgba(167,139,250,0.4)',
            cursor: 'pointer', fontSize: 12, letterSpacing: '.1em',
            textTransform: 'uppercase',
          }}
        >
          Export CSV
        </button>
        <button
          onClick={testSlack}
          disabled={slackTesting}
          data-testid="admin-lc-test-slack"
          style={{
            marginLeft: 8,
            padding: '8px 14px', borderRadius: 20,
            background: 'transparent',
            color: '#7C7CE5',
            border: '1px solid rgba(124,124,229,0.4)',
            cursor: 'pointer', fontSize: 12, letterSpacing: '.1em',
            textTransform: 'uppercase',
          }}
        >
          {slackTesting ? '...' : 'Tester Slack'}
        </button>
        <button
          onClick={sendWeeklyRecapNow}
          disabled={recapBusy}
          data-testid="admin-lc-weekly-recap-now"
          style={{
            marginLeft: 8,
            padding: '8px 14px', borderRadius: 20,
            background: 'transparent',
            color: '#4ADE80',
            border: '1px solid rgba(74,222,128,0.4)',
            cursor: 'pointer', fontSize: 12, letterSpacing: '.1em',
            textTransform: 'uppercase',
          }}
        >
          {recapBusy ? '...' : 'Envoyer Recap'}
        </button>
      </div>

      {/* Champ URL Slack custom */}
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
        <label style={{ fontSize: 10, color: 'rgba(184,180,201,0.7)', letterSpacing: '.1em', textTransform: 'uppercase' }}>
          Webhook Slack (optionnel)
        </label>
        <input
          type="url"
          value={slackWebhookInput}
          onChange={(e) => setSlackWebhookInput(e.target.value)}
          placeholder="https://hooks.slack.com/services/… (vide = SLACK_WEBHOOK_URL env)"
          data-testid="admin-lc-slack-webhook-input"
          style={{
            flex: 1, minWidth: 320,
            background: 'rgba(11,16,32,0.5)', color: '#e8e6f0',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 6, padding: '6px 10px', fontSize: 12,
          }}
        />
      </div>

      {slackResult && (
        <div
          data-testid="admin-lc-slack-result"
          style={{
            padding: 10, marginBottom: 12, borderRadius: 8, fontSize: 12,
            background: slackResult.success ? 'rgba(74,222,128,0.12)' : 'rgba(248,113,113,0.12)',
            border: `1px solid ${slackResult.success ? 'rgba(74,222,128,0.35)' : 'rgba(248,113,113,0.35)'}`,
            color: slackResult.success ? '#4ADE80' : '#f87171',
          }}
        >
          {slackResult.success ? '✅ Ping Slack envoyé' : '❌ ' + (slackResult.reason || 'Echec')}
        </div>
      )}

      {recapResult && (
        <div
          data-testid="admin-lc-recap-result"
          style={{
            padding: 10, marginBottom: 12, borderRadius: 8, fontSize: 12,
            background: recapResult.error ? 'rgba(248,113,113,0.12)' : 'rgba(74,222,128,0.12)',
            border: `1px solid ${recapResult.error ? 'rgba(248,113,113,0.35)' : 'rgba(74,222,128,0.35)'}`,
            color: recapResult.error ? '#f87171' : '#4ADE80',
          }}
        >
          {recapResult.error
            ? '❌ ' + recapResult.error
            : `✅ Recap envoyé à ${recapResult.sent_to || 0} admin(s) — ${recapResult.stats?.paid || 0} paiements · ${recapResult.stats?.rate_pct || 0}% refund`
          }
        </div>
      )}

      {/* SVG cache stats collapsible */}
      <div
        data-testid="admin-lc-svg-cache-panel"
        style={{
          marginBottom: 16, padding: 10, borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(124,124,229,0.15)',
        }}
      >
        <button
          type="button"
          onClick={() => { if (!svgStats) loadSvgStats(); else setSvgStats(null); }}
          data-testid="admin-lc-svg-cache-toggle"
          style={{
            background: 'transparent', border: 'none', cursor: 'pointer', padding: 0,
            display: 'flex', alignItems: 'center', gap: 6, width: '100%',
            color: '#7C7CE5', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase',
          }}
        >
          {svgStats ? '▼' : '▶'} Cache SVG (Supabase Storage)
          {svgStats && !svgStats.error && (
            <span style={{ color: 'rgba(184,180,201,0.55)', fontSize: 10, textTransform: 'none', letterSpacing: 0 }}>
              · {svgStats.total_files} fichiers · {svgStats.total_size_human}
            </span>
          )}
          {svgStatsBusy && <span style={{ marginLeft: 8, fontSize: 10, color: 'rgba(184,180,201,0.5)' }}>chargement…</span>}
        </button>
        {svgStats && !svgStats.error && (
          <div data-testid="admin-lc-svg-cache-details" style={{ marginTop: 10, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8 }}>
            {Object.entries(svgStats.by_chart_type || {}).map(([ct, s]) => (
              <div key={ct} style={{ padding: 8, borderRadius: 6, background: 'rgba(11,16,32,0.4)', fontSize: 11 }}>
                <div style={{ color: '#e8e6f0', fontWeight: 600 }}>{ct}</div>
                <div style={{ color: 'rgba(184,180,201,0.7)', marginTop: 2 }}>{s.files} fichier{s.files > 1 ? 's' : ''}</div>
                <div style={{ color: 'rgba(184,180,201,0.55)', fontSize: 10 }}>
                  {s.size_bytes ? `${Math.round(s.size_bytes / 1024)} KB` : '—'}
                </div>
              </div>
            ))}
          </div>
        )}
        {svgStats?.error && (
          <div style={{ marginTop: 8, fontSize: 11, color: '#f87171' }}>Erreur : {svgStats.error}</div>
        )}
      </div>

      {/* ═══ Jauge Coût LLM (mensuel) ═══ */}
      {llmUsage && (() => {
        const cur = llmUsage.current || { total_calls: 0, total_cost_eur: 0, by_usage: {} };
        const budget = Number(llmUsage.budget_eur || 30);
        const spent = Number(cur.total_cost_eur || 0);
        const pct = budget > 0 ? Math.min(100, (spent / budget) * 100) : 0;
        const state = pct >= 90 ? 'danger' : pct >= 65 ? 'warn' : 'ok';
        const color = state === 'danger' ? '#f87171' : state === 'warn' ? '#fbbf24' : '#4ADE80';
        const usages = Object.entries(cur.by_usage || {});
        return (
          <div
            data-testid="admin-lc-llm-usage-panel"
            style={{
              marginBottom: 16, padding: 14, borderRadius: 12,
              background: 'rgba(24,24,32,0.55)',
              border: `1px solid ${color}44`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 11, letterSpacing: '.14em', textTransform: 'uppercase', color, fontWeight: 700 }}>
                ✦ Jauge coût GPT — {llmUsage.current_month}
              </div>
              <div style={{ fontSize: 11, color: 'rgba(232,230,240,0.6)' }}>
                Budget mensuel : <b style={{ color: '#E8C766' }}>{budget.toFixed(0)} €</b>
              </div>
            </div>

            <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ flex: 1, height: 10, borderRadius: 6, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                <div style={{
                  width: `${pct}%`, height: '100%',
                  background: `linear-gradient(90deg, ${color}, ${color}bb)`,
                  transition: 'width .5s ease',
                }} />
              </div>
              <div style={{ minWidth: 110, textAlign: 'right' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color }}>
                  {spent.toFixed(2)} €
                </div>
                <div style={{ fontSize: 10, color: 'rgba(232,230,240,0.55)', letterSpacing: '.06em' }}>
                  {pct.toFixed(0)}% du budget
                </div>
              </div>
            </div>

            <div style={{
              marginTop: 12, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8,
            }}>
              <div style={{ fontSize: 11, color: 'rgba(232,230,240,0.7)' }}>
                <div style={{ color: 'rgba(232,230,240,0.5)', letterSpacing: '.06em', fontSize: 10, textTransform: 'uppercase' }}>Total appels</div>
                <div style={{ fontSize: 15, color: '#fff', marginTop: 2, fontWeight: 600 }}>{cur.total_calls}</div>
              </div>
              {usages.map(([usage, stats]) => (
                <div key={usage} style={{ fontSize: 11, color: 'rgba(232,230,240,0.7)' }}>
                  <div style={{ color: 'rgba(232,230,240,0.5)', letterSpacing: '.06em', fontSize: 10, textTransform: 'uppercase' }}>{usage}</div>
                  <div style={{ fontSize: 13, color: '#fff', marginTop: 2 }}>
                    <b>{stats.calls}</b> · <span style={{ color: '#E8C766' }}>{Number(stats.cost_eur || 0).toFixed(2)} €</span>
                  </div>
                </div>
              ))}
            </div>

            {state !== 'ok' && (
              <div style={{
                marginTop: 12, padding: '8px 10px', borderRadius: 8, fontSize: 11,
                background: `${color}18`, color, lineHeight: 1.5,
              }}>
                {state === 'danger'
                  ? "⚠ Budget quasi atteint. Envisage de désactiver ponctuellement l'IA depuis le toggle ci-dessous — les PDFs conservent leurs pages via le fallback statique riche."
                  : "Attention : la moitié du budget est déjà consommée. Reste vigilant sur les prochains jours."}
              </div>
            )}

            {llmUsage.history?.length > 0 && (
              <div style={{ marginTop: 12, display: 'flex', gap: 10, alignItems: 'flex-end', height: 42 }}>
                {llmUsage.history.map(h => {
                  const hPct = budget > 0 ? Math.min(100, (h.total_cost_eur / budget) * 100) : 0;
                  return (
                    <div key={h.month} style={{ flex: 1, textAlign: 'center' }} title={`${h.total_calls} appels · ${h.total_cost_eur.toFixed(2)}€`}>
                      <div style={{ height: 24, display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
                        <div style={{
                          width: '60%', height: `${Math.max(4, hPct * 0.24)}px`,
                          background: 'rgba(232,199,102,0.5)', borderRadius: 3,
                        }} />
                      </div>
                      <div style={{ fontSize: 9, color: 'rgba(232,230,240,0.5)', marginTop: 3, letterSpacing: '.05em' }}>
                        {h.month.slice(5)} · {h.total_cost_eur.toFixed(1)}€
                      </div>
                    </div>
                  );
                })}
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <div style={{ height: 24, display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
                    <div style={{
                      width: '60%', height: `${Math.max(4, pct * 0.24)}px`,
                      background: color, borderRadius: 3,
                    }} />
                  </div>
                  <div style={{ fontSize: 9, color, marginTop: 3, letterSpacing: '.05em', fontWeight: 600 }}>
                    {llmUsage.current_month.slice(5)} · {spent.toFixed(1)}€
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })()}

      {/* ═══ AI Enrichment Toggle (transversal PDFs) ═══ */}
      <div
        data-testid="admin-lc-ai-enrichment-panel"
        style={{
          marginBottom: 16, padding: 12, borderRadius: 10,
          background: aiEnrichmentEnabled ? 'rgba(74,222,128,0.05)' : 'rgba(248,113,113,0.05)',
          border: `1px solid ${aiEnrichmentEnabled ? 'rgba(74,222,128,0.25)' : 'rgba(248,113,113,0.35)'}`,
          display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap',
        }}
      >
        <div style={{ flex: 1, minWidth: 260 }}>
          <div style={{
            fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase',
            color: aiEnrichmentEnabled ? '#4ADE80' : '#f87171', fontWeight: 600,
          }}>
            {aiEnrichmentEnabled ? '✦ Enrichissement IA actif' : '✦ Enrichissement IA désactivé'}
          </div>
          <div style={{
            fontSize: 12, color: 'rgba(232,230,240,0.75)', marginTop: 4, lineHeight: 1.5,
          }}>
            {aiEnrichmentEnabled
              ? "Les PDFs Karma, Numérologie, Kabbale, Médiumnité et Pack Karmique appellent GPT-5.4 pour rédiger les pages narratives Soléna."
              : "Fallback statique riche pré-rédigé — pages toujours étoffées, aucun appel LLM (budget préservé)."}
          </div>
        </div>
        <button
          type="button"
          onClick={toggleAiEnrichment}
          disabled={aiToggleBusy}
          data-testid="admin-lc-ai-enrichment-toggle"
          style={{
            fontSize: 11, padding: '8px 14px', borderRadius: 20,
            background: aiEnrichmentEnabled ? 'rgba(248,113,113,0.12)' : 'rgba(74,222,128,0.15)',
            color: aiEnrichmentEnabled ? '#f87171' : '#4ADE80',
            border: `1px solid ${aiEnrichmentEnabled ? 'rgba(248,113,113,0.4)' : 'rgba(74,222,128,0.4)'}`,
            cursor: aiToggleBusy ? 'wait' : 'pointer',
            textTransform: 'uppercase', letterSpacing: '.1em', fontWeight: 600,
            transition: 'all 0.2s ease',
          }}
        >
          {aiToggleBusy
            ? '…'
            : aiEnrichmentEnabled
              ? 'Désactiver l\'IA'
              : 'Réactiver l\'IA'}
        </button>
      </div>

      {/* ═══ Hero A/B Panel ═══ */}
      <div
        data-testid="admin-lc-hero-ab-panel"
        style={{
          marginBottom: 16, padding: 14, borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(74,222,128,0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
          <span style={{ color: '#4ADE80', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', fontWeight: 600 }}>
            ⚡ Hero A/B Landing
          </span>
          {heroAbStats?.forced_variant && (
            <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 10,
              background: 'rgba(74,222,128,0.12)', color: '#4ADE80', fontWeight: 600 }}>
              LOCK → {heroAbStats.forced_variant}
            </span>
          )}
          {heroAbStats?.winner && !heroAbStats?.forced_variant && (
            <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 10,
              background: 'rgba(217,178,106,0.12)', color: '#d9b26a', fontWeight: 600 }}>
              Gagnant détecté : {heroAbStats.winner}
            </span>
          )}
          <button
            onClick={loadHeroAbStats}
            disabled={heroAbBusy}
            data-testid="admin-lc-hero-ab-refresh"
            style={{
              marginLeft: 'auto', padding: '4px 10px', fontSize: 10,
              background: 'transparent', color: '#A78BFA',
              border: '1px solid rgba(167,139,250,0.35)', borderRadius: 10, cursor: 'pointer',
            }}
          >
            {heroAbBusy ? '…' : '↻ refresh'}
          </button>
        </div>
        {heroAbStats && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              {['A', 'B'].map((v) => {
                const row = heroAbStats.variants?.[v] || {};
                const isWinner = heroAbStats.winner === v;
                const isForced = heroAbStats.forced_variant === v;
                return (
                  <div
                    key={v}
                    data-testid={`admin-lc-hero-ab-variant-${v}`}
                    style={{
                      padding: 12, borderRadius: 8,
                      background: isWinner ? 'rgba(74,222,128,0.06)' : 'rgba(11,16,32,0.4)',
                      border: `1px solid ${isForced ? 'rgba(74,222,128,0.4)' : (isWinner ? 'rgba(217,178,106,0.25)' : 'rgba(255,255,255,0.05)')}`,
                    }}
                  >
                    <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginBottom: 6 }}>
                      <span style={{ fontSize: 14, fontWeight: 600, color: '#e8e6f0' }}>Variante {v}</span>
                      {isWinner && <span style={{ fontSize: 10, color: '#d9b26a' }}>🏆</span>}
                      {isForced && <span style={{ fontSize: 10, color: '#4ADE80' }}>🔒</span>}
                    </div>
                    <div style={{ fontSize: 11, color: '#b8b4c9', fontStyle: 'italic', marginBottom: 8, lineHeight: 1.4 }}>
                      « {heroAbStats.headlines?.[v] || '—'} »
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6, fontSize: 11 }}>
                      <div><div style={{ color: '#8a86a0', fontSize: 9, textTransform: 'uppercase' }}>Imp.</div><div style={{ color: '#e8e6f0' }}>{row.impression || 0}</div></div>
                      <div><div style={{ color: '#8a86a0', fontSize: 9, textTransform: 'uppercase' }}>Clicks</div><div style={{ color: '#e8e6f0' }}>{row.total_clicks || 0}</div></div>
                      <div><div style={{ color: '#8a86a0', fontSize: 9, textTransform: 'uppercase' }}>CTR</div><div style={{ color: isWinner ? '#d9b26a' : '#e8e6f0', fontWeight: 600 }}>{row.ctr_pct || 0}%</div></div>
                    </div>
                  </div>
                );
              })}
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
              {heroAbStats.forced_variant ? (
                <button
                  type="button"
                  onClick={() => setHeroForcedVariant(null)}
                  data-testid="admin-lc-hero-ab-unlock"
                  style={{
                    fontSize: 10, padding: '5px 12px', borderRadius: 12,
                    background: 'transparent', color: '#f87171',
                    border: '1px solid rgba(248,113,113,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.1em',
                  }}
                >
                  Déverrouiller (retour A/B 50/50)
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setHeroForcedVariant('A')}
                    data-testid="admin-lc-hero-ab-lock-a"
                    style={{
                      fontSize: 10, padding: '5px 12px', borderRadius: 12,
                      background: 'transparent', color: '#A78BFA',
                      border: '1px solid rgba(167,139,250,0.35)', cursor: 'pointer',
                      textTransform: 'uppercase', letterSpacing: '.1em',
                    }}
                  >
                    🔒 Lock A (100%)
                  </button>
                  <button
                    type="button"
                    onClick={() => setHeroForcedVariant('B')}
                    data-testid="admin-lc-hero-ab-lock-b"
                    style={{
                      fontSize: 10, padding: '5px 12px', borderRadius: 12,
                      background: 'transparent', color: '#d9b26a',
                      border: '1px solid rgba(217,178,106,0.35)', cursor: 'pointer',
                      textTransform: 'uppercase', letterSpacing: '.1em',
                    }}
                  >
                    🔒 Lock B (100%)
                  </button>
                  {heroAbStats.winner && (
                    <button
                      type="button"
                      onClick={() => setHeroForcedVariant(heroAbStats.winner)}
                      data-testid="admin-lc-hero-ab-lock-winner"
                      style={{
                        fontSize: 10, padding: '5px 12px', borderRadius: 12,
                        background: 'linear-gradient(135deg,#c9a24b,#e2c07c)',
                        color: '#1a1030', border: 'none', cursor: 'pointer', fontWeight: 600,
                        textTransform: 'uppercase', letterSpacing: '.1em',
                      }}
                    >
                      🏆 Locker le gagnant ({heroAbStats.winner})
                    </button>
                  )}
                </>
              )}
            </div>
          </>
        )}
      </div>

      {/* ═══ Testimonials Validator ═══ */}
      <div
        data-testid="admin-lc-testimonials-panel"
        style={{
          marginBottom: 16, padding: 14, borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(217,178,106,0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
          <span style={{ color: '#d9b26a', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', fontWeight: 600 }}>
            ✍️ Témoignages soumis
          </span>
          {testimonialsAdmin && (
            <span style={{ color: '#b8b4c9', fontSize: 10 }}>
              · {testimonialsAdmin.filter(t => t.status === 'pending').length} en attente ·
              {' '}{testimonialsAdmin.filter(t => t.status === 'approved').length} approuvés
            </span>
          )}
          <button
            onClick={loadTestimonialsAdmin}
            disabled={testimonialsBusy}
            data-testid="admin-lc-testimonials-refresh"
            style={{
              marginLeft: 'auto', padding: '4px 10px', fontSize: 10,
              background: 'transparent', color: '#A78BFA',
              border: '1px solid rgba(167,139,250,0.35)', borderRadius: 10, cursor: 'pointer',
            }}
          >
            {testimonialsBusy ? '…' : '↻ refresh'}
          </button>
        </div>
        {testimonialsAdmin && testimonialsAdmin.length === 0 && (
          <div style={{ fontSize: 12, color: 'rgba(184,180,201,0.55)', fontStyle: 'italic' }}>
            Aucun témoignage pour l'instant.
          </div>
        )}
        {testimonialsAdmin && testimonialsAdmin.map((t) => (
          <div
            key={t.id}
            data-testid={`admin-lc-testimonial-${t.id}`}
            style={{
              marginBottom: 8, padding: 10, borderRadius: 8,
              background: 'rgba(11,16,32,0.4)',
              borderLeft: `3px solid ${t.status === 'approved' ? '#4ADE80' : '#f59e0b'}`,
            }}
          >
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
              <span style={{ padding: '1px 6px', borderRadius: 8, fontSize: 9,
                background: t.status === 'approved' ? 'rgba(74,222,128,0.12)' : 'rgba(245,158,11,0.15)',
                color: t.status === 'approved' ? '#4ADE80' : '#f59e0b',
                letterSpacing: '.1em', textTransform: 'uppercase', fontWeight: 600,
              }}>
                {t.status}
              </span>
              <strong style={{ color: '#e8e6f0', fontSize: 12 }}>{t.name}</strong>
              {t.sign && <span style={{ color: '#8a86a0', fontSize: 10 }}>{t.sign}</span>}
              {t.city && <span style={{ color: '#8a86a0', fontSize: 10 }}>· {t.city}</span>}
              <span style={{ marginLeft: 'auto', fontSize: 10, color: 'rgba(184,180,201,0.4)' }}>
                {t.created_at ? new Date(t.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) : ''}
              </span>
            </div>
            <div style={{ fontSize: 11, color: '#e8e6f0', lineHeight: 1.5, fontStyle: 'italic',
              paddingLeft: 10, borderLeft: '2px solid rgba(217,178,106,0.3)' }}>
              « {t.quote} »
            </div>
            {(t.transform_before || t.transform_after) && (
              <div style={{ marginTop: 6, fontSize: 10, color: '#b8b4c9' }}>
                {t.transform_before && <span><strong>Avant :</strong> {t.transform_before}</span>}
                {t.transform_before && t.transform_after && <span> · </span>}
                {t.transform_after && <span><strong>Après :</strong> {t.transform_after}</span>}
              </div>
            )}
            <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
              {t.status !== 'approved' && (
                <button
                  type="button"
                  onClick={() => approveTestimonial(t.id)}
                  data-testid={`admin-lc-testimonial-approve-${t.id}`}
                  style={{
                    fontSize: 10, padding: '4px 10px', borderRadius: 10,
                    background: 'rgba(74,222,128,0.15)', color: '#4ADE80',
                    border: '1px solid rgba(74,222,128,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.08em',
                  }}
                >
                  ✓ Approuver
                </button>
              )}
              <button
                type="button"
                onClick={() => deleteTestimonial(t.id)}
                data-testid={`admin-lc-testimonial-delete-${t.id}`}
                style={{
                  fontSize: 10, padding: '4px 10px', borderRadius: 10,
                  background: 'transparent', color: '#f87171',
                  border: '1px solid rgba(248,113,113,0.3)', cursor: 'pointer',
                  textTransform: 'uppercase', letterSpacing: '.08em',
                }}
              >
                × Supprimer
              </button>
              {t.author_email && (
                <span style={{ fontSize: 9, color: '#7d7a90', marginLeft: 'auto', alignSelf: 'center' }}>
                  {t.author_email}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* ═══ Chat Escalations Reply Widget ═══ */}
      <div
        data-testid="admin-lc-chat-escalations-panel"
        style={{
          marginBottom: 16, padding: 14, borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(248,113,113,0.18)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          <span style={{ color: '#f87171', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', fontWeight: 600 }}>
            🚨 Escalades chat IA
          </span>
          {chatEscalations && (
            <span style={{ color: '#b8b4c9', fontSize: 10 }}>
              · {chatEscalations.filter(e => !e.resolved).length} à traiter
              {' · '}{chatEscalations.filter(e => e.resolved).length} résolues
            </span>
          )}
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#b8b4c9', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showResolved}
              onChange={(e) => setShowResolved(e.target.checked)}
              data-testid="admin-lc-escalations-show-resolved"
              style={{ cursor: 'pointer' }}
            />
            Afficher résolues
          </label>
          <button
            onClick={loadChatEscalations}
            disabled={chatEscalationsBusy}
            data-testid="admin-lc-chat-escalations-refresh"
            style={{
              marginLeft: 'auto', padding: '4px 10px', fontSize: 10,
              background: 'transparent', color: '#A78BFA',
              border: '1px solid rgba(167,139,250,0.35)', borderRadius: 10, cursor: 'pointer',
            }}
          >
            {chatEscalationsBusy ? '…' : '↻ refresh'}
          </button>
        </div>
        {chatEscalations && chatEscalations.length === 0 && (
          <div style={{ fontSize: 12, color: 'rgba(184,180,201,0.55)', fontStyle: 'italic' }}>
            Aucune escalade en attente. Tout va bien 🌙
          </div>
        )}
        {chatEscalations && chatEscalations
          .filter((esc) => showResolved ? true : !esc.resolved)
          .map((esc) => (
          <div
            key={esc.session_id}
            data-testid={`admin-lc-escalation-${esc.session_id}`}
            style={{
              marginBottom: 10, padding: 10, borderRadius: 8,
              background: esc.resolved ? 'rgba(74,222,128,0.03)' : 'rgba(11,16,32,0.4)',
              opacity: esc.resolved ? 0.7 : 1,
              borderLeft: `3px solid ${esc.resolved ? '#4ADE80' : (esc.admin_replies_count > 0 ? '#d9b26a' : '#f87171')}`,
            }}
          >
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6, flexWrap: 'wrap' }}>
              {esc.resolved ? (
                <span style={{ padding: '1px 6px', borderRadius: 8, fontSize: 9,
                  background: 'rgba(74,222,128,0.15)', color: '#4ADE80',
                  letterSpacing: '.1em', textTransform: 'uppercase', fontWeight: 600 }}>
                  ✓ Résolu
                </span>
              ) : (
                <span style={{ padding: '1px 6px', borderRadius: 8, fontSize: 9,
                  background: esc.admin_replies_count > 0 ? 'rgba(217,178,106,0.15)' : 'rgba(248,113,113,0.15)',
                  color: esc.admin_replies_count > 0 ? '#d9b26a' : '#f87171',
                  letterSpacing: '.1em', textTransform: 'uppercase', fontWeight: 600 }}>
                  {esc.admin_replies_count > 0 ? `${esc.admin_replies_count} réponse${esc.admin_replies_count > 1 ? 's' : ''}` : 'À traiter'}
                </span>
              )}
              <code style={{ fontSize: 9, color: '#8a86a0' }}>{esc.session_id}</code>
              <span style={{ marginLeft: 'auto', fontSize: 9, color: 'rgba(184,180,201,0.4)' }}>
                {esc.created_at ? new Date(esc.created_at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
            </div>
            <div style={{ marginBottom: 6, fontSize: 11 }}>
              <div style={{ color: '#8a86a0', fontSize: 9, textTransform: 'uppercase', letterSpacing: '.08em', marginBottom: 2 }}>Message utilisatrice</div>
              <div style={{ color: '#e8e6f0', fontStyle: 'italic', paddingLeft: 8, borderLeft: '2px solid rgba(248,113,113,0.4)' }}>
                « {esc.last_user_message} »
              </div>
            </div>
            <div style={{ marginBottom: 8, fontSize: 10, color: 'rgba(184,180,201,0.65)' }}>
              <strong style={{ color: '#8a86a0' }}>Réponse IA :</strong> {esc.last_ai_reply}
            </div>
            {esc.last_admin_reply_at && (
              <div style={{ marginBottom: 6, fontSize: 10, color: '#4ADE80' }}>
                ✓ Dernière réponse humaine envoyée le {new Date(esc.last_admin_reply_at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
              </div>
            )}
            {esc.resolved && (
              <div style={{ marginBottom: 6, fontSize: 10, color: '#4ADE80' }}>
                Résolu par {esc.resolved_by} le {esc.resolved_at ? new Date(esc.resolved_at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
              </div>
            )}
            {!esc.resolved && (
              <>
                <div style={{ display: 'flex', gap: 6, alignItems: 'flex-end', marginTop: 8 }}>
                  <textarea
                    value={replyDrafts[esc.session_id] || ''}
                    onChange={(e) => setReplyDrafts((d) => ({ ...d, [esc.session_id]: e.target.value }))}
                    placeholder="Ta réponse à l'utilisatrice… (apparait dans son chat en direct)"
                    rows={2}
                    data-testid={`admin-lc-escalation-reply-input-${esc.session_id}`}
                    style={{
                      flex: 1,
                      background: 'rgba(11,16,32,0.6)', color: '#e8e6f0',
                      border: '1px solid rgba(201,162,75,0.25)', borderRadius: 8,
                      padding: '6px 10px', fontSize: 11, fontFamily: 'Georgia, serif',
                      resize: 'vertical', minHeight: 40,
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => sendAdminReply(esc.session_id)}
                    data-testid={`admin-lc-escalation-reply-send-${esc.session_id}`}
                    style={{
                      fontSize: 10, padding: '8px 14px', borderRadius: 12,
                      background: 'linear-gradient(135deg,#c9a24b,#e2c07c)', color: '#1a1030',
                      border: 'none', cursor: 'pointer', fontWeight: 600,
                      textTransform: 'uppercase', letterSpacing: '.08em',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    Envoyer
                  </button>
                </div>
                <div style={{ marginTop: 8, textAlign: 'right' }}>
                  <button
                    type="button"
                    onClick={() => resolveEscalation(esc.session_id)}
                    data-testid={`admin-lc-escalation-resolve-${esc.session_id}`}
                    style={{
                      fontSize: 9, padding: '4px 10px', borderRadius: 10,
                      background: 'rgba(74,222,128,0.1)', color: '#4ADE80',
                      border: '1px solid rgba(74,222,128,0.35)', cursor: 'pointer',
                      textTransform: 'uppercase', letterSpacing: '.08em',
                    }}
                  >
                    ✓ Marquer résolu
                  </button>
                </div>
              </>
            )}
            {esc.resolved && (
              <div style={{ marginTop: 8, textAlign: 'right' }}>
                <button
                  type="button"
                  onClick={() => reopenEscalation(esc.session_id)}
                  data-testid={`admin-lc-escalation-reopen-${esc.session_id}`}
                  style={{
                    fontSize: 9, padding: '4px 10px', borderRadius: 10,
                    background: 'transparent', color: '#A78BFA',
                    border: '1px solid rgba(167,139,250,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.08em',
                  }}
                >
                  ↺ Rouvrir
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Filtres export CSV */}
      <div
        data-testid="admin-lc-export-filters"
        style={{
          display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16, padding: 10,
          background: 'rgba(167,139,250,0.03)',
          border: '1px dashed rgba(167,139,250,0.25)', borderRadius: 8,
          fontSize: 11,
        }}
      >
        <span style={{ color: 'rgba(184,180,201,0.75)', alignSelf: 'center' }}>Filtres Export :</span>
        <input
          type="date"
          value={exportFilters.since}
          onChange={(e) => setExportFilters(s => ({ ...s, since: e.target.value }))}
          data-testid="admin-lc-filter-since"
          style={{ background: 'rgba(11,16,32,0.5)', color: '#e8e6f0', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 4, padding: '4px 8px' }}
        />
        <span style={{ alignSelf: 'center', color: 'rgba(184,180,201,0.5)' }}>→</span>
        <input
          type="date"
          value={exportFilters.until}
          onChange={(e) => setExportFilters(s => ({ ...s, until: e.target.value }))}
          data-testid="admin-lc-filter-until"
          style={{ background: 'rgba(11,16,32,0.5)', color: '#e8e6f0', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 4, padding: '4px 8px' }}
        />
        <select
          value={exportFilters.payment_status}
          onChange={(e) => setExportFilters(s => ({ ...s, payment_status: e.target.value }))}
          data-testid="admin-lc-filter-status"
          style={{ background: 'rgba(11,16,32,0.5)', color: '#e8e6f0', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 4, padding: '4px 8px' }}
        >
          <option value="">Tous statuts</option>
          <option value="paid">Payé</option>
          <option value="unpaid">Non payé</option>
          <option value="initiated">Initié</option>
        </select>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: 'rgba(184,180,201,0.85)' }}>
          <input
            type="checkbox"
            checked={exportFilters.include_bypass}
            onChange={(e) => setExportFilters(s => ({ ...s, include_bypass: e.target.checked }))}
            data-testid="admin-lc-filter-bypass"
          />
          Inclure admin bypass
        </label>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: 'rgba(184,180,201,0.85)' }}>
          <input
            type="checkbox"
            checked={exportFilters.refunded_only}
            onChange={(e) => setExportFilters(s => ({ ...s, refunded_only: e.target.checked }))}
            data-testid="admin-lc-filter-refunded-only"
          />
          Remboursés uniquement
        </label>
      </div>

      {error && (
        <div style={{ padding: 12, background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', borderRadius: 8, color: '#f87171', marginBottom: 16, fontSize: 13 }}>
          {error}
        </div>
      )}

      {stats && (
        <div
          data-testid="admin-lc-stats"
          style={{
            display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16,
            padding: 12, background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(217,178,106,0.15)', borderRadius: 10,
          }}
        >
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Payés (hors bypass) : <strong style={{ color: '#e8e6f0' }}>{stats.total_paid}</strong>
          </span>
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Remboursés : <strong style={{ color: '#f87171' }}>{stats.total_refunded}</strong>
          </span>
          <span style={{ fontSize: 12, color: 'rgba(184,180,201,0.75)' }}>
            Taux de refund : <strong data-testid="admin-lc-stats-refund-rate" style={{ color: stats.refund_rate_pct > 5 ? '#f87171' : '#4ADE80' }}>{stats.refund_rate_pct}%</strong>
          </span>
        </div>
      )}

      {abStats && (
        <div
          data-testid="admin-lc-ab-panel"
          style={{
            marginBottom: 16, padding: 12,
            background: 'linear-gradient(135deg, rgba(167,139,250,0.08), rgba(217,178,106,0.05))',
            border: '1px solid rgba(167,139,250,0.25)', borderRadius: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', color: '#A78BFA' }}>
              A/B Test J+30 Upsell
            </span>
            <span style={{ fontSize: 11, color: 'rgba(184,180,201,0.65)' }}>
              · {abStats.total} envois {abStats.total >= 50 ? '· prêt à décider' : `· ${50 - abStats.total} à attendre`}
            </span>
            <button
              onClick={loadCTR}
              disabled={ctrLoading || abStats.total === 0}
              data-testid="admin-lc-ab-load-ctr"
              style={{
                marginLeft: 'auto', fontSize: 10, padding: '4px 10px',
                borderRadius: 12, background: 'rgba(167,139,250,0.15)',
                color: '#A78BFA', border: '1px solid rgba(167,139,250,0.3)',
                cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '.1em',
              }}
            >
              {ctrLoading ? 'Chargement…' : (abStats.ctr ? 'Rafraîchir CTR' : 'Charger CTR Resend')}
            </button>
          </div>
          {/* Bascule variante gagnante */}
          <div
            data-testid="admin-lc-ab-force-panel"
            style={{
              display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap',
              marginBottom: 10, padding: 8, borderRadius: 6,
              background: 'rgba(11,16,32,0.4)',
              border: forcedVariant ? '1px solid rgba(74,222,128,0.35)' : '1px dashed rgba(255,255,255,0.08)',
            }}
          >
            <span style={{ fontSize: 10, color: 'rgba(184,180,201,0.7)', letterSpacing: '.1em', textTransform: 'uppercase' }}>
              Auto-bascule variante :
            </span>
            {forcedVariant ? (
              <>
                <span
                  data-testid="admin-lc-ab-force-active"
                  style={{
                    fontSize: 11, color: '#4ADE80', fontWeight: 600,
                    padding: '2px 8px', borderRadius: 10,
                    background: 'rgba(74,222,128,0.12)',
                  }}
                >
                  100% → {forcedVariant === 'question' ? '❓ Question' : '✉️ Invitation'}
                </span>
                <button
                  type="button"
                  onClick={() => setForcedVariantHandler(null)}
                  disabled={settingsBusy}
                  data-testid="admin-lc-ab-force-reset"
                  style={{
                    fontSize: 10, padding: '4px 10px', borderRadius: 12,
                    background: 'transparent', color: '#f87171',
                    border: '1px solid rgba(248,113,113,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.1em',
                  }}
                >
                  Reset A/B 50/50
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setForcedVariantHandler('question')}
                  disabled={settingsBusy}
                  data-testid="admin-lc-ab-force-question"
                  style={{
                    fontSize: 10, padding: '4px 10px', borderRadius: 12,
                    background: 'transparent', color: '#A78BFA',
                    border: '1px solid rgba(167,139,250,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.1em',
                  }}
                >
                  Forcer Question 100%
                </button>
                <button
                  type="button"
                  onClick={() => setForcedVariantHandler('invitation')}
                  disabled={settingsBusy}
                  data-testid="admin-lc-ab-force-invitation"
                  style={{
                    fontSize: 10, padding: '4px 10px', borderRadius: 12,
                    background: 'transparent', color: '#d9b26a',
                    border: '1px solid rgba(217,178,106,0.35)', cursor: 'pointer',
                    textTransform: 'uppercase', letterSpacing: '.1em',
                  }}
                >
                  Forcer Invitation 100%
                </button>
                <span style={{ fontSize: 10, color: 'rgba(184,180,201,0.55)', fontStyle: 'italic' }}>
                  · défaut : hash session_id 50/50
                </span>
              </>
            )}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {['question', 'invitation'].map((v) => {
              const n = abStats[v] || 0;
              const pct = abStats.total ? Math.round((n / abStats.total) * 100) : 0;
              const isLeader = abStats.total >= 20 && n > (abStats[v === 'question' ? 'invitation' : 'question'] || 0);
              return (
                <div
                  key={v}
                  data-testid={`admin-lc-ab-${v}`}
                  style={{
                    padding: 10, borderRadius: 8,
                    background: 'rgba(11,16,32,0.5)',
                    border: `1px solid ${isLeader ? 'rgba(74,222,128,0.4)' : 'rgba(255,255,255,0.06)'}`,
                  }}
                >
                  <div style={{ fontSize: 12, color: '#e8e6f0', marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
                    <span>
                      {v === 'question' ? '❓ Question ouverte' : '✉️ Invitation directe'}
                      {isLeader && <span style={{ color: '#4ADE80', marginLeft: 6, fontSize: 10 }}>· leader</span>}
                    </span>
                    <span style={{ color: '#d9b26a', fontWeight: 600 }}>{n}</span>
                  </div>
                  <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%', width: `${pct}%`,
                        background: v === 'question' ? '#A78BFA' : '#d9b26a',
                        transition: 'width .3s ease',
                      }}
                    />
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(184,180,201,0.55)', marginTop: 4 }}>
                    {pct}% du volume
                  </div>
                </div>
              );
            })}
          </div>
          {abStats.total < 50 && (
            <div style={{ fontSize: 10, color: 'rgba(184,180,201,0.5)', marginTop: 8, fontStyle: 'italic' }}>
              Décision statistiquement fiable à partir de 50 envois. Vérifier le CTR dans Resend via les email_ids stockés.
            </div>
          )}
          {abStats.ctr && (
            <div
              data-testid="admin-lc-ab-ctr"
              style={{ marginTop: 12, padding: 10, background: 'rgba(11,16,32,0.4)', borderRadius: 8 }}
            >
              <div style={{ fontSize: 11, color: '#d9b26a', marginBottom: 6, letterSpacing: '.1em', textTransform: 'uppercase' }}>
                CTR réel via Resend
                {abStats.ctr.winner && (
                  <span style={{ color: '#4ADE80', marginLeft: 8, textTransform: 'none' }}>
                    🏆 Gagnant : {abStats.ctr.winner === 'question' ? 'Question ouverte' : 'Invitation directe'}
                  </span>
                )}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {['question', 'invitation'].map((v) => {
                  const s = abStats.ctr[v] || {};
                  return (
                    <div key={v} style={{ fontSize: 11, color: 'rgba(184,180,201,0.85)' }}>
                      <div style={{ marginBottom: 2, color: '#e8e6f0' }}>
                        {v === 'question' ? '❓ Question' : '✉️ Invitation'}
                      </div>
                      <div>Envoyés : <strong>{s.sent || 0}</strong></div>
                      <div>Ouverts : <strong>{s.opened || 0}</strong> ({s.open_rate || 0}%)</div>
                      <div>Cliqués : <strong style={{ color: '#4ADE80' }}>{s.clicked || 0}</strong> (CTR {s.ctr || 0}%)</div>
                      {s.sample_note && (
                        <div style={{ fontSize: 9, color: 'rgba(184,180,201,0.5)', marginTop: 2 }}>{s.sample_note}</div>
                      )}
                    </div>
                  );
                })}
              </div>
              {!abStats.ctr.winner && abStats.total >= 30 && (
                <div style={{ fontSize: 10, color: 'rgba(184,180,201,0.55)', marginTop: 6, fontStyle: 'italic' }}>
                  Écart CTR &lt; 0.5% ou volumes insuffisants — pas encore de gagnant fiable.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {orders.length === 0 && !loading && (
        <p style={{ color: 'rgba(184,180,201,0.7)', fontSize: 14 }}>Aucune commande 97€ pour l&apos;instant.</p>
      )}

      {/* Historique des alertes envoyées */}
      <div
        data-testid="admin-lc-alerts-history-panel"
        style={{
          marginBottom: 16, padding: 10, borderRadius: 10,
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(167,139,250,0.15)',
        }}
      >
        <button
          type="button"
          onClick={() => setShowAlertsHistory(v => !v)}
          data-testid="admin-lc-alerts-history-toggle"
          style={{
            background: 'transparent', border: 'none', cursor: 'pointer', padding: 0,
            display: 'flex', alignItems: 'center', gap: 6, width: '100%',
            color: '#A78BFA', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase',
          }}
        >
          {showAlertsHistory ? '▼' : '▶'} Historique alertes envoyées
          <span style={{ color: 'rgba(184,180,201,0.55)', fontSize: 10, textTransform: 'none', letterSpacing: 0 }}>
            · {alertsHistory.length} entrée{alertsHistory.length > 1 ? 's' : ''} (30 max)
          </span>
        </button>
        {showAlertsHistory && (
          <div data-testid="admin-lc-alerts-history-list" style={{ marginTop: 10 }}>
            {alertsHistory.length === 0 ? (
              <div style={{ fontSize: 12, color: 'rgba(184,180,201,0.55)', fontStyle: 'italic' }}>
                Aucune alerte Slack ou email envoyée pour le moment.
              </div>
            ) : (
              alertsHistory.slice().reverse().map((a, i) => (
                <div
                  key={i}
                  data-testid={`admin-lc-alerts-history-item-${i}`}
                  style={{
                    marginBottom: 8, padding: 8, borderRadius: 6,
                    background: 'rgba(11,16,32,0.4)',
                    borderLeft: `3px solid ${a.kind === 'refund_alert' ? '#f87171' : a.kind === 'slack_test' ? '#4ADE80' : '#A78BFA'}`,
                  }}
                >
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 11, color: '#e8e6f0' }}>
                    <span style={{
                      padding: '1px 6px', borderRadius: 8,
                      background: 'rgba(167,139,250,0.15)', color: '#A78BFA',
                      fontSize: 9, letterSpacing: '.1em', textTransform: 'uppercase',
                    }}>
                      {a.kind}
                    </span>
                    <strong>{a.title}</strong>
                    <span style={{ marginLeft: 'auto', fontSize: 10, color: 'rgba(184,180,201,0.55)' }}>
                      {a.at ? new Date(a.at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                  {a.details && (
                    <div style={{ marginTop: 4, fontSize: 10, color: 'rgba(184,180,201,0.65)' }}>
                      {a.details}
                    </div>
                  )}
                  {a.channels && a.channels.length > 0 && (
                    <div style={{ marginTop: 4, fontSize: 9, color: 'rgba(184,180,201,0.5)' }}>
                      Canaux : {a.channels.join(' · ')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {orders.map((o) => (
          <div
            key={o.session_id}
            data-testid={`admin-lc-order-${o.session_id}`}
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(217,178,106,0.15)',
              borderRadius: 12, padding: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: 260 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                  <strong style={{ color: '#e8e6f0', fontSize: 15 }}>{o.email || '(sans email)'}</strong>
                  {o.admin_bypass && (
                    <span style={{ padding: '2px 8px', borderRadius: 10, background: 'rgba(167,139,250,0.15)', color: '#a78bfa', fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase' }}>Admin</span>
                  )}
                  <span style={{ padding: '2px 8px', borderRadius: 10, background: o.payment_status === 'paid' ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)', color: o.payment_status === 'paid' ? '#4ADE80' : '#f87171', fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase' }}>
                    {o.payment_status}
                  </span>
                  {!o.bundle_dispatched && o.payment_status === 'paid' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#fbbf24', fontSize: 11 }}>
                      <AlertTriangle className="w-3 h-3" /> non dispatché
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 11, color: 'rgba(184,180,201,0.65)', fontFamily: 'monospace' }}>
                  {o.session_id} · {o.created_at ? new Date(o.created_at).toLocaleString('fr-FR') : ''}
                </div>
                {o.bundle_error && (
                  <div style={{ marginTop: 4, fontSize: 11, color: '#f87171' }}>Erreur bundle : {o.bundle_error}</div>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'rgba(184,180,201,0.75)' }}>
                  <Mail className="w-3 h-3" />
                  J+1 <span style={{ color: o.sequence?.j1 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+7 <span style={{ color: o.sequence?.j7 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+13 <span style={{ color: o.sequence?.j13 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                  {' '}J+30 <span style={{ color: o.sequence?.j30 ? '#4ADE80' : 'rgba(184,180,201,0.4)' }}>●</span>
                </div>
                <button
                  onClick={() => redispatch(o.session_id)}
                  disabled={redispatching === o.session_id || !!o.refunded_at}
                  data-testid={`admin-lc-redispatch-${o.session_id}`}
                  style={{
                    padding: '6px 12px', borderRadius: 16,
                    background: 'transparent',
                    color: o.refunded_at ? 'rgba(184,180,201,0.4)' : '#d9b26a',
                    border: `1px solid ${o.refunded_at ? 'rgba(184,180,201,0.2)' : 'rgba(217,178,106,0.5)'}`,
                    fontSize: 11, cursor: o.refunded_at ? 'not-allowed' : 'pointer',
                  }}
                >
                  {redispatching === o.session_id ? '...' : 'Relancer'}
                </button>
                {!o.refunded_at ? (
                  <button
                    onClick={() => openRefundModal(o)}
                    disabled={refunding === o.session_id}
                    data-testid={`admin-lc-refund-${o.session_id}`}
                    style={{
                      padding: '6px 12px', borderRadius: 16,
                      background: 'transparent',
                      color: '#f87171',
                      border: '1px solid rgba(248,113,113,0.4)',
                      fontSize: 11, cursor: 'pointer',
                    }}
                  >
                    {refunding === o.session_id ? '...' : 'Rembourser'}
                  </button>
                ) : (
                  <span
                    data-testid={`admin-lc-refunded-${o.session_id}`}
                    style={{
                      padding: '4px 10px', borderRadius: 14,
                      background: 'rgba(248,113,113,0.15)',
                      color: '#f87171',
                      fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase',
                    }}
                    title={o.refund_reason || 'Remboursé'}
                  >
                    Remboursé
                  </span>
                )}
              </div>
            </div>

            <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 8 }}>
              {o.children.length === 0 && (
                <div style={{ fontSize: 12, color: 'rgba(184,180,201,0.5)' }}>Aucun PDF enfant créé.</div>
              )}
              {o.children.map((c) => (
                <div
                  key={c.session_id}
                  style={{
                    padding: 10, borderRadius: 8,
                    background: 'rgba(11,16,32,0.5)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                >
                  <div style={{ fontSize: 12, color: '#e8e6f0', marginBottom: 4 }}>
                    {KIND_LABEL[c.kind] || c.kind}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11 }}>
                    <StatusPill status={c.pdf_status} ready={c.pdf_ready} error={c.pdf_error} />
                    {c.email_sent && <Mail className="w-3 h-3" style={{ color: '#4ADE80' }} />}
                  </div>
                </div>
              ))}
            </div>

            {/* Timeline actions admin */}
            {(o.admin_actions && o.admin_actions.length > 0) && (
              <div style={{ marginTop: 12 }}>
                <button
                  type="button"
                  onClick={() => setExpandedTimeline(expandedTimeline === o.session_id ? null : o.session_id)}
                  data-testid={`admin-lc-timeline-toggle-${o.session_id}`}
                  style={{
                    fontSize: 11, background: 'transparent', border: 'none',
                    color: '#A78BFA', cursor: 'pointer', padding: 0,
                    letterSpacing: '.08em', textTransform: 'uppercase',
                  }}
                >
                  {expandedTimeline === o.session_id ? '▼' : '▶'} Timeline actions ({o.admin_actions.length})
                </button>
                {expandedTimeline === o.session_id && (
                  <div
                    data-testid={`admin-lc-timeline-${o.session_id}`}
                    style={{
                      marginTop: 8, paddingLeft: 12,
                      borderLeft: '2px solid rgba(167,139,250,0.3)',
                    }}
                  >
                    {o.admin_actions.slice().reverse().map((a, i) => (
                      <div key={i} style={{ marginBottom: 6, fontSize: 11, color: 'rgba(184,180,201,0.85)' }}>
                        <span style={{
                          color: a.action.includes('refund') ? '#f87171' :
                                 a.action === 'redispatch' ? '#d9b26a' : '#A78BFA',
                          fontWeight: 600, marginRight: 6,
                        }}>{a.action}</span>
                        <span style={{ color: 'rgba(184,180,201,0.6)' }}>
                          {new Date(a.at).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span style={{ color: 'rgba(184,180,201,0.6)', marginLeft: 6 }}>
                          par <em>{a.admin_email || (a.auto ? 'auto' : 'admin')}</em>
                        </span>
                        {a.details && (
                          <div style={{ marginTop: 2, fontSize: 10, color: 'rgba(184,180,201,0.55)', paddingLeft: 8 }}>
                            {a.details}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ═══ MODAL REFUND ═══ */}
      <Dialog open={refundModalOpen} onOpenChange={setRefundModalOpen}>
        <DialogContent
          className="max-w-md"
          data-testid="refund-modal"
          style={{ background: '#141a33', color: '#e8e6f0', border: '1px solid rgba(217,178,106,0.3)' }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: '#f87171' }}>
              Rembourser la commande
            </DialogTitle>
            <DialogDescription>
              {refundTarget && (
                <>
                  <div className="text-xs opacity-70 font-mono break-all mb-2">
                    {refundTarget.sid}
                  </div>
                  <div className="text-sm">
                    <strong>{refundTarget.email}</strong>
                    {' — '}{refundTarget.amount}€
                    {refundTarget.admin_bypass && <span className="ml-2 text-purple-300">(admin bypass)</span>}
                  </div>
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          {refundSuccess ? (
            <div
              data-testid="refund-modal-success"
              className="rounded-lg p-3 text-sm"
              style={{ background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)', color: '#4ADE80' }}
            >
              ✓ Remboursement effectué{refundSuccess.stripe_refund_id ? ` · Stripe : ${refundSuccess.stripe_refund_id}` : ''}
              {refundSuccess.stripe_skipped && <div className="text-xs opacity-70 mt-1">Stripe non appelé (admin bypass ou skip demandé).</div>}
            </div>
          ) : (
            <>
              <div className="space-y-3">
                <div>
                  <label className="text-xs uppercase tracking-wider block mb-1" style={{ color: '#d9b26a' }}>
                    Raison type
                  </label>
                  <select
                    data-testid="refund-modal-reason-preset"
                    onChange={(e) => {
                      const v = e.target.value;
                      if (!v) return;
                      const map = {
                        pdf_defect: 'PDF défectueux ou incomplet',
                        duplicate: 'Commande en doublon',
                        unsatisfied: 'Client insatisfait du contenu',
                        chargeback: 'Chargeback / litige carte',
                        wrong_purchase: 'Achat par erreur (mauvais produit)',
                        no_delivery: 'Livraison non reçue (bug orchestration)',
                      };
                      setRefundReason(prev => (prev ? prev + ' · ' : '') + (map[v] || v));
                      e.target.value = '';
                    }}
                    className="w-full rounded px-3 py-2 text-sm mb-2"
                    style={{
                      background: 'rgba(11,16,32,0.6)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      color: '#e8e6f0',
                    }}
                    defaultValue=""
                  >
                    <option value="">— Sélectionner une raison type (optionnel) —</option>
                    <option value="pdf_defect">PDF défectueux ou incomplet</option>
                    <option value="duplicate">Commande en doublon</option>
                    <option value="unsatisfied">Client insatisfait du contenu</option>
                    <option value="chargeback">Chargeback / litige carte</option>
                    <option value="wrong_purchase">Achat par erreur</option>
                    <option value="no_delivery">Livraison non reçue</option>
                  </select>
                  <label className="text-xs uppercase tracking-wider block mb-1" style={{ color: '#d9b26a' }}>
                    Raison (optionnel)
                  </label>
                  <textarea
                    data-testid="refund-modal-reason"
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                    placeholder="Ex : client a demandé, PDF défectueux, doublon…"
                    rows={3}
                    className="w-full rounded px-3 py-2 text-sm"
                    style={{
                      background: 'rgba(11,16,32,0.6)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      color: '#e8e6f0',
                    }}
                  />
                </div>

                {suggestedPartial && !refundPartial && (
                  <div
                    data-testid="refund-modal-suggestion"
                    className="rounded-lg p-3 flex items-start justify-between gap-2"
                    style={{
                      background: 'rgba(217,178,106,0.08)',
                      border: '1px solid rgba(217,178,106,0.3)',
                    }}
                  >
                    <div className="text-xs" style={{ color: '#d9b26a', flex: 1 }}>
                      <div style={{ fontWeight: 600, marginBottom: 4 }}>💡 Suggestion</div>
                      <div style={{ color: 'rgba(232,230,240,0.85)' }}>{suggestedPartial.note}</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setRefundPartial(true);
                        setRefundAmount(String(suggestedPartial.amount));
                      }}
                      data-testid="refund-modal-apply-suggestion"
                      className="text-xs px-2 py-1 rounded"
                      style={{
                        background: '#d9b26a', color: '#1a1030',
                        border: 'none', cursor: 'pointer',
                        fontWeight: 600, whiteSpace: 'nowrap',
                      }}
                    >
                      Appliquer
                    </button>
                  </div>
                )}

                {refundTarget && !refundTarget.admin_bypass && (
                  <>
                    <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: 'rgba(184,180,201,0.85)' }}>
                      <input
                        type="checkbox"
                        checked={refundSkipStripe}
                        onChange={(e) => setRefundSkipStripe(e.target.checked)}
                        data-testid="refund-modal-skip-stripe"
                      />
                      Ne pas appeler Stripe (marquer localement uniquement)
                    </label>
                    <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: 'rgba(184,180,201,0.85)' }}>
                      <input
                        type="checkbox"
                        checked={refundPartial}
                        onChange={(e) => setRefundPartial(e.target.checked)}
                        data-testid="refund-modal-partial-toggle"
                      />
                      Remboursement partiel
                    </label>
                    <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ color: 'rgba(184,180,201,0.85)' }}>
                      <input
                        type="checkbox"
                        checked={suspendNotifications}
                        onChange={(e) => setSuspendNotifications(e.target.checked)}
                        data-testid="refund-modal-suspend-notifications"
                      />
                      Suspendre les notifications futures (journal, séquence) pour ce client
                    </label>
                    {refundPartial && (
                      <div className="pl-6">
                        <label className="text-xs uppercase tracking-wider block mb-1" style={{ color: '#d9b26a' }}>
                          Montant à rembourser (€)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          min="0.01"
                          max={refundTarget.amount}
                          value={refundAmount}
                          onChange={(e) => setRefundAmount(e.target.value)}
                          placeholder={`Max ${refundTarget.amount}€`}
                          data-testid="refund-modal-amount"
                          className="w-full rounded px-3 py-2 text-sm"
                          style={{
                            background: 'rgba(11,16,32,0.6)',
                            border: '1px solid rgba(255,255,255,0.15)',
                            color: '#e8e6f0',
                          }}
                        />
                      </div>
                    )}
                  </>
                )}

                {refundError && (
                  <div
                    data-testid="refund-modal-error"
                    className="rounded p-2 text-xs"
                    style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.3)', color: '#f87171' }}
                  >
                    {refundError}
                  </div>
                )}
              </div>

              <DialogFooter>
                <button
                  type="button"
                  onClick={() => setRefundModalOpen(false)}
                  disabled={!!refunding}
                  data-testid="refund-modal-cancel"
                  className="px-4 py-2 rounded text-xs uppercase tracking-wider"
                  style={{ background: 'transparent', color: 'rgba(184,180,201,0.75)', border: '1px solid rgba(255,255,255,0.15)' }}
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={confirmRefund}
                  disabled={!!refunding}
                  data-testid="refund-modal-confirm"
                  className="px-4 py-2 rounded text-xs uppercase tracking-wider inline-flex items-center gap-1.5"
                  style={{ background: '#f87171', color: '#0b1020', border: 'none', cursor: refunding ? 'not-allowed' : 'pointer', fontWeight: 600 }}
                >
                  {refunding && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {refunding ? 'Refund…' : (refundSkipStripe || refundTarget?.admin_bypass ? 'Marquer remboursé' : 'Rembourser via Stripe')}
                </button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
