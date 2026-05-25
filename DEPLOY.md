# Plume Astrale — Deploiement Supabase + Railway + Netlify

## 1. Configurer Supabase (UNE SEULE FOIS)

1. Va sur https://supabase.com/dashboard/project/ebwicqvbkwogxneipaxh/sql/new
2. Copie-colle TOUT le contenu de `/app/supabase/schema.sql`
3. Clique **Run** — toutes les tables + RLS + trigger sont crees
4. Verifie dans **Database -> Tables** que tu vois : profiles, wallets, credit_transactions, payment_transactions, promo_codes, streaks, plume_chat_messages, journal_entries

## 2. Deployer le Backend sur Railway

1. Push ton repo sur GitHub (utilise "Save to GitHub" dans Emergent)
2. Sur https://railway.app -> New Project -> Deploy from GitHub repo
3. Selectionne ton repo, sous-dossier `/backend`
4. Ajoute ces variables d'env :
   - `SUPABASE_URL` = https://ebwicqvbkwogxneipaxh.supabase.co
   - `SUPABASE_SERVICE_ROLE_KEY` = (copie depuis backend/.env)
   - `SUPABASE_ANON_KEY` = (copie depuis backend/.env)
   - `SUPABASE_JWT_SECRET` = bf640975-ab0e-43a0-9b90-d22de3800041
   - `ASTROLOGY_API_USER_ID` = 649448
   - `ASTROLOGY_API_KEY` = fdc70a8227029d5e3f11ba9e495bb56995bb343a
   - `ASTROLOGY_API_ACCESS_TOKEN` = c520138ec226c81240e263e1034fdd53dfa71d23
   - `STRIPE_API_KEY` = ta cle Stripe LIVE (sk_live_...)
   - `EMERGENT_LLM_KEY` = (ta cle Emergent)
   - `CORS_ORIGINS` = https://ton-site.netlify.app
5. Railway detecte automatiquement Python + le Procfile -> deploie
6. Note l'URL publique (ex: https://plume-backend.up.railway.app)

## 3. Deployer le Frontend sur Netlify

1. Sur https://netlify.com -> Add new site -> Import from Git
2. Selectionne ton repo, base directory : `frontend`
3. Build command : `yarn build`, Publish directory : `frontend/build`
4. Ajoute ces variables d'env (scope = All) :
   - `REACT_APP_BACKEND_URL` = https://plume-backend.up.railway.app (URL Railway)
   - `REACT_APP_SUPABASE_URL` = https://ebwicqvbkwogxneipaxh.supabase.co
   - `REACT_APP_SUPABASE_ANON_KEY` = (anon key Supabase)
5. Deploy

## 4. Webhook Stripe (en prod)

1. Sur https://dashboard.stripe.com/webhooks -> Add endpoint
2. URL : `https://plume-backend.up.railway.app/api/webhook/stripe`
3. Selectionne l'evenement `checkout.session.completed`
4. Copie le webhook secret -> ajoute `STRIPE_WEBHOOK_SECRET` dans Railway

## 5. Tester en local (preview Emergent)

Le backend pointe deja sur ta vraie BDD Supabase, donc tout test ici se reflete dans ta base.
- Inscription / connexion : http://localhost:3000/inscription
- Chat Plume : http://localhost:3000/chat-astral
- Achat credits : http://localhost:3000/acheter-credits
