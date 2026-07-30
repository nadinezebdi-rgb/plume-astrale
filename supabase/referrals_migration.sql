-- ═══════════════════════════════════════════════════════════════════════
-- Programme de parrainage — un filleul achète → le parrain reçoit un
-- horoscope PDF offert de son signe.
-- À exécuter dans Supabase SQL Editor.
-- ═══════════════════════════════════════════════════════════════════════

-- 1) Code de parrainage sur chaque profil (8 caractères base32 sans ambiguïté)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS referral_code TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_referral_code ON profiles(referral_code) WHERE referral_code IS NOT NULL;

-- 2) Rattachement d'un filleul à son parrain (facultatif ; posé après signup si ?ref=X)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES profiles(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_referred_by ON profiles(referred_by) WHERE referred_by IS NOT NULL;

-- 3) Table de suivi des parrainages : première conversion payante + récompense envoyée
CREATE TABLE IF NOT EXISTS referrals (
  id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id                 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  referred_user_id            UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  first_purchase_session_id   TEXT,
  first_purchase_amount_cents INT,
  first_purchase_at           TIMESTAMPTZ,
  reward_sent_at              TIMESTAMPTZ,
  reward_horoscope_sign       TEXT,
  reward_email_id             TEXT,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(referred_user_id)   -- un filleul ne peut avoir qu'un seul parrain
);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_rewarded ON referrals(reward_sent_at) WHERE reward_sent_at IS NOT NULL;

ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
-- Aucune policy publique : seul le backend (service_role) accède.
