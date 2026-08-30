-- ═══════════════════════════════════════════════════════════════════════════
-- Migration : stripe_webhook_events (idempotence globale des webhooks Stripe)
-- ═══════════════════════════════════════════════════════════════════════════
-- Contexte : incident P0 février 2026. Sans idempotence sur event.id, Stripe
-- retry (jusqu'à 3 jours) un même event si le handler n'a pas répondu 200
-- en < 30 s → doublons de PDF, emails et transactions.
--
-- Cette table sert de verrou :
--   • INSERT ON CONFLICT DO NOTHING → si déjà là, on ignore
--   • champs `status` / `handled_at` pour tracer erreurs handler
--
-- À coller dans Supabase → SQL Editor → Run.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.stripe_webhook_events (
    event_id      TEXT PRIMARY KEY,
    event_type    TEXT NOT NULL,
    session_id    TEXT,
    kind          TEXT,
    status        TEXT NOT NULL DEFAULT 'received',  -- received | processing | done | failed
    received_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    handled_at    TIMESTAMPTZ,
    error_message TEXT,
    payload       JSONB
);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_status
    ON public.stripe_webhook_events (status);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_session
    ON public.stripe_webhook_events (session_id);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_received_at
    ON public.stripe_webhook_events (received_at DESC);

-- Row Level Security : lecture réservée au service_role (aucun accès public).
ALTER TABLE public.stripe_webhook_events ENABLE ROW LEVEL SECURITY;

-- Aucune policy = seul le service_role peut lire/écrire (comportement souhaité).
COMMENT ON TABLE public.stripe_webhook_events IS
    'Idempotence des webhooks Stripe (guard global sur event.id) — 2026-02.';
