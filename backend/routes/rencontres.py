"""
Rencontres Astrales — Decodeur du Destin Amoureux.

Free reveal + email capture + one-shot payment (29,99 EUR).

Endpoints :
  POST /api/rencontres/reveal    → portrait du partenaire ideal (public, no auth)
  POST /api/rencontres/capture   → email capture + envoi fenetres de rencontre par mail
  POST /api/rencontres/checkout  → creation session Stripe (produit one-shot 29,99 EUR)
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout,
    CheckoutSessionRequest,
)

from config import get_settings
from services import astrology_io_service as aio
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rencontres", tags=["rencontres"])

# In-memory cache pour lier reveal_id → birth_data (evite de refaire le calcul)
# Prod : a stocker en Redis / Supabase table si besoin persistant
_REVEAL_CACHE: dict[str, dict] = {}


# ────────────────────────────────────────────────────────────────
# Modeles Pydantic
# ────────────────────────────────────────────────────────────────
from pydantic import field_validator, constr


class BirthPayload(BaseModel):
    day: int
    month: int
    year: int
    hour: int = 12
    minute: int = 0
    place: constr(strip_whitespace=True, min_length=2, max_length=80)
    country: Optional[str] = "France"
    first_name: Optional[str] = None
    utm: Optional[dict] = None

    @field_validator("day")
    @classmethod
    def _day(cls, v):
        if v < 1 or v > 31:
            raise ValueError("Le jour doit etre entre 1 et 31.")
        return v

    @field_validator("month")
    @classmethod
    def _month(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Le mois doit etre entre 1 et 12.")
        return v

    @field_validator("year")
    @classmethod
    def _year(cls, v):
        if v < 1900 or v > 2030:
            raise ValueError("L'annee doit etre entre 1900 et 2030.")
        return v

    @field_validator("hour")
    @classmethod
    def _hour(cls, v):
        if v < 0 or v > 23:
            raise ValueError("L'heure doit etre entre 0 et 23.")
        return v

    @field_validator("minute")
    @classmethod
    def _minute(cls, v):
        if v < 0 or v > 59:
            raise ValueError("Les minutes doivent etre entre 0 et 59.")
        return v


class CapturePayload(BaseModel):
    reveal_id: str
    email: EmailStr
    consent_marketing: bool = True
    utm: Optional[dict] = None


class CheckoutPayload(BaseModel):
    origin_url: str
    reveal_id: Optional[str] = None
    email: Optional[EmailStr] = None
    utm: Optional[dict] = None
    promo_code: Optional[str] = None
    # Personne qui t'interesse — REQUIS pour la synastrie 12 domaines
    partner_first_name: Optional[str] = None
    partner_birth_date: Optional[str] = None   # 'YYYY-MM-DD'
    partner_birth_time: Optional[str] = None   # 'HH:MM'
    partner_place: Optional[str] = None


# ────────────────────────────────────────────────────────────────
# Constantes reveal
# ────────────────────────────────────────────────────────────────
SIGN_ELEMENT = {
    "Belier": "Feu", "Taureau": "Terre", "Gemeaux": "Air",
    "Cancer": "Eau", "Lion": "Feu", "Vierge": "Terre",
    "Balance": "Air", "Scorpion": "Eau", "Sagittaire": "Feu",
    "Capricorne": "Terre", "Verseau": "Air", "Poissons": "Eau",
}

# ── Utilitaires UTM (attribution TikTok/social) ────────────────────
_UTM_ALLOWED_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "referrer", "landing_path", "landing_ts",
}


def _sanitize_utm(utm) -> dict:
    """Retourne un dict UTM safe (cles autorisees + valeurs strings <= 250)."""
    if not utm or not isinstance(utm, dict):
        return {}
    out = {}
    for k in _UTM_ALLOWED_KEYS:
        v = utm.get(k)
        if v is None:
            continue
        s = str(v)[:250]
        if s:
            out[k] = s
    return out

# Portrait du partenaire ideal — texte poetique par element de la Maison VII
PARTNER_PORTRAIT_TEMPLATES = {
    "Eau": (
        "Votre Maison VII {article}**{sign}** revele une ame sœur d'une **sensibilite a fleur "
        "de peau**. Cette personne possede une intuition tres developpee, un besoin de connexion "
        "fusionnelle et une profondeur emotionnelle rare. Elle vous accueillera dans l'espace "
        "sacre de ses ressentis les plus intimes. Vous n'etes pas fait(e) pour les amours tiedes : "
        "il vous faut de l'intensite, du silence partage, de la magie du subtil."
    ),
    "Feu": (
        "Votre Maison VII {article}**{sign}** vous designe un partenaire **passionne, "
        "audacieux, magnetique**. Cette personne rayonne d'une chaleur solaire, elle ose, elle "
        "prend des initiatives, elle vous emporte dans son elan. Vous vibrez au contact d'une "
        "flamme qui ne se cache pas. La routine amoureuse vous eteint ; il vous faut un feu "
        "constant, une aventure a co-creer."
    ),
    "Air": (
        "Votre Maison VII {article}**{sign}** dessine un partenaire **cerebral, curieux, "
        "libre**. Cette personne vous stimulera intellectuellement, ouvrira vos horizons, vous "
        "surprendra par son originalite. La conversation profonde est un aphrodisiaque pour "
        "vous. Vous cherchez un complice, un miroir vibrant, un compagnon de voyage plutot qu'un "
        "gardien."
    ),
    "Terre": (
        "Votre Maison VII {article}**{sign}** vous promet une ame sœur **stable, sensuelle, "
        "profondement fiable**. Cette personne construit avec vous quelque chose de durable, "
        "d'incarne, de tangible. Elle n'a pas peur du long terme. Sa presence rassure votre "
        "systeme nerveux ; sa fidelite est une forme d'amour tres precieuse. Vous meritez cet "
        "ancrage."
    ),
}


def _sign_article(sign: str) -> str:
    """Retourne l'article francais approprie devant un signe astro.
    'en signe du Belier' / 'en signe de la Balance' / 'en signe des Poissons'."""
    if not sign:
        return "en signe de "
    articles = {
        "Belier": "du ",
        "Taureau": "du ",
        "Gemeaux": "des ",
        "Cancer": "du ",
        "Lion": "du ",
        "Vierge": "de la ",
        "Balance": "de la ",
        "Scorpion": "du ",
        "Sagittaire": "du ",
        "Capricorne": "du ",
        "Verseau": "du ",
        "Poissons": "des ",
    }
    return "en signe " + articles.get(sign, "de ")


def _find_point(points: list, name: str) -> Optional[dict]:
    """Retourne le dict de la planete/maison si trouvee."""
    for p in points or []:
        if (p.get("name") or "").lower() == name.lower():
            return p
    return None


def _house_seven_sign_fr(natal: dict) -> Optional[str]:
    """Retourne le signe de la Maison VII en francais, ou None."""
    houses = natal.get("houses") or natal.get("house_cusps") or []
    for h in houses:
        num = h.get("house") or h.get("number") or h.get("id")
        if num == 7 or num == "7":
            sign_en = h.get("sign") or h.get("zodiac_sign")
            return aio.sign_to_fr(sign_en) if sign_en else None
    # Fallback : chercher un point "Descendant"
    d = _find_point(natal.get("points") or natal.get("planets") or [], "Descendant")
    if d:
        return aio.sign_to_fr(d.get("sign", ""))
    return None


def _venus_mars_signs_fr(natal: dict) -> tuple[Optional[str], Optional[str]]:
    """Retourne (venus_sign_fr, mars_sign_fr)."""
    pts = natal.get("points") or natal.get("planets") or []
    venus = _find_point(pts, "Venus")
    mars = _find_point(pts, "Mars")
    v = aio.sign_to_fr(venus.get("sign", "")) if venus else None
    m = aio.sign_to_fr(mars.get("sign", "")) if mars else None
    return v, m


# ────────────────────────────────────────────────────────────────
# POST /reveal — revelation immediate (public)
# ────────────────────────────────────────────────────────────────
@router.post("/reveal")
async def reveal(payload: BirthPayload):
    """Genere le portrait du partenaire ideal.
    Le calendrier des rencontres est email-gated (endpoint /capture)."""
    try:
        country_code = (payload.country or "France")[:2].upper() if payload.country else "FR"
        # Normalisation basique
        _country_map = {"FR": "FR", "US": "US", "UK": "GB", "GB": "GB", "BE": "BE", "CH": "CH", "CA": "CA", "MA": "MA", "DZ": "DZ", "TN": "TN"}
        cc = _country_map.get(country_code, "FR")
        bd = aio.make_birth_data(
            year=payload.year,
            month=payload.month,
            day=payload.day,
            hour=payload.hour,
            minute=payload.minute,
            city=payload.place,
            country_code=cc,
        )
    except Exception as e:
        raise HTTPException(400, f"Donnees de naissance invalides : {e}")

    name = payload.first_name or "toi"
    natal = await aio.natal_chart(bd, name=name, language="fr")
    if not natal:
        raise HTTPException(400, "Impossible de calculer votre theme natal. Verifiez la date et le lieu de naissance.")

    m7_sign = _house_seven_sign_fr(natal) or "Balance"
    venus_fr, mars_fr = _venus_mars_signs_fr(natal)

    element = SIGN_ELEMENT.get(m7_sign, "Air")
    portrait_template = PARTNER_PORTRAIT_TEMPLATES.get(element, PARTNER_PORTRAIT_TEMPLATES["Air"])
    portrait = portrait_template.format(sign=m7_sign, article=_sign_article(m7_sign))

    # Petit complement Venus + Mars
    complement = None
    if venus_fr and mars_fr:
        complement = (
            f"Votre Venus en **{venus_fr}** vous rend sensible a {_venus_flavor(venus_fr)}, "
            f"tandis que votre Mars en **{mars_fr}** desire {_mars_flavor(mars_fr)}. "
            "Cette combinaison sculpte votre langage d'amour unique."
        )

    reveal_id = uuid.uuid4().hex
    _REVEAL_CACHE[reveal_id] = {
        "birth_data": bd,
        "first_name": payload.first_name,
        "m7_sign": m7_sign,
        "venus_fr": venus_fr,
        "mars_fr": mars_fr,
        "utm": _sanitize_utm(payload.utm),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Nettoyage cache si trop gros (garde 1000 derniers)
    if len(_REVEAL_CACHE) > 1000:
        for k in list(_REVEAL_CACHE.keys())[:200]:
            _REVEAL_CACHE.pop(k, None)

    return {
        "reveal_id": reveal_id,
        "house7_sign": m7_sign,
        "element": element,
        "portrait": portrait,
        "complement": complement,
        "venus_sign": venus_fr,
        "mars_sign": mars_fr,
        # les fenetres de rencontre sont email-gated
        "next_step": "Debloquez vos 3 fenetres de rencontre precises avec votre email.",
    }


def _venus_flavor(sign: str) -> str:
    m = {
        "Belier": "les elans passionnes, aux jeux de conquete rapides",
        "Taureau": "la douceur sensorielle, aux gestes tendres et durables",
        "Gemeaux": "la conversation vive, aux echanges spirituels",
        "Cancer": "la tendresse protectrice, aux liens intimes profonds",
        "Lion": "la reconnaissance amoureuse, aux gestes theatraux et genereux",
        "Vierge": "les attentions discretes, au service et au raffinement",
        "Balance": "l'harmonie relationnelle, aux beautes partagees",
        "Scorpion": "l'intensite fusionnelle, aux verites qui transforment",
        "Sagittaire": "la liberte partagee, a l'aventure a deux",
        "Capricorne": "la loyaute durable, aux constructions serieuses",
        "Verseau": "la connexion mentale libre, a l'amitie amoureuse",
        "Poissons": "la fusion romantique, a la magie et au reve",
    }
    return m.get(sign, "des vibrations qui vous sont propres")


def _mars_flavor(sign: str) -> str:
    m = {
        "Belier": "conquerir avec fougue",
        "Taureau": "posseder avec patience",
        "Gemeaux": "seduire par la parole",
        "Cancer": "proteger avec tendresse",
        "Lion": "aimer avec panache",
        "Vierge": "servir avec devotion",
        "Balance": "charmer avec elegance",
        "Scorpion": "fusionner avec intensite",
        "Sagittaire": "explorer avec passion",
        "Capricorne": "batir avec constance",
        "Verseau": "surprendre avec liberte",
        "Poissons": "aimer avec compassion",
    }
    return m.get(sign, "aimer a votre facon")


# ────────────────────────────────────────────────────────────────
# POST /capture — email capture + envoi des fenetres par mail
# ────────────────────────────────────────────────────────────────
@router.post("/capture")
async def capture(payload: CapturePayload):
    """Enregistre l'email et renvoie les 3 fenetres de rencontre."""
    ctx = _REVEAL_CACHE.get(payload.reveal_id)
    if not ctx:
        raise HTTPException(410, "Revelation expiree. Reessayez.")

    bd = ctx["birth_data"]
    name = ctx.get("first_name") or "toi"

    # Compute transits today for context (best effort)
    transits = None
    try:
        transits = await aio.transits_today(bd, name=name, language="fr")
    except Exception as e:
        logger.warning(f"[rencontres] transits failed: {e}")

    windows = _synthesize_windows(ctx, transits)

    # Enregistrer le lead
    utm = _sanitize_utm(payload.utm) or ctx.get("utm") or {}
    try:
        sb = get_admin_client()
        sb.table("oracle_leads").upsert({
            "email": payload.email,
            "first_name": ctx.get("first_name"),
            "birth_date": f"{bd['year']:04d}-{bd['month']:02d}-{bd['day']:02d}",
            "source": utm.get("utm_source") or "rencontres_astrales",
            "consent_marketing": payload.consent_marketing,
            "metadata": {
                "campaign": utm.get("utm_campaign"),
                "medium": utm.get("utm_medium"),
                "content": utm.get("utm_content"),
                "term": utm.get("utm_term"),
                "referrer": utm.get("referrer"),
                "landing_path": utm.get("landing_path"),
                "m7_sign": ctx.get("m7_sign"),
            },
        }, on_conflict="email").execute()
    except Exception as e:
        logger.warning(f"[rencontres] lead upsert failed (table may not exist yet): {e}")

    # Envoi email best-effort
    _send_windows_email(payload.email, ctx, windows)

    return {
        "ok": True,
        "windows": windows,
        "email_sent": True,
        "cta": {
            "product": "rencontres_ultime",
            "price": "29,99 €",
            "title": "Guide de Compatibilite Ultime & Calendrier de Rencontres detaille",
            "features": [
                "L'identite astrale complete de ton futur partenaire",
                "Vos 12 points de compatibilite decodes",
                "Le calendrier precis des 6 prochains mois",
                "Les rituels energetiques pour attirer cette relation",
            ],
        },
    }


