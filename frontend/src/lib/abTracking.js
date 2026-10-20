// Lightweight first-party A/B tracking — writes to /api/analytics/ab-event
// in addition to the GA4 dataLayer, so we can aggregate conversion stats from
// Supabase in /admin/alerts (no GA4 Data API dependency).

const API_URL = process.env.REACT_APP_BACKEND_URL;

let _sessionId = null;
function _getSessionId() {
  if (_sessionId) return _sessionId;
  try {
    let s = sessionStorage.getItem('plume_ab_sid');
    if (!s) {
      s = `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
      sessionStorage.setItem('plume_ab_sid', s);
    }
    _sessionId = s;
    return s;
  } catch {
    return null;
  }
}

export function trackABEvent(experiment, variant, eventName, metadata = {}) {
  if (!API_URL || !experiment || !variant || !eventName) return;
  const body = {
    experiment,
    variant,
    event_name: eventName,
    session_id: _getSessionId(),
    metadata,
  };
  // Fire-and-forget, non-blocking, keepalive for unload scenarios
  try {
    fetch(`${API_URL}/api/analytics/ab-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      keepalive: true,
    }).catch(() => { /* silent */ });
  } catch { /* silent */ }
}
