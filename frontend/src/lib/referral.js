/**
 * Capture le paramètre ?ref=CODE présent dans l'URL et le stocke en localStorage
 * pour être joué au premier login/register. Idempotent, ne re-écrit pas si déjà présent
 * (le premier parrain qui amène le visiteur gagne le lead).
 */
export const REFERRAL_LS_KEY = 'plume_ref_code';

export function captureReferralFromURL() {
  try {
    const params = new URLSearchParams(window.location.search);
    const code = (params.get('ref') || '').trim().toUpperCase();
    if (!code) return null;
    if (!/^[A-Z0-9]{4,16}$/.test(code)) return null;
    const existing = localStorage.getItem(REFERRAL_LS_KEY);
    if (!existing) {
      localStorage.setItem(REFERRAL_LS_KEY, code);
    }
    return existing || code;
  } catch {
    return null;
  }
}

export function readReferralCode() {
  try { return localStorage.getItem(REFERRAL_LS_KEY) || null; } catch { return null; }
}

export function clearReferralCode() {
  try { localStorage.removeItem(REFERRAL_LS_KEY); } catch { /* ignore */ }
}
