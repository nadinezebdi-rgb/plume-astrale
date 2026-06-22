-- ═══════════════════════════════════════════════════════════════════════
-- Synastrie haut-ticket 49€ (Phase 3 cahier des charges)
-- A executer dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

-- Achat Synastrie one-shot (Stripe payment mode=payment)
CREATE TABLE IF NOT EXISTS synastrie_purchases (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES profiles(id) ON DELETE CASCADE,
  email               TEXT,                  -- snapshot email (en cas d'achat invite)
  stripe_session_id   TEXT UNIQUE,
  stripe_payment_intent TEXT,
  amount_cents        INT NOT NULL DEFAULT 4900,
  currency            TEXT NOT NULL DEFAULT 'eur',
  status              TEXT NOT NULL DEFAULT 'pending',  -- pending | paid | failed
  -- Donnees natales des 2 personnes (JSON)
  person1_data        JSONB NOT NULL,
  person2_data        JSONB NOT NULL,
  -- PDF
  pdf_generated_at    TIMESTAMPTZ,
  pdf_path            TEXT,                  -- chemin storage Supabase ou URL
  -- Resend email envoye
  email_sent_at       TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_synastrie_user ON synastrie_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_synastrie_session ON synastrie_purchases(stripe_session_id);
CREATE INDEX IF NOT EXISTS idx_synastrie_status ON synastrie_purchases(status);

ALTER TABLE synastrie_purchases ENABLE ROW LEVEL SECURITY;
-- Aucune policy publique : seul le backend (service_role) accede.
