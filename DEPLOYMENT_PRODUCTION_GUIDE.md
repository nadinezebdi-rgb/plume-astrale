# 🚀 PRODUCTION DEPLOYMENT GUIDE

**Status:** READY TO DEPLOY  
**Estimated Time:** 2-3 hours  

---

## ⚠️ IMPORTANT: CREDENTIALS

Keep your credentials SAFE:
- Stripe keys: Store in `.env` (never commit!)
- Supabase keys: Store in `.env` (never commit!)
- API keys: Store in `.env` (never commit!)

**Use `.env` file locally, Railway/Vercel env vars in production.**

---

## 📋 PHASE 1: RAILWAY BACKEND (30 min)

### 1. Create Railway Project
```
1. Go to https://railway.app
2. Login with GitHub
3. Create "New Project" → "Deploy from GitHub"
4. Select your repo
5. Branch: main
```

### 2. Configure Environment Variables
Set these in Railway Dashboard:
```
SUPABASE_URL=[your-supabase-url]
SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]
SUPABASE_ANON_KEY=[your-anon-key]

STRIPE_API_KEY=sk_live_[your-stripe-secret-key]
STRIPE_WEBHOOK_SECRET=rk_live_[your-webhook-secret]

ASTROLOGY_API_IO_KEY=[your-astrology-api-key]
```

### 3. Configure Service
```
- Root Directory: /backend
- Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### 4. Deploy
- Click "Deploy"
- Wait ~2-3 minutes
- Copy Backend URL when ready

✅ **Backend URL:** Save this! (e.g., `https://your-app.up.railway.app`)

---

## 📋 PHASE 2: VERCEL FRONTEND (15 min)

### 1. Create Vercel Project
```
1. Go to https://vercel.com
2. Login with GitHub
3. Create new project
4. Select your repo
5. Framework: React
6. Root Directory: ./frontend
```

### 2. Environment Variables
```
REACT_APP_BACKEND_URL=[your-railway-url-from-phase-1]
REACT_APP_SUPABASE_URL=[your-supabase-url]
REACT_APP_SUPABASE_ANON_KEY=[your-anon-key]
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_[your-stripe-public-key]
```

### 3. Deploy
- Click "Deploy"
- Wait ~2-3 minutes
- Save Frontend URL

✅ **Frontend URL:** Save this! (e.g., `https://your-app.vercel.app`)

---

## 📋 PHASE 3: SUPABASE STORAGE (10 min)

Create storage bucket for PDFs:

```sql
-- In Supabase SQL Editor:

INSERT INTO storage.buckets (id, name, public)
VALUES ('reports', 'reports', true);

CREATE POLICY "Public read reports"
ON storage.objects
FOR SELECT
USING (bucket_id = 'reports');

CREATE POLICY "Service role write reports"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'reports');
```

✅ Bucket "reports" is ready

---

## 📋 PHASE 4: STRIPE WEBHOOK (10 min)

### 1. Add Webhook in Stripe
```
1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add Endpoint"
3. URL: https://[your-railway-url]/api/webhook/stripe
4. Event: checkout.session.completed
5. Save
```

### 2. Copy Webhook Secret
- Go to your endpoint
- Copy signing secret
- Add to Railway as `STRIPE_WEBHOOK_SECRET`

✅ Webhook configured

---

## 📋 PHASE 5: TEST (20 min)

### Test 1: Frontend loads
```
Open: https://[your-vercel-url]/numerologie-pdf
✅ Should see landing page with form
```

### Test 2: Promo Code (no payment)
```
1. Fill form
2. Use code: ADMIN26
3. Click submit
4. Should redirect to /attente page
5. Wait ~60s for PDF
```

### Test 3: Stripe Payment
```
1. Fill form
2. Click submit (no promo code)
3. Use test card: 4242 4242 4242 4242
4. Expiry: 12/26
5. CVC: 123
6. Complete payment
7. Should generate PDF
```

### Test 4: Webhook
```
In Stripe dashboard → Webhooks → Your endpoint
Should see checkout.session.completed events
```

---

## ✅ GO LIVE CHECKLIST

- [ ] Phase 1: Railway backend deployed
- [ ] Phase 2: Vercel frontend deployed
- [ ] Phase 3: Supabase bucket created
- [ ] Phase 4: Stripe webhook configured
- [ ] Phase 5: All tests passed

---

## 📊 PRODUCTION MONITORING

**Keep these links handy:**

- Railway: https://railway.app/dashboard
- Vercel: https://vercel.com/dashboard
- Supabase: https://app.supabase.com
- Stripe: https://dashboard.stripe.com

---

## 🎉 READY FOR PRODUCTION

When all checkboxes are done:
- ✅ Plume Astrale is LIVE
- 💰 Stripe accepts payments
- 📧 Emails ready (once DNS propagates)
- 📊 Ready to scale

---

## ⚠️ IMPORTANT REMINDERS

1. **Never commit secrets** - Use `.env` file only
2. **Stripe webhook** - Must point to correct backend URL
3. **Supabase bucket** - Must be public for downloads
4. **Environment variables** - Same in all 3 platforms (Railway, Vercel, local)

🚀 **You're ready to deploy!**