def _synthesize_windows(ctx: dict, transits: Optional[dict]) -> list[dict]:
    """Retourne 3 fenetres de rencontre plausibles pour les 6 prochains mois."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    months_fr = ["janvier", "fevrier", "mars", "avril", "mai", "juin",
                 "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]

    def m_label(offset_days: int) -> str:
        d = now + timedelta(days=offset_days)
        return months_fr[d.month - 1]

    intensity_by_element = {
        "Eau": "haute intensite emotionnelle",
        "Feu": "explosion romantique passionnee",
        "Air": "connexion intellectuelle fulgurante",
        "Terre": "rencontre stable et incarnee",
    }
    element = SIGN_ELEMENT.get(ctx.get("m7_sign", ""), "Air")

    return [
        {
            "period": f"entre {m_label(20)} et {m_label(45)}",
            "kind": "Fenetre d'ouverture",
            "text": (
                f"Une premiere zone de {intensity_by_element[element]} s'active. "
                "Venus caresse ta carte du ciel et cree des occasions inattendues. "
                "Reste ouvert aux rencontres non planifiees."
            ),
        },
        {
            "period": f"entre {m_label(70)} et {m_label(100)}",
            "kind": "Fenetre de synchronicite",
            "text": (
                "Un mouvement de Jupiter reveille ta Maison VII : une personne significative "
                "peut entrer dans ton champ. Coincidences, retrouvailles, connexions karmiques."
            ),
        },
        {
            "period": f"entre {m_label(130)} et {m_label(160)}",
            "kind": "Fenetre de destin",
            "text": (
                "Un transit majeur active tes points d'amour. C'est LA fenetre a ne pas manquer. "
                "Prepare ton cœur, rends-toi disponible, et laisse la magie faire le reste."
            ),
        },
    ]


def _send_windows_email(email: str, ctx: dict, windows: list[dict]) -> None:
    """Envoi Resend best-effort."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        logger.warning("[rencontres] RESEND_API_KEY missing, skipping email")
        return
    try:
        import httpx
        html_windows = "".join([
            f"<div style='margin:16px 0;padding:16px;border-left:3px solid #C5A059;"
            f"background:rgba(197,160,89,0.06);'>"
            f"<div style='font-size:11px;letter-spacing:0.2em;text-transform:uppercase;"
            f"color:#C5A059;'>{w['kind']}</div>"
            f"<div style='font-family:Cormorant Garamond,serif;font-size:20px;margin-top:4px;"
            f"color:#0C0918;'>Fenetre {w['period']}</div>"
            f"<p style='margin-top:8px;color:#333;font-size:14px;line-height:1.6;'>{w['text']}</p>"
            f"</div>"
            for w in windows
        ])
        html = f"""
        <div style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:32px;background:#fff;color:#0C0918;">
          <!-- Header Solena -->
          <div style="text-align:center;margin-bottom:24px;">
            <img src="https://plume-astrale.fr/brand/solena.png" alt="Solena"
                 width="72" height="72"
                 style="border-radius:50%;object-fit:cover;object-position:center 22%;border:2px solid #C5A059;" />
            <div style="margin-top:8px;font-size:11px;letter-spacing:0.25em;text-transform:uppercase;color:#C5A059;">
              De Solena · Plume Astrale
            </div>
          </div>

          <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#0C0918;">
            Tes fenetres de rencontre sont ouvertes.
          </h1>
          <p style="color:#555;line-height:1.6;">
            Plume a decode ton ciel des 6 prochains mois. Voici les 3 zones ou l'univers
            joue pour toi en matiere d'amour :
          </p>
          {html_windows}
          <div style="margin-top:32px;padding:24px;background:#0C0918;color:#F4E8D2;border-radius:16px;text-align:center;">
            <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#C5A059;">
              Aller plus loin
            </div>
            <h2 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:24px;margin-top:8px;">
              Guide de Compatibilite Ultime & Calendrier de Rencontres
            </h2>
            <div style="font-size:14px;line-height:1.6;color:#F4E8D2;opacity:0.85;margin-top:12px;">
              15 pages d'analyse holistique · L'identite astrale complete de ton futur partenaire ·
              Le calendrier precis des 6 prochains mois · Les rituels energetiques a activer.
            </div>
            <div style="margin-top:20px;">
              <a href="https://plume-astrale.fr/rencontres-astrales?buy=1"
                 style="display:inline-block;padding:14px 28px;background:#C5A059;color:#0C0918;
                        text-decoration:none;border-radius:999px;font-size:12px;letter-spacing:0.2em;
                        text-transform:uppercase;font-weight:600;">
                Reveler mon guide · 29,99 €
              </a>
            </div>
          </div>

          <!-- Signature -->
          <div style="margin-top:32px;padding-top:24px;border-top:1px solid #eee;text-align:center;font-size:12px;color:#888;line-height:1.6;">
            <div style="font-family:'Cormorant Garamond',serif;font-size:18px;color:#0C0918;font-style:italic;">
              — Solena
            </div>
            <div style="margin-top:4px;">Astrologue &amp; guide chez Plume Astrale</div>
            <div style="margin-top:8px;font-size:10px;letter-spacing:0.1em;color:#aaa;">
              <a href="https://plume-astrale.fr/solena" style="color:#C5A059;text-decoration:none;">plume-astrale.fr/solena</a>
            </div>
          </div>
        </div>
        """
        with httpx.Client(timeout=15) as client:
            client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "from": "Solena · Plume Astrale <contact@plume-astrale.fr>",
                    "to": [email],
                    "subject": "Tes 3 fenetres de rencontre sont ouvertes",
                    "html": html,
                },
            )
    except Exception as e:
        logger.warning(f"[rencontres] email send failed: {e}")


