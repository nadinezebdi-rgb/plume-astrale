-- Migration 2026-02-27 : Flow d'approbation 72h "Vous lisez avant qu'on imprime"
--
-- À exécuter dans le SQL Editor Supabase du projet.
--
-- Contexte produit (Édition Reliée 149€) :
--   Après paiement, la cliente reçoit un email avec le PDF complet et un lien
--   d'approbation. Elle a 72h pour :
--     1. Approuver → on lance l'impression.
--     2. Refuser (texte qui ne touche pas) → remboursement intégral, rien imprimé.
--     3. Ne rien faire → rappels doux à 24h et 48h. À 72h, statut 'expired'
--        et l'admin doit trancher manuellement.
--
-- Les tokens `approve_token` et `refuse_token` sont opaques (uuid.hex, 32 chars).
-- Ils sont utilisés dans les liens email → 1-clic pour approuver/refuser.

CREATE TABLE IF NOT EXISTS print_approvals (
    id TEXT PRIMARY KEY,                                  -- uuid.hex (32 chars)
    order_ref TEXT NOT NULL,                              -- session_id Stripe ou payment_transactions.id
    product_kind TEXT NOT NULL DEFAULT 'edition_reliee',  -- 'edition_reliee' | 'edition_reliee_deux_vies'
    purchaser_email TEXT NOT NULL,
    purchaser_first_name TEXT,
    recipient_first_name TEXT,                            -- Pour personnaliser les emails ("Le livre de {recipient}")

    pdf_url TEXT NOT NULL,                                -- Lien opaque vers le PDF preview (relecture avant impression)

    status TEXT NOT NULL DEFAULT 'awaiting_review',       -- 'awaiting_review' | 'approved' | 'refused' | 'expired'
    approve_token TEXT NOT NULL UNIQUE,                   -- uuid.hex — GET /r/approve/{token}
    refuse_token TEXT NOT NULL UNIQUE,                    -- uuid.hex — POST /api/print-approval/refuse

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deadline_at TIMESTAMPTZ NOT NULL,                     -- created_at + 72h

    reminder_24h_sent_at TIMESTAMPTZ,                     -- Idempotence rappel J+1
    reminder_48h_sent_at TIMESTAMPTZ,                     -- Idempotence rappel J+2

    approved_at TIMESTAMPTZ,
    refused_at TIMESTAMPTZ,
    refused_reason TEXT,                                  -- Texte libre de la cliente
    expired_at TIMESTAMPTZ,

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_print_approvals_status_deadline
    ON print_approvals (status, deadline_at)
    WHERE status = 'awaiting_review';

CREATE INDEX IF NOT EXISTS idx_print_approvals_purchaser
    ON print_approvals (purchaser_email);

CREATE INDEX IF NOT EXISTS idx_print_approvals_order_ref
    ON print_approvals (order_ref);

ALTER TABLE print_approvals ENABLE ROW LEVEL SECURITY;
