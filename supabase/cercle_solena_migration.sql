-- ============================================================================
-- Migration : Cercle Soléna (abonnement mensuel 19€) — 2026-02-20
-- ============================================================================
-- À exécuter dans Supabase Studio → SQL Editor.
-- Idempotent : peut être ré-exécuté sans erreur.
-- ============================================================================

-- 1. Colonnes additionnelles sur profiles
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS stripe_customer_id text,
  ADD COLUMN IF NOT EXISTS is_cercle_member boolean NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer_id ON profiles(stripe_customer_id);

-- 2. Table subscriptions (une ligne par abonnement Stripe)
CREATE TABLE IF NOT EXISTS subscriptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  product text NOT NULL,                    -- ex: 'cercle_solena'
  stripe_subscription_id text NOT NULL UNIQUE,
  stripe_customer_id text,
  status text NOT NULL,                     -- active|trialing|past_due|canceled|unpaid|incomplete
  current_period_end timestamptz,
  cancel_at_period_end boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- 3. Table credit_grants (idempotence + audit trail des crédits offerts)
CREATE TABLE IF NOT EXISTS credit_grants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  amount integer NOT NULL,
  reason text NOT NULL,                     -- 'cercle_solena' | 'signup_bonus' | 'admin_gift' | ...
  external_id text,                         -- ex: invoice_id Stripe pour idempotence
  granted_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (reason, external_id)
);

CREATE INDEX IF NOT EXISTS idx_credit_grants_user_id ON credit_grants(user_id);

-- 4. RLS — les utilisateurs ne peuvent voir que leurs propres subscriptions
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_grants ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_read_own_subscriptions" ON subscriptions;
CREATE POLICY "user_read_own_subscriptions" ON subscriptions
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "user_read_own_credit_grants" ON credit_grants;
CREATE POLICY "user_read_own_credit_grants" ON credit_grants
  FOR SELECT USING (auth.uid() = user_id);

-- Backend admin (service_role) a full access (bypasse RLS automatiquement).
