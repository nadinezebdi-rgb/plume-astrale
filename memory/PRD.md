# Plume Astrale - PRD

## Date: 02 Mars 2026

## Produit
Espace digital de guidance symbolique, alliant calculs astrologiques precis et interpretation experte.

## Domaine
https://plume-astrale.fr

## Direction Artistique (v3)
- Fond violet profond (#0C0918) avec etoiles scintillantes et orbes
- Ecriture doree (#C5A059), headings (#F0E6D3)
- Typo: Cormorant Garamond (headings), DM Sans (body)
- Code Promo: PLUME2026

## Tech Stack
- Frontend: React, React Router, TailwindCSS, Lucide React, react-helmet-async
- Backend: FastAPI (Python), reportlab (PDF), emergentintegrations (LLM + Stripe)
- APIs: AstrologyAPI (Growth Plan), Emergent LLM (gpt-4o-mini)
- Paiement: Stripe
- Deploiement: Docker Compose, Nginx

## AstrologyAPI Growth Plan
- **Disponible**: western_horoscope, planets/tropical, daily/weekly/monthly horoscope, geo_details, natal_wheel_chart, house_cusps, tarot_predictions, yes_no_tarot
- **Bloque (plan superieur)**: numero_table, natal_chart_interpretation, match_making, current_transit, general_ascendant_report

## Completed
1. PDF Theme Astral Pro 28+ pages
2. Carte Astrale Partageable PNG
3. Integration AstrologyAPI Phase 1
4. Flux Tarot Oui/Non (3 tirages gratuits)
5. Numerologie + Traduction IA (local, API bloquee)
6. Code Promo PLUME2026 toutes pages
7. Refonte design editoriale complete (violet/dore/etoiles)
8. Experience Premium 199 EUR (parcours guide 5 etapes + PDF)
9. SEO Complet (meta tags, sitemap, robots.txt, JSON-LD, OG)
10. **Integration Growth Plan AstrologyAPI** (02 Mars 2026):
    - Tarot Oui/Non: utilise l'API yes_no_tarot avec traduction FR (fallback local)
    - Predictions Tarot: endpoint /api/tarot/predictions (amour, carriere, finances)
    - Section "Vos predictions du jour" ajoutee sur la page Tarologie

## Backlog
### P1
- [ ] Integration emails (SendGrid/Resend/Brevo) — capture leads + envoi PDF
- [ ] Endpoints Growth AstrologyAPI avances (bloque par plan superieur: numero_table, match_making, current_transit)

### P2
- [ ] Abonnement Stripe 14,99 EUR/mois (contenu recurrent)
- [ ] Tableau de bord admin

### P3
- [ ] Emails automatiques relance
- [ ] Blog SEO (horoscope mensuel, articles numerologie)
- [ ] React Context pour etat global
