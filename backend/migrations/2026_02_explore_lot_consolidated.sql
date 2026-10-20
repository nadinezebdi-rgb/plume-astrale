-- ═════════════════════════════════════════════════════════════════
-- MIGRATION CONSOLIDÉE Feb 2026 — 3 tables pour les features Explore
--   1. admin_alerts — historique alertes Resend (health-checks tiers)
--   2. ab_events — tracking first-party des expériences A/B
--   3. synastrie_lead_followups — logs email relance J+2 (idempotence)
--
-- À exécuter dans le SQL Editor Supabase. Idempotent (CREATE IF NOT EXISTS).
-- ═════════════════════════════════════════════════════════════════

-- ────────────────────────────────────────────────────────────────
-- 1) admin_alerts
-- ────────────────────────────────────────────────────────────────
create table if not exists public.admin_alerts (
  id             uuid primary key default gen_random_uuid(),
  alert_type     text not null,
  severity       text not null default 'high',
  subject        text not null,
  reason         text,
  http_status    int,
  error_detail   text,
  payload        jsonb,
  resend_id      text,
  recipient      text,
  resolved_at    timestamptz,
  created_at     timestamptz not null default now()
);

create index if not exists idx_admin_alerts_created_at on public.admin_alerts (created_at desc);
create index if not exists idx_admin_alerts_type on public.admin_alerts (alert_type);
create index if not exists idx_admin_alerts_resolved on public.admin_alerts (resolved_at);

comment on table public.admin_alerts is
  'Historique des alertes système envoyées via Resend (health-checks tiers, incidents prod).';

-- ────────────────────────────────────────────────────────────────
-- 2) ab_events
-- ────────────────────────────────────────────────────────────────
create table if not exists public.ab_events (
  id             uuid primary key default gen_random_uuid(),
  experiment     text not null,
  variant        text not null,
  event_name     text not null,
  session_id     text,
  metadata       jsonb,
  created_at     timestamptz not null default now()
);

create index if not exists idx_ab_events_experiment on public.ab_events (experiment, variant, event_name);
create index if not exists idx_ab_events_created_at on public.ab_events (created_at desc);

comment on table public.ab_events is
  'Tracking first-party des expériences A/B. Agrégé via /api/admin/ab-stats.';

-- ────────────────────────────────────────────────────────────────
-- 3) synastrie_lead_followups
-- ────────────────────────────────────────────────────────────────
create table if not exists public.synastrie_lead_followups (
  id           uuid primary key default gen_random_uuid(),
  email        text not null,
  lead_id      uuid,
  resend_id    text,
  sent_at      timestamptz not null default now()
);

create unique index if not exists uq_synastrie_lead_followups_email
  on public.synastrie_lead_followups (email);
create index if not exists idx_synastrie_lead_followups_sent_at
  on public.synastrie_lead_followups (sent_at desc);

comment on table public.synastrie_lead_followups is
  'Logs des emails de relance J+2 synastrie (code SYNEXT10 -10%) — garde idempotence.';
