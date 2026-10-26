# 🚀 DEPLOYMENT GUIDE — Production Setup

**Status:** Frontend UI ✅ Complete | Backend API ✅ Complete | Ready for Deployment

---

## 1. LOCAL TESTING CHECKLIST

Before deploying to production, test locally:

### Backend Testing
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export ASTROLOGY_API_IO_KEY="your_key_here"
export STRIPE_API_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_test_..."
export RESEND_API_KEY="re_..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJ..."

# Run backend
uvicorn server:app --reload --port 8000
```

### Frontend Testing
```bash
cd frontend
npm install
REACT_APP_BACKEND_URL=http://localhost:8000 npm start
```

### Test Each Product Flow
1. Go to `/numerologie-pdf`
2. Fill in test form data
3. Click "Accéder à Mon Rapport"
4. If Stripe test: Use card `4242 4242 4242 4242` / any future date / any CVC
5. If promo bypass: Use code `ADMIN26`
6. Should redirect to `/numerologie-pdf/attente` (polling page)
7. Wait for PDF generation (30-60 seconds)
8. Check if download link appears

Repeat for:
- `/karma-destin-pdf`
- `/fenetre-rencontre-pdf` (both solo + duo modes)

---

## 2. DEPLOYMENT INFRASTRUCTURE

### Option A: Railway (Recommended for Simplicity)

#### Deploy Backend to Railway
```bash
# 1. Install Railway CLI
npm install -g railway

# 2. Login
railway login

# 3. Create new project
railway init

# 4. Link to Railway
railway link

# 5. Add environment variables
railway variables set ASTROLOGY_API_IO_KEY="your_key"
railway variables set STRIPE_API_KEY="sk_live_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_live_..."
railway variables set RESEND_API_KEY="re_..."
railway variables set SUPABASE_URL="https://xxx.supabase.co"
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJ..."

# 6. Deploy
railway up
```

#### Deploy Frontend to Railway
```bash
# Create public/package.json redirect to static build if needed
railway deploy
```

Or use Vercel (see Option B).

### Option B: Vercel (Best for React Frontend)

#### Deploy Backend to Railway / Deploy Frontend to Vercel

**Frontend:**
```bash
cd frontend
vercel --prod
```

Set environment variable in Vercel dashboard:
```
REACT_APP_BACKEND_URL=https://your-railway-backend-url.railway.app
```

**Backend:**
Use Railway as above, or:
```bash
# On Vercel (if using serverless functions)
# Add api/ folder with Python handler (more complex)
# Recommended: Use Railway or another Python host
```

---

## 3. SUPABASE STORAGE SETUP

Create storage bucket for PDF files:

```sql
-- In Supabase SQL Editor:
INSERT INTO storage.buckets (id, name, public)
VALUES ('reports', 'reports', true);

-- Grant public read access
CREATE POLICY "Public reports bucket"
ON storage.objects
FOR SELECT
USING (bucket_id = 'reports');

-- Grant service role write access
CREATE POLICY "Service role write to reports"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'reports');
```

**File Structure:**
```
reports/
├── numerologie/
│   └── {session_id}.pdf
├── karma/
│   └── {session_id}.pdf
└── fenetre/
    └── {session_id}.pdf
```

---

## 4. STRIPE WEBHOOK CONFIGURATION

### Create Webhook Endpoint

**In Stripe Dashboard:**
1. Go to Developers → Webhooks
2. Click "Add Endpoint"
3. Endpoint URL: `https://your-backend-url/api/webhook/stripe`
4. Select Events: `checkout.session.completed`
5. Copy Webhook Secret → Add to env vars

**Backend expects:**
```python
# backend/routes/webhook.py should have:
@router.post('/webhook/stripe')
async def handle_stripe_webhook(request: Request):
    # 1. Verify signature
    # 2. Get checkout session ID
    # 3. Update payment_transactions table
    # 4. Trigger PDF generation task
```

