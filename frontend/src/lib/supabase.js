import { createClient } from '@supabase/supabase-js';

// Public Supabase URL + anon key (anon key is rate-limited + protected by RLS).
// Fallbacks are kept ON PURPOSE: if Netlify build env vars are missing, the app
// still boots instead of crashing with a blank screen.
const url = process.env.REACT_APP_SUPABASE_URL
  || 'https://ebwicqvbkwogxneipaxh.supabase.co';
const anonKey = process.env.REACT_APP_SUPABASE_ANON_KEY
  || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA';

export const supabase = createClient(url, anonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
