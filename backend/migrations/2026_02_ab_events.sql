-- Table : ab_events
-- Objectif : Tracking first-party des expériences A/B pour voir les conversions
-- sans dépendre d'un rapport GA4 custom (plus rapide, plus fiable).
--
-- Rempli par POST /api/analytics/ab-event depuis le frontend (exit-intent modal,
-- lead magnet success, etc.) et agrégé par GET /api/admin/ab-stats.
create table if not exists public.ab_events (
  id             uuid primary key default gen_random_uuid(),
  experiment     text not null,        -- ex: 'synastrie_exit_intent'
  variant        text not null,        -- ex: 'A' | 'B'
  event_name     text not null,        -- 'shown' | 'dismissed' | 'converted' | …
  session_id     text,                 -- anonyme (fingerprint client, pas user_id)
  metadata       jsonb,                -- payload libre (source, email_domain, etc.)
  created_at     timestamptz not null default now()
);

create index if not exists idx_ab_events_experiment on public.ab_events (experiment, variant, event_name);
create index if not exists idx_ab_events_created_at on public.ab_events (created_at desc);

comment on table public.ab_events is
  'Tracking first-party des expériences A/B. Agrégé via /api/admin/ab-stats.';
