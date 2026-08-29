-- ═══════════════════════════════════════════════════════════════════════════
-- Complements à 2026_02_28_stripe_webhook_events.sql (audit ChatGPT — mars 2026)
-- À jouer une seule fois dans le SQL Editor Supabase. Idempotent : rejeu safe.
-- ═══════════════════════════════════════════════════════════════════════════

-- 1) Index utilisés par le dry-run (status,received_at) et par la reprise des
--    events orphelins.
CREATE INDEX IF NOT EXISTS idx_swe_status_received
    ON public.stripe_webhook_events (status, received_at);

CREATE INDEX IF NOT EXISTS idx_swe_session
    ON public.stripe_webhook_events (session_id);

-- 2) Compteur de reprises (attempts) : permet de repérer un event qui boucle.
--    Le handler NE l'incrémente PAS automatiquement pour éviter une écriture
--    supplémentaire à chaque tentative — c'est du monitoring optionnel qu'on
--    peut brancher plus tard sur `_claim_event()` si besoin.
ALTER TABLE public.stripe_webhook_events
    ADD COLUMN IF NOT EXISTS attempts INT NOT NULL DEFAULT 0;

-- ═══════════════════════════════════════════════════════════════════════════
-- 3) GARDE-FOU MÉTIER (COMMENTÉ INTENTIONNELLEMENT)
-- ═══════════════════════════════════════════════════════════════════════════
-- L'idempotence par event_id empêche de retraiter le MÊME event Stripe.
-- Elle n'empêche PAS deux events DIFFÉRENTS (ex: checkout.session.completed
-- + payment_intent.succeeded) de livrer deux fois la même commande.
--
-- Chez Plume Astrale, la table de livraison est `payment_transactions` avec
-- `session_id` UNIQUE (fixé par Stripe, 1 session = 1 ligne) et le flag
-- `metadata.pdf_status = 'success'` + `metadata.pdf_path` qui trace la
-- livraison. Le garde-fou métier est :
--
--   a) `session_id` PK unique dans payment_transactions
--   b) le handler `theme_natal_oneshot_service.build_pdf(...)` skip si
--      `md.get('pdf_path') and not force` (cf. services/theme_natal_oneshot_service.py L85)
--
-- Ces 2 garde-fous suffisent pour la stack actuelle. La contrainte
-- UNIQUE(session_id, kind) ci-dessous serait redondante MAIS utile si un jour
-- on veut découpler « transaction » et « livraison PDF » dans deux tables.
--
-- Pour l'activer plus tard, décommenter ces 3 lignes après avoir créé la
-- vraie table de livraison :
--
-- CREATE UNIQUE INDEX IF NOT EXISTS uniq_livraison_session_kind
--     ON public.<table_de_livraison_dediee> (session_id, kind);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4) Vue de santé pour /admin/payments-health et monitoring
-- ═══════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE VIEW public.stripe_webhook_health AS
SELECT
    status,
    count(*)                                    AS total,
    max(received_at)                            AS dernier_event,
    count(*) FILTER (
        WHERE status = 'processing'
          AND received_at < now() - interval '10 minutes'
    )                                           AS orphelins
FROM public.stripe_webhook_events
GROUP BY status;

COMMENT ON VIEW public.stripe_webhook_health IS
    'Santé webhooks Stripe — passé la fenêtre 10min, un processing devient orphelin (crash/redeploy).';
