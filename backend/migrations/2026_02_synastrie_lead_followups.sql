-- Table : synastrie_lead_followups
-- Objectif : marquer les emails de relance J+2 déjà envoyés aux leads du
-- lead-magnet synastrie (POST /api/synastrie/free-extract) qui n'ont pas
-- acheté la synastrie complète 49€. Alimentée par la boucle
-- synastrie_lead_followup_loop() toutes les 6h.
create table if not exists public.synastrie_lead_followups (
  id           uuid primary key default gen_random_uuid(),
  email        text not null,
  lead_id      uuid,                   -- oracle_leads.id référencé (sans FK pour résilience)
  resend_id    text,
  sent_at      timestamptz not null default now()
);

create unique index if not exists uq_synastrie_lead_followups_email
  on public.synastrie_lead_followups (email);
create index if not exists idx_synastrie_lead_followups_sent_at
  on public.synastrie_lead_followups (sent_at desc);

comment on table public.synastrie_lead_followups is
  'Logs des emails de relance J+2 synastrie (code SYNEXT10 -10%) — garde idempotence.';
