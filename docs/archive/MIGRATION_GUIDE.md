# Guide d'exécution des Migrations SQL — Plume Astrale

## 📊 Vos identifiants Supabase

```
Project URL : https://ebwicqvbkwogxneipaxh.supabase.co
Email Admin : admin@plume-astrale.fr
Password   : PlumeAdmin2026
```

---

## 🚀 Étapes pour exécuter les migrations

### 1. Accéder à Supabase SQL Editor

1. Va sur [app.supabase.com](https://app.supabase.com)
2. Connecte-toi avec `admin@plume-astrale.fr` / `PlumeAdmin2026`
3. Sélectionne le projet **plume-astrale**
4. Clique sur **"SQL Editor"** (à gauche)

### 2. Exécuter les 3 migrations dans l'ordre

#### Migration 1️⃣ : Oracle Leads (Email Tunnel)

**Copie-colle ce code :**

```sql
-- Table oracle_leads : capture des emails depuis le tunnel d'acquisition gratuit
CREATE TABLE IF NOT EXISTS oracle_leads (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           TEXT UNIQUE NOT NULL,
  first_name      TEXT,
  birth_date      DATE,
  source          TEXT DEFAULT 'hero_oracle',
  consent_marketing BOOLEAN DEFAULT TRUE,
  unsubscribed_at TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  email_sequence_step INT DEFAULT 0,
  last_email_sent_at  TIMESTAMPTZ,
  converted_to_user_id UUID REFERENCES profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_oracle_leads_email ON oracle_leads(email);
CREATE INDEX IF NOT EXISTS idx_oracle_leads_unsubscribed ON oracle_leads(unsubscribed_at);

ALTER TABLE oracle_leads ENABLE ROW LEVEL SECURITY;
```

**Puis clique "RUN"** ✅

---

#### Migration 2️⃣ : Cercle Dashboard (Rituel quotidien)

**Copie-colle ce code :**

```sql
-- Conseil de la Plume cache 24h par utilisateur
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

-- Check-in matinal (humeur + intention)
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

-- Reflexion du soir (journal prive)
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

-- Etat de streak
CREATE TABLE IF NOT EXISTS cercle_streaks (
  user_id          UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
  current_streak   INT DEFAULT 0,
  longest_streak   INT DEFAULT 0,
  total_checkins   INT DEFAULT 0,
  last_checkin_day DATE,
  grace_used_month TEXT,
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE cercle_daily_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_checkins        ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_reflections     ENABLE ROW LEVEL SECURITY;
ALTER TABLE cercle_streaks         ENABLE ROW LEVEL SECURITY;
```

**Puis clique "RUN"** ✅

---

#### Migration 3️⃣ : Synastrie (Paiements 49€)

**Copie-colle ce code :**

```sql
-- Achat Synastrie one-shot (Stripe)
CREATE TABLE IF NOT EXISTS synastrie_purchases (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES profiles(id) ON DELETE CASCADE,
  email               TEXT,
  stripe_session_id   TEXT UNIQUE,
  stripe_payment_intent TEXT,
  amount_cents        INT NOT NULL DEFAULT 4900,
  currency            TEXT NOT NULL DEFAULT 'eur',
  status              TEXT NOT NULL DEFAULT 'pending',
  person1_data        JSONB NOT NULL,
  person2_data        JSONB NOT NULL,
  pdf_generated_at    TIMESTAMPTZ,
  pdf_path            TEXT,
  email_sent_at       TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_synastrie_user ON synastrie_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_synastrie_session ON synastrie_purchases(stripe_session_id);
CREATE INDEX IF NOT EXISTS idx_synastrie_status ON synastrie_purchases(status);

ALTER TABLE synastrie_purchases ENABLE ROW LEVEL SECURITY;
```

**Puis clique "RUN"** ✅

---

## ✅ Vérifier que les migrations ont réussi

Après chaque migration, tu devrais voir:
- ✅ `Query succeeded with 0 rows` ou `Query succeeded with X rows`
- Pas d'erreur en rouge

**Pour vérifier les tables créées:**

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Tu devrais voir:
- ✅ `cercle_checkins`
- ✅ `cercle_daily_insights`
- ✅ `cercle_reflections`
- ✅ `cercle_streaks`
- ✅ `oracle_leads`
- ✅ `synastrie_purchases`

---

## 🧪 Tester les migrations depuis le backend

Une fois les migrations exécutées, tu peux tester avec:

```bash
cd backend
python -m pytest tests/test_migrations.py -v
```

---

## 🎯 Résultat attendu

Après les migrations:
- ✅ Dashboard Cercle fonctionne à 100% (checkin → UI flip immédiat)
- ✅ Synastrie paiements persistés dans la DB
- ✅ Oracle leads capturés et trackés
- ✅ Aucune erreur de persistance

