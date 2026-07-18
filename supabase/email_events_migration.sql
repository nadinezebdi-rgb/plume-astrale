-- ============================================================================
-- Table email_events — journal complet des envois Resend
-- ============================================================================
-- Deux sources d'entrées :
--   1) 'app'    → écrit par le backend AVANT chaque appel Resend (statut 'queued'
--                 ou 'send_failed' si Resend renvoie une erreur HTTP)
--   2) 'resend' → écrit par le webhook /api/webhook/resend quand Resend nous
--                 pousse les events email.sent, email.delivered, email.bounced,
--                 email.complained, email.opened, email.clicked, email.delivery_delayed
--
-- Cela permet de détecter :
--   - Les emails jamais demandés (aucune ligne app pour une transaction payée)
--   - Les emails demandés mais rejetés par Resend (send_failed)
--   - Les emails acceptés par Resend mais bounced / spam
-- ============================================================================

create table if not exists public.email_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  -- Identification
  source text not null check (source in ('app','resend')),
  event_type text not null,          -- 'queued'|'send_failed'|'email.sent'|'email.delivered'|'email.bounced'|'email.complained'|'email.opened'|'email.clicked'|'email.delivery_delayed'
  resend_id text,                    -- id retourné par l'API Resend (POST /emails) ou event.data.email_id
  provider_event_id text,            -- id de l'event webhook lui-même (dédup)

  -- Contenu
  to_email text,
  from_email text,
  subject text,
  product text,                      -- 'kabbale' | 'pack_karmique' | 'numerologie' | 'karma_destin' | 'fenetre_rencontre' | 'compatibilite_ultime' | 'cart_recovery' | 'lead_nurture' | 'test'
  session_id text,                   -- lien vers payment_transactions si applicable
  http_status int,                   -- status HTTP retourné par Resend au POST
  error_message text,                -- corps d'erreur Resend si send_failed / bounced
  raw jsonb                          -- payload brut (event ou réponse Resend, tronqué)
);

create index if not exists idx_email_events_created_at on public.email_events (created_at desc);
create index if not exists idx_email_events_to_email on public.email_events (to_email);
create index if not exists idx_email_events_resend_id on public.email_events (resend_id);
create index if not exists idx_email_events_provider_event_id on public.email_events (provider_event_id);
create index if not exists idx_email_events_session_id on public.email_events (session_id);
create index if not exists idx_email_events_event_type on public.email_events (event_type);

comment on table public.email_events is 'Journal des envois email (source=app) + webhook Resend (source=resend). Utilisé pour diagnostiquer les livraisons manquantes.';