# ────────────────────────────────────────────────────────────────
# POST /checkout — Stripe one-shot 29,99 EUR
# ────────────────────────────────────────────────────────────────
@router.post("/checkout")
async def rencontres_checkout(payload: CheckoutPayload, request: Request):
    settings = get_settings()
    pack = settings.PACKS.get("rencontres_ultime")
    if not pack:
        raise HTTPException(500, "Produit indisponible.")

    # ── Donnees du partenaire REQUISES (synastrie 12 domaines de vie) ──
    if not (payload.partner_first_name or "").strip():
        raise HTTPException(400, "Le prenom de la personne qui t'interesse est requis.")
    if not payload.partner_birth_date:
        raise HTTPException(400, "La date de naissance de l'autre personne est requise.")
    try:
        py, pm, pd = payload.partner_birth_date[:10].split("-")
        ph, pmi = (payload.partner_birth_time or "12:00")[:5].split(":")
        partner_birth_data = aio.make_birth_data(
            year=int(py), month=int(pm), day=int(pd),
            hour=int(ph), minute=int(pmi),
            city=(payload.partner_place or "Paris").split(",")[0].strip(),
            country_code="FR",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Date de naissance du partenaire invalide (format AAAA-MM-JJ).")

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip("/")
    success_url = f"{origin}/rencontres-astrales/succes?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/rencontres-astrales"

    # Merge UTM du payload avec celui capture au reveal (first-touch)
    utm = _sanitize_utm(payload.utm)
    reveal_ctx = None
    if payload.reveal_id:
        reveal_ctx = _REVEAL_CACHE.get(payload.reveal_id)
        if reveal_ctx and reveal_ctx.get("utm"):
            for k, v in reveal_ctx["utm"].items():
                utm.setdefault(k, v)

    # Extraire les donnees du reveal pour la generation PDF post-webhook
    pdf_ctx = {}
    if reveal_ctx:
        bd = reveal_ctx.get("birth_data") or {}
        pdf_ctx = {
            "first_name": reveal_ctx.get("first_name") or "",
            "m7_sign": reveal_ctx.get("m7_sign") or "",
            "venus_sign": reveal_ctx.get("venus_fr") or "",
            "mars_sign": reveal_ctx.get("mars_fr") or "",
            "user_birth_data": bd if isinstance(bd, dict) else {},
            # birth date au format ISO pour le PDF
            "birth_date_iso": f"{bd.get('year','1990')}-{str(bd.get('month','1')).zfill(2)}-{str(bd.get('day','1')).zfill(2)}"
                              if isinstance(bd, dict) else "",
        }
    pdf_ctx["partner"] = {
        "first_name": payload.partner_first_name.strip(),
        "birth_data": partner_birth_data,
        "birth_date_iso": payload.partner_birth_date[:10],
    }

    # ─────────────────────────────────────────────────────────────
    # BYPASS PROMO — si code valide (ex: ADMIN26), on saute Stripe
    # ─────────────────────────────────────────────────────────────
    from services.promo_bypass import try_consume_promo
    from services.rencontres_ultime_service import handle_rencontres_ultime_webhook
    import asyncio as _asyncio
    if payload.promo_code and try_consume_promo(payload.promo_code):
        fake_session_id = f"admin-rencontres-{uuid.uuid4().hex[:16]}"
        try:
            sb = get_admin_client()
            sb.table("payment_transactions").insert({
                "session_id": fake_session_id,
                "user_email": payload.email or "",
                "pack_id": "rencontres_ultime",
                "amount": 0.0,
                "currency": pack["currency"],
                "credits": 0,
                "status": "completed",
                "payment_status": "paid",
                "credits_granted": True,
                "metadata": {
                    "product": "rencontres_ultime",
                    "kind": "rencontres_ultime",
                    "reveal_id": payload.reveal_id,
                    "pdf_ctx": pdf_ctx,
                    "utm": utm,
                    "admin_bypass": True,
                    "promo_code": payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f"[rencontres] admin bypass tx insert failed: {e}")

        _asyncio.create_task(handle_rencontres_ultime_webhook(fake_session_id))
        success_bypass_url = f"{origin}/rencontres-astrales/succes?session_id={fake_session_id}"
        return {"url": success_bypass_url, "session_id": fake_session_id, "admin_bypass": True}

    req = CheckoutSessionRequest(
        amount=float(pack["amount"]),
        currency=pack["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product": "rencontres_ultime",
            "kind": "rencontres_ultime",   # discriminator pour le webhook
            "reveal_id": payload.reveal_id or "",
            "email": payload.email or "",
            # Attribution — Stripe limite chaque valeur a 500 chars
            "utm_source":   (utm.get("utm_source") or "")[:100],
            "utm_medium":   (utm.get("utm_medium") or "")[:100],
            "utm_campaign": (utm.get("utm_campaign") or "")[:100],
            "utm_content":  (utm.get("utm_content") or "")[:100],
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table("payment_transactions").insert({
            "session_id": session.session_id,
            "user_email": payload.email,
            "pack_id": "rencontres_ultime",
            "amount": float(pack["amount"]),
            "currency": pack["currency"],
            "credits": 0,
            "status": "initiated",
            "payment_status": "unpaid",
            "credits_granted": False,
            "metadata": {
                "product": "rencontres_ultime",
                "kind": "rencontres_ultime",
                "reveal_id": payload.reveal_id,
                "utm": utm,
                "pdf_ctx": pdf_ctx,   # sert au webhook pour generer le PDF
            },
        }).execute()
    except Exception as e:
        logger.warning(f"[rencontres] payment_transactions insert failed: {e}")

    return {"url": session.url, "session_id": session.session_id}


# ────────────────────────────────────────────────────────────────
# GET /ultime/status?session_id=… — Polling par la page de succes
# Retourne le stade de traitement post-paiement (rassure le client).
# ────────────────────────────────────────────────────────────────
@router.get("/ultime/status")
async def rencontres_ultime_status(session_id: str):
    """Retourne le stade actuel du pipeline post-paiement rencontres_ultime.

    Stades possibles :
      - 'pending'    : paiement non confirme (webhook Stripe pas encore reçu)
      - 'generating' : PDF en cours de generation
      - 'emailing'   : PDF genere, email en cours d'envoi
      - 'delivered'  : tout ok, PDF + email envoyes
      - 'error'      : session inconnue
    """
    if not session_id:
        return {"stage": "error", "message": "session_id manquant"}

    try:
        sb = get_admin_client()
        r = sb.table("payment_transactions").select(
            "status,payment_status,metadata,user_email"
        ).eq("session_id", session_id).maybe_single().execute()
        if not r or not r.data:
            return {"stage": "error", "message": "Session introuvable"}

        tx = r.data
        md = tx.get("metadata") or {}

        # Paiement pas encore confirme
        if tx.get("status") != "completed" or tx.get("payment_status") != "paid":
            return {"stage": "pending", "message": "Confirmation du paiement en cours…"}

        pdf_path = md.get("pdf_path")
        email_sent = md.get("email_sent_at")

        if not pdf_path:
            return {"stage": "generating", "message": "Ton Guide de Compatibilité Ultime est en train d'être généré…"}
        if not email_sent:
            return {
                "stage": "emailing",
                "message": "Envoi de l'email en cours…",
                "pdf_url": pdf_path,
            }
        return {
            "stage": "delivered",
            "message": "Ton PDF t'a été envoyé — vérifie ta boîte mail !",
            "pdf_url": pdf_path,
            "email": tx.get("user_email"),
        }
    except Exception as e:
        logger.warning(f"[rencontres] status polling error: {e}")
        return {"stage": "error", "message": "Une petite perturbation cosmique — réessaie dans un instant."}
