import { createClient } from '@supabase/supabase-js';

// Public Supabase URL + anon key — read from env only (no hardcoded fallbacks).
// Env vars are injected at build time by CRA / Emergent deployment.
const url = process.env.REACT_APP_SUPABASE_URL;
const anonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!url || !anonKey) {
  // Fail fast in dev/prod if the deployment forgot to inject these.
   
  console.error('[Supabase] Missing REACT_APP_SUPABASE_URL or REACT_APP_SUPABASE_ANON_KEY');
}

export const supabase = createClient(url, anonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
