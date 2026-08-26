-- Migration 2026-02-26 : Carte cadeau (gift_cards)
--
-- À exécuter dans le SQL Editor Supabase du projet.
-- Résout l'objection "je n'ai pas son heure de naissance" du segment "Celle qui offre" :
-- l'acheteur commande, le destinataire reçoit un code et complète ses propres données.

CREATE TABLE IF NOT EXISTS gift_cards (
    code TEXT PRIMARY KEY,                             -- ex: NOEL-A7B9-K3M2 (14 chars max)
    product_kind TEXT NOT NULL,                        -- 'theme_natal' | 'voyage_karmique' | 'kabbale'
    amount_cents INTEGER NOT NULL,                     -- Prix effectivement payé
    purchaser_email TEXT NOT NULL,                     -- Copie destinataire = acheteur pour reçu
    purchaser_first_name TEXT,
    recipient_email TEXT NOT NULL,                     -- À qui envoyer le code
    recipient_first_name TEXT,                         -- Optionnel (surprise si non fourni)
    personal_message TEXT,                             -- 800 chars max, formaté dans l'email
    stripe_session_id TEXT UNIQUE,                     -- Rattachement paiement
    payment_status TEXT NOT NULL DEFAULT 'pending',    -- 'pending' | 'paid' | 'refunded'
    deliver_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),     -- Immédiat ou date future (anniversaire J-0)
    delivered_at TIMESTAMPTZ,                          -- Email envoyé au destinataire
    redeemed_at TIMESTAMPTZ,                           -- Destinataire a complété ses données
    redeemed_pdf_url TEXT,                             -- Lien signé vers son PDF final
    redeemed_by_user_id UUID,                          -- Si le destinataire crée un compte
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gift_cards_recipient
    ON gift_cards (recipient_email);
CREATE INDEX IF NOT EXISTS idx_gift_cards_purchaser
    ON gift_cards (purchaser_email);
CREATE INDEX IF NOT EXISTS idx_gift_cards_deliver_pending
    ON gift_cards (deliver_at) WHERE delivered_at IS NULL AND payment_status = 'paid';

ALTER TABLE gift_cards ENABLE ROW LEVEL SECURITY;