### Webhook Handler (if not already created)

```python
# backend/routes/webhook.py
from fastapi import APIRouter, Request
from stripe.error import SignatureVerificationError
import stripe

router = APIRouter(prefix="/webhook")

@router.post('/stripe')
async def handle_stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event['type'] == 'checkout.session.completed':
        session_id = event['data']['object']['id']
        
        # Update status in database
        supabase.table('payment_transactions').update(
            {'status': 'completed'}
        ).eq('session_id', session_id).execute()
        
        # Trigger PDF generation (already handled by checkout endpoint)
    
    return {'status': 'ok'}
```

---

## 5. DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Backend syntax check: `python -m py_compile backend/routes/*.py backend/services/*.py`
- [ ] Frontend build: `npm run build` (check for errors)
- [ ] Environment variables configured (all 7 required)
- [ ] Supabase tables created (payment_transactions, energy_cache)
- [ ] Supabase storage bucket created (reports)
- [ ] Stripe keys validated (test vs. live)
- [ ] Email templates tested (Resend)

### Deployment
- [ ] Deploy backend (Railway/Vercel)
- [ ] Deploy frontend (Vercel/Railway)
- [ ] Add backend URL to frontend env vars
- [ ] Configure Stripe webhook (point to deployed URL)
- [ ] Test product flow (full E2E in production sandbox)

### Post-Deployment
- [ ] Monitor logs (no critical errors)
- [ ] Test Stripe payment flow (real webhook)
- [ ] Verify email delivery (check Resend dashboard)
- [ ] Check PDF generation (Supabase storage)
- [ ] Test all 3 products (numerologie, karma, fenetre)

---

## 6. ENVIRONMENT VARIABLES (PROD)

```bash
# Astrology API
ASTROLOGY_API_IO_KEY=key_xyz_prod

# Stripe (LIVE keys)
STRIPE_API_KEY=sk_live_abc123
STRIPE_WEBHOOK_SECRET=whsec_live_abc123

# Email
RESEND_API_KEY=re_abc123_xyz

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxxx

# Frontend (Vercel)
REACT_APP_BACKEND_URL=https://your-api.railway.app
```

---

## 7. MONITORING & MAINTENANCE

### Daily Checks
- Stripe webhook failures (Developers → Webhooks → Recent Events)
- Email delivery issues (Resend → Logs)
- PDF generation errors (Backend logs)
- Database quota (Supabase dashboard)

### Weekly Checks
- User feedback (errors, missing features)
- API response times
- Storage usage (reports folder size)

### Monthly Checks
- Payment reconciliation (Stripe vs. database)
- Email bounce rates
- API rate limits (astrology-api.io)

---

## 8. ROLLBACK PLAN

If deployment fails:

1. **Frontend error:** Revert to last stable Vercel deployment (one-click on dashboard)
2. **Backend error:** Scale down Railway service, check logs, redeploy with fixes
3. **Database issue:** Restore from Supabase backup (daily auto-backups available)
4. **Stripe issues:** Check webhook status, re-send failed events manually if needed

---

## 9. NEXT MILESTONES

✅ Task 1: Backend API (Complete)
✅ Task 3: Frontend UI (Complete)
⏭️ Task 2: Production Deployment (Next)
⏭️ Task 4: Report Improvements (Optional)
⏭️ Task 5: Affiliate/Referral System (Optional)

**Estimated Timeline:**
- Deployment: 2-4 hours (infrastructure setup)
- Testing: 1-2 hours (full E2E validation)
- Launch: Ready when all checks pass ✓

---

## 📞 Support Resources

- **Stripe:** stripe.com/docs/payments/checkout
- **Vercel:** vercel.com/docs
- **Railway:** docs.railway.app
- **Supabase:** supabase.com/docs/reference/python
- **Resend:** resend.com/docs

🚀 **Ready to launch Plume Astrale monetized products!**
