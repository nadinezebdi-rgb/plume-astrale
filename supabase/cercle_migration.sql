-- ═══════════════════════════════════════════════════════════════════════
-- LE CERCLE — Dashboard rituel quotidien (Phase 2 cahier des charges)
-- A executer dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════

-- Conseil de la Plume cache 24h par utilisateur (1 doc / user / day)
CREATE TABLE IF NOT EXISTS cercle_daily_insights (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  day             DATE NOT NULL,
  insight         TEXT NOT NULL,
  mood_snapshot   TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, day)
);
CREATE INDEX IF NOT EXISTS idx_cercle_insights_user_day ON cercle_daily_insights(user_id, day);

-- Check-in matinal (humeur + intention) — 1 doc / user / day
CREATE TABLE IF NOT EXISTS cercle_checkins (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  day             DATE NOT NULL,
  mood            TEXT NOT NULL,
  intention       TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, day)
);
CREATE INDEX IF NOT EXISTS idx_cercle_checkins_user_day ON cercle_checkins(user_id, day);

-- Reflexion du soir (journal prive) + reponse Plume (historique)
CREATE TABLE IF NOT EXISTS cercle_reflections (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  day             DATE NOT NULL,
  entry           TEXT NOT NULL,
  plume_response  TEXT,
  mood            TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cercle_reflections_user_created ON cercle_reflections(user_id, created_at DESC);

-- Etat de streak (1 doc / user)
CREATE TABLE IF NOT EXISTS cercle_streaks (
  user_id          UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
  current_streak   INT DEFAULT 0,
  longest_streak   INT DEFAULT 0,
  total_checkins   INT DEFAULT 0,
  last_checkin_day DATE,
  grace_used_month TEXT,  -- format YYYY-MM, 1 jour de grace offert par mois
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- RLS : aucun acces direct depuis le client; tout passe par le backend (service_role)
ALTER TABLE cercle_daily_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_checkins        ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_reflections     ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_streaks         ENABLE ROW LEVEL SECURITY;
