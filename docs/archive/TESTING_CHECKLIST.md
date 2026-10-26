# 🧪 FUNNEL TESTING CHECKLIST - Priority #3

**Objective:** Validate the complete UX transformation funnel works end-to-end
**Time:** 30 minutes
**Environment:** Local development
**Date:** 2026-07-11

---

## 🚀 STEP 0: Start Local Environment

```bash
# Terminal 1: Start backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
# Should show: "Running on http://localhost:8001"

# Terminal 2: Start frontend (wait 30s for backend to be ready)
cd frontend
REACT_APP_BACKEND_URL=http://localhost:8001 yarn start
# Should show: "Compiled successfully! You can now view plume-astrale in the browser."
```

**✅ Checkpoint:** Both servers running on `http://localhost:3000` (frontend)

---

## 🎯 TEST #1: QuickOracle Landing (5 min)

### 1.1 - Oracle Button Visible
- [ ] Open `http://localhost:3000` in browser
- [ ] Page loads with dark background + stars animation
- [ ] See gold button: **"✨ Découvrez votre oracle du jour GRATUITEMENT"**
- [ ] Button has hover effect (scale-105)

**Expected:** Gold gradient button appears instead of form

**Result:** ✅ / ❌ (Notes: __________________)

---

### 1.2 - Oracle Opens
- [ ] Click the gold button
- [ ] QuickOracle modal opens
- [ ] See zodiac signs (12 options)
- [ ] Modal has close (X) button top-right
- [ ] Background dimmed

**Expected:** QuickOracle component renders with all zodiac signs

**Result:** ✅ / ❌ (Notes: __________________)

---

### 1.3 - Select Sign & View Oracle
- [ ] Click on a zodiac sign (e.g., "Bélier")
- [ ] Oracle text appears below
- [ ] Oracle text is personalized for sign (should mention "Mercure", "action", etc.)
- [ ] See button: "Voir la lecture COMPLÈTE"
- [ ] All text is readable (good contrast)

**Expected:** Oracle displays with sign-specific reading in French

**Result:** ✅ / ❌ (Notes: __________________)

---

### 1.4 - Proceed to Packs
- [ ] Click "Voir la lecture COMPLÈTE" button
- [ ] Modal closes
- [ ] 3 packs displayed below oracle
- [ ] Packs are visible and readable

**Expected:** Transition from oracle to pack selection smooth

**Result:** ✅ / ❌ (Notes: __________________)

---

## 💰 TEST #2: Pack Visualization & Psychology (8 min)

### 2.1 - All 3 Packs Visible
- [ ] Pack 1 "🌙 Initiation" visible
  - Price: 4.99€
  - Credits: 15
  - Accent color: #A89B7E
- [ ] Pack 2 "✨ Clarté" visible
  - Price: 14.99€
  - Credits: 60
  - Accent color: #D4AF37 (GOLD)
- [ ] Pack 3 "🔥 Flammes Jumelles" visible
  - Price: 29.99€
  - Credits: 130
  - Accent color: #E8944A

**Expected:** 3 packs with correct prices, emojis, and colors

**Result:** ✅ / ❌ (Notes: __________________)

---

### 2.2 - Pack 2 is Highlighted (BESTSELLER)
- [ ] Pack 2 "Clarté" has:
  - [ ] ⭐ Badge: "BESTSELLER"
  - [ ] Box shadow larger than others
  - [ ] Slight scale/transform emphasis
  - [ ] Different background color (highlighted)
  - [ ] Text: "Économise 5€" visible
  - [ ] Text: "78% choisissent ce pack" visible

**Expected:** Pack 2 clearly distinguished as recommended option

**Result:** ✅ / ❌ (Notes: __________________)

---

### 2.3 - Price Per Credit Visible
- [ ] Hover/View Pack 1:
  - [ ] Shows: "0.25€/crédit" or "€/cr"
