-- Table oracle_leads : capture des emails depuis le tunnel d'acquisition gratuit
-- A executer dans Supabase SQL Editor

CREATE TABLE IF NOT EXISTS oracle_leads (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           TEXT UNIQUE NOT NULL,
  first_name      TEXT,
  birth_date      DATE,
  source          TEXT DEFAULT 'hero_oracle',
  consent_marketing BOOLEAN DEFAULT TRUE,
  unsubscribed_at TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  -- pour suivre la sequence d'emails envoyes
  email_sequence_step INT DEFAULT 0,
  last_email_sent_at  TIMESTAMPTZ,
  converted_to_user_id UUID REFERENCES profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_oracle_leads_email ON oracle_leads(email);
CREATE INDEX IF NOT EXISTS idx_oracle_leads_unsubscribed ON oracle_leads(unsubscribed_at);

-- RLS : aucun acces direct depuis le client ; tout passe par le backend (service_role)
ALTER TABLE oracle_leads ENABLE ROW LEVEL SECURITY;
-- Pas de policy publique : seul le backend (service_role) peut lire/ecrire
