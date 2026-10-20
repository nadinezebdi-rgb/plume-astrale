-- Table : admin_alerts
-- Objectif : historique des alertes système envoyées (astrology-api.io 401/5xx, etc.)
-- Visualisable depuis /admin/alerts pour suivre la fiabilité des intégrations tierces.
create table if not exists public.admin_alerts (
  id             uuid primary key default gen_random_uuid(),
  alert_type     text not null,                -- 'astrology_io_auth' | 'astrology_io_5xx_streak' | ...
  severity       text not null default 'high', -- 'low' | 'medium' | 'high' | 'critical'
  subject        text not null,                -- sujet email ressortant
  reason         text,                         -- 'auth' | '5xx_streak' | ...
  http_status    int,                          -- status HTTP capturé (401, 500, etc.)
  error_detail   text,                         -- message d'erreur abrégé
  payload        jsonb,                        -- payload libre (key_fingerprint, latency_ms, checked_at…)
  resend_id      text,                         -- id Resend si envoi email réussi
  recipient      text,                         -- destinataire (ex: contact@plume-astrale.fr)
  resolved_at    timestamptz,                  -- rempli manuellement quand incident clos
  created_at     timestamptz not null default now()
);

create index if not exists idx_admin_alerts_created_at on public.admin_alerts (created_at desc);
create index if not exists idx_admin_alerts_type on public.admin_alerts (alert_type);
create index if not exists idx_admin_alerts_resolved on public.admin_alerts (resolved_at);

comment on table public.admin_alerts is
  'Historique des alertes système envoyées via Resend (health-checks tiers, incidents prod).';