- [ ] Hover/View Pack 2:
  - [ ] Shows: "0.25€/crédit"
- [ ] Hover/View Pack 3:
  - [ ] Shows: "0.23€/crédit" (best value)

**Expected:** All packs show price-per-credit ratio

**Result:** ✅ / ❌ (Notes: __________________)

---

### 2.4 - Feature Checkmarks
- [ ] Each pack shows feature list:
  - [ ] "✓ Accès chat Solena"
  - [ ] "✓ Lectures illimitées"
  - [ ] "✓ Support email"
- [ ] Checkmarks visible and readable

**Expected:** Pack differentiation via features

**Result:** ✅ / ❌ (Notes: __________________)

---

## 🛒 TEST #3: Checkout Flow (10 min)

### 3.1 - Select Pack 2 (Clarté)
- [ ] Click on Pack 2 card anywhere (not just button)
- [ ] Button lights up: "Débloquer Clarté"
- [ ] Click "Débloquer Clarté" button
- [ ] Page transitions to checkout

**Expected:** Smooth transition to Stripe checkout

**Result:** ✅ / ❌ (Notes: __________________)

---

### 3.2 - Stripe Checkout
- [ ] Stripe checkout page loads
- [ ] Shows:
  - [ ] Price: 14.99€
  - [ ] Product: "60 Crédits - Clarté"
  - [ ] Email field
  - [ ] Card field (4242 4242 4242 4242)
- [ ] Page is secure (HTTPS or dev environment)

**Expected:** Stripe iframe loads correctly

**Result:** ✅ / ❌ (Notes: __________________)

---

### 3.3 - Test Payment
- [ ] Fill email: `test@example.com`
- [ ] Fill card: `4242 4242 4242 4242`
- [ ] Expiry: `12/25`
- [ ] CVC: `123`
- [ ] Click "Pay 14.99€"
- [ ] Payment processes (may take 3-5 seconds)
- [ ] Redirect to success page or confirmation

**Expected:** Payment completes without errors

**Result:** ✅ / ❌ (Notes: __________________)

---

### 3.4 - Success Confirmation
- [ ] After payment, see confirmation message
- [ ] Message shows: "Paiement réussi" or success state
- [ ] Credits appear in account
- [ ] Can proceed to next feature

**Expected:** User receives credits and sees success state

**Result:** ✅ / ❌ (Notes: __________________)

---

## 📱 TEST #4: Mobile Responsiveness (5 min)

### 4.1 - Open DevTools
- [ ] Press `F12` to open DevTools
- [ ] Click device toggle (iPhone icon)
- [ ] Select "iPhone 12" or similar

**Expected:** Browser enters mobile view

**Result:** ✅ / ❌

---

### 4.2 - Oracle Button on Mobile
- [ ] Refresh page (Ctrl+R)
- [ ] See gold button on mobile
- [ ] Button width: full width (100% of container)
- [ ] Padding: at least 44x44px (thumb-clickable)
- [ ] Text visible and not truncated

**Expected:** Button is thumb-friendly and fully responsive

**Result:** ✅ / ❌ (Notes: __________________)

---

### 4.3 - QuickOracle on Mobile
- [ ] Click oracle button
- [ ] Modal opens correctly on mobile
- [ ] Zodiac signs arranged vertically (not horizontally)
- [ ] Each sign is clickable (44x44px minimum)
- [ ] Scrolling is smooth

**Expected:** Modal responsive to mobile screen size

**Result:** ✅ / ❌ (Notes: __________________)

---

### 4.4 - Packs on Mobile
- [ ] Click "Voir la lecture COMPLÈTE"
- [ ] 3 packs visible on mobile
- [ ] Packs stack vertically (not 3 columns)
- [ ] Each pack is tappable (large buttons)
- [ ] Text is readable (font size appropriate)
- [ ] No horizontal scrolling required

**Expected:** Packs adapt to mobile layout

**Result:** ✅ / ❌ (Notes: __________________)

---

### 4.5 - Checkout on Mobile
- [ ] Click "Débloquer Clarté" on mobile
- [ ] Stripe checkout loads on mobile
- [ ] Form fields are large (at least 44px tall)
- [ ] No content hidden by keyboard
- [ ] Payment can complete on mobile

**Expected:** Full checkout flow works on mobile

**Result:** ✅ / ❌ (Notes: __________________)

---

## 🐛 TEST #5: Error Handling (2 min)

### 5.1 - Console Check
- [ ] Open DevTools Console (F12 → Console tab)
- [ ] No red error messages
- [ ] No warnings about missing props
- [ ] No CORS errors
- [ ] Network tab shows all requests succeed (200 status)

**Expected:** Clean console, no errors

**Result:** ✅ / ❌ (Errors: __________________)

---

### 5.2 - Performance Check
- [ ] DevTools → Performance tab
- [ ] Click "Record" → Perform test action → Stop
- [ ] Page load time < 3 seconds
- [ ] Interactive elements respond instantly (< 100ms)
- [ ] No layout shifts (Cumulative Layout Shift < 0.1)

**Expected:** Fast, responsive page

**Result:** ✅ / ❌ (Notes: __________________)

---

## 📊 TEST #6: Analytics Events (3 min)

### 6.1 - Console Network Tab
- [ ] Open DevTools → Network tab
- [ ] Clear network history
- [ ] Click oracle button
- [ ] Look for `/api/` or analytics requests
- [ ] Click pack selection
- [ ] Look for tracking events

**Expected:** Events sent to backend/analytics

**Result:** ✅ / ❌ (Events logged: __________________)

---

### 6.2 - localStorage Check
- [ ] Open DevTools → Application → localStorage
- [ ] After pack selection, check for:
  - [ ] `plume_astrale_plan` key with value
  - [ ] `pa_birth_data_v2` key (if form completed)
- [ ] Values are correct JSON

**Expected:** Data persisted correctly in localStorage

**Result:** ✅ / ❌ (Notes: __________________)

---

## ✅ FINAL RESULTS

### Critical Path (Must Pass)
- [ ] **1.1** - Oracle button visible
- [ ] **1.3** - Oracle displays with text
- [ ] **2.2** - Pack 2 highlighted as BESTSELLER
- [ ] **3.1** - Pack selection works
- [ ] **3.3** - Payment completes
- [ ] **4.2** - Mobile responsive

### Success Criteria
- ✅ **PASS:** 6/6 critical tests pass
- ⚠️ **WARN:** 5/6 pass (fix before launch)
- ❌ **FAIL:** <5/6 pass (cannot launch yet)

---

## 🎯 Overall Status

**Date:** 2026-07-11  
**Tester:** ________________  
**Environment:** Local dev  
**Overall Result:** ✅ PASS / ⚠️ WARN / ❌ FAIL

**Critical Issues Found:**
```
1. ________________
2. ________________
3. ________________
```

**Notes & Observations:**
```
________________
________________
________________
```

---

## 🚀 Next Steps

If **✅ PASS:**
→ Move to Priority #4: Add RetentionCTA

If **⚠️ WARN:**
→ Fix issues identified
→ Re-test critical path
→ Escalate to team if needed

If **❌ FAIL:**
→ Debug failing tests
→ Check browser console for errors
→ Verify all imports in NewHome.js
→ Contact dev team

---

## 📞 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Backend not connecting | Check `REACT_APP_BACKEND_URL=http://localhost:8001` |
| QuickOracle not rendering | Verify import in NewHome.js (line 6) |
| Packs not showing | Check CreditsPaywallModal.js PACKS array |
| Stripe error | Use test card: 4242 4242 4242 4242 |
| Mobile not responsive | Clear browser cache (Ctrl+Shift+Delete) |
| Console errors | Open DevTools F12, check for red messages |

