"""
lead_magnet_pdf — Aperçu 5 pages personnalisé "Thème Natal" offert à l'inscription.

Composé avec la voix Nocturne Éditorial (aucun mot déterministe).
Endpoint public : `/api/lead-magnet/generate` (email + prenom + birth_date [+ birth_time, birth_place]).
PDF envoyé par Resend + URL retournée pour téléchargement immédiat.

Non-personnalisé au niveau planétaire précis (pas d'appel API astrologie coûteux) —
un mois offert, une lecture littéraire, une invitation vers le Thème Natal complet 39€.
"""
from __future__ import annotations
import io
import logging
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, planet_analysis_page, emotional_ending,
)

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'
LEAD_DIR = ASSETS_DIR / 'lead_magnet'
LEAD_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# Soleil ~ signe (basé sur date de naissance, tropical Sun sign)
# Pas d'appel API : c'est un aperçu, pas la lecture complète.
# ─────────────────────────────────────────────────────────────
_SUN_SIGN_DATES = [
    ((3, 21), (4, 19), 'Bélier'),
    ((4, 20), (5, 20), 'Taureau'),
    ((5, 21), (6, 20), 'Gémeaux'),
    ((6, 21), (7, 22), 'Cancer'),
    ((7, 23), (8, 22), 'Lion'),
    ((8, 23), (9, 22), 'Vierge'),
    ((9, 23), (10, 22), 'Balance'),
    ((10, 23), (11, 21), 'Scorpion'),
    ((11, 22), (12, 21), 'Sagittaire'),
    ((12, 22), (1, 19), 'Capricorne'),
    ((1, 20), (2, 18), 'Verseau'),
    ((2, 19), (3, 20), 'Poissons'),
]


def _sun_sign(birth_date_iso: str) -> str:
    try:
        d = datetime.fromisoformat(birth_date_iso[:10]).date()
    except Exception:
        return 'Poissons'
    m, day = d.month, d.day
    for (s_m, s_d), (e_m, e_d), sign in _SUN_SIGN_DATES:
        if s_m == e_m:
            if m == s_m and s_d <= day <= e_d:
                return sign
        elif s_m > e_m:  # traverse janvier (Capricorne)
            if (m == s_m and day >= s_d) or (m == e_m and day <= e_d):
                return sign
        else:
            if (m == s_m and day >= s_d) or (m == e_m and day <= e_d):
                return sign
    return 'Poissons'


# ─────────────────────────────────────────────────────────────
# Narration Nocturne Éditorial — 12 luminaires solaires
# ─────────────────────────────────────────────────────────────
_SUN_NARRATIVES = {
    'Bélier': "Vous portez une clarté franche — un feu qui décide avant que le doute n'ait fini sa phrase. Ce qui vous traverse cherche moins la permission que le mouvement.",
    'Taureau': "Vous habitez le monde par les sens. Ce qui vous traverse cherche la matière, la durée, la texture — jamais la promesse rapide.",
    'Gémeaux': "Deux voix respirent en vous, et c'est ce qui vous rend vivant. Ce qui vous traverse en ce moment vous demande de choisir laquelle mérite le silence.",
    'Cancer': "Vous portez une mémoire fine — celle des lieux, des saisons, des visages. Ce qui vous traverse revient d'un endroit ancien, et ce n'est pas une régression.",
    'Lion': "Vous êtes fait pour être vu — mais seulement par ce que vous choisissez de montrer. Ce qui vous traverse teste votre rapport à votre propre lumière.",
    'Vierge': "Vous voyez ce que les autres survolent. Ce qui vous traverse vous demande d'accueillir l'imperfection sans en faire une erreur.",
    'Balance': "Vous êtes un lieu de rencontre — l'endroit où deux choses opposées trouvent une manière de coexister. Ce qui vous traverse veut de la justesse, pas de la vitesse.",
    'Scorpion': "Vous transformez tout ce que vous regardez longtemps. Ce qui vous traverse en ce moment est une mue — pas une crise.",
    'Sagittaire': "Vous cherchez toujours une phrase plus grande que celle du jour. Ce qui vous traverse vous propose un déplacement — intérieur ou géographique.",
    'Capricorne': "Vous construisez lentement, et le temps travaille pour vous. Ce qui vous traverse consolide plus qu'il ne renverse.",
    'Verseau': "Vous appartenez à demain. Ce qui vous traverse vous invite à traduire votre vision dans le langage d'aujourd'hui.",
    'Poissons': "Vous êtes traversé par des choses que le mental n'attrape pas encore. Ce qui vous traverse demande à être écouté avant d'être expliqué.",
}


# ─────────────────────────────────────────────────────────────
# Saison intérieure — variation par mois calendaire
# ─────────────────────────────────────────────────────────────
_MONTH_SEASONS = {
    1: ("La saison du seuil", "Janvier vous demande de fermer sans claquer la porte. Ce qui s'est achevé mérite un mot, une lettre, une soirée."),
    2: ("La saison du silence habité", "Février creuse en vous une chambre plus profonde. Ce qui a besoin de mûrir doit d'abord se taire."),
    3: ("La saison de l'élan retenu", "Mars vous appelle dehors, mais votre corps veut encore l'intérieur. Écoutez ce désaccord — il est fertile."),
    4: ("La saison du réveil clair", "Avril éclaircit ce que l'hiver avait obscurci. Ce qui vous traverse s'écrit lisiblement pour la première fois."),
    5: ("La saison de la floraison lente", "Mai vous offre le temps d'apprécier. Ce qui vous arrive maintenant sait durer."),
    6: ("La saison du plein éclat", "Juin porte votre projet au grand jour. Ce que vous osez maintenant sera lu par d'autres."),
    7: ("La saison du souffle long", "Juillet vous invite à ralentir sans vous absenter. Ce qui vous traverse veut du corps, pas des idées."),
    8: ("La saison du désir mûr", "Août révèle ce que vous voulez vraiment — pas ce que vous croyez devoir vouloir."),
    9: ("La saison de la clarté rentrée", "Septembre relit l'été et en tire l'enseignement. Ce qui vous traverse s'organise."),
    10: ("La saison du dépouillement", "Octobre vous délivre d'un poids que vous portiez sans le nommer. Ce qui tombe fait de la place."),
    11: ("La saison de l'intériorité", "Novembre creuse un puits en vous. Ce qui vous traverse vient d'un endroit qui n'a pas encore de mots."),
    12: ("La saison de la relecture", "Décembre relit l'année entière. Ce qui vous traverse vous demande de nommer ce que vous emportez."),
}


def _first_name_clean(name: str) -> str:
    name = (name or '').strip()
    if not name:
        return 'ami·e'
    # Capitalize first letter of each word, keep unicode
    return ' '.join(w.capitalize() for w in re.split(r'\s+', name) if w)


def build_lead_magnet_pdf(
    email: str,
    first_name: str,
    birth_date_iso: str,
    birth_time: Optional[str] = None,
    birth_place: Optional[str] = None,
) -> bytes:
    """Construit l'aperçu 5 pages personnalisé au prénom + Soleil.

    Args:
        email: adresse email (pour signature colophon)
        first_name: prénom de l'utilisateur
        birth_date_iso: 'YYYY-MM-DD'
        birth_time: 'HH:MM' (optionnel, non utilisé au niveau planétaire)
        birth_place: ville (optionnel, pour poésie de la couverture)

    Returns:
        PDF bytes (5 pages).
    """
    prenom = _first_name_clean(first_name)
    sun = _sun_sign(birth_date_iso)
    now = datetime.now(timezone.utc)
    season_title, season_body = _MONTH_SEASONS.get(now.month, _MONTH_SEASONS[1])

    subtitle_line = "Aperçu de votre lecture — 5 pages"
    if birth_place:
        subtitle_line = f"Aperçu — {birth_place}"

    buf = io.BytesIO()
    doc = build_luxury_doc(buf, title=f'Aperçu Thème Natal — {prenom}')
    styles = luxury_styles()
    story = []

    # ─── Page 1 : Couverture personnalisée ───
    cover_page(
        story, styles,
        prenom=prenom,
        subtitle=subtitle_line,
        illustration_slug='ciel_zodiaque',
    )

    # ─── Page 2 : Ouverture — trois luminaires ───
    opening_page(
        story, styles,
        prenom=prenom,
        first_line=f"{prenom}, votre ciel est un texte — voici les trois premiers mots.",
    )

    # ─── Page 3 : Soleil narré (l'essence) ───
    planet_analysis_page(
        story, styles,
        planet_name='Votre Soleil',
        sign=sun,
        body_html=(
            f"<b>{_SUN_NARRATIVES.get(sun, _SUN_NARRATIVES['Poissons'])}</b>"
            "<br/><br/>"
            "Le Soleil, dans votre ciel, ne dit pas ce que vous êtes de façon figée — "
            "il dit ce qui rayonne en vous quand vous cessez de vous excuser d'exister. "
            "C'est le premier des trois luminaires. Il y en a deux autres qui vous attendent : "
            "la Lune (votre monde intérieur) et l'Ascendant (la manière dont vous entrez "
            "dans une pièce)."
            "<br/><br/>"
            "<i>Dans votre Thème Natal complet, ce chapitre s'étend sur quatre pages, et onze "
            "autres luminaires vous attendent — chacun avec sa saison propre.</i>"
        ),
        dialogue_question="Qu'est-ce qui rayonne en vous quand personne ne vous regarde ?",
    )

    # ─── Page 4 : Saison intérieure (transit du mois) ───
    planet_analysis_page(
        story, styles,
        planet_name='Votre saison',
        sign=season_title,
        body_html=(
            f"<b>{season_body}</b>"
            "<br/><br/>"
            f"En ce mois de {['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][now.month-1]}, "
            "ce que vous traversez appartient à cette saison précise du ciel. Ce n'est pas une "
            "prédiction — c'est une lecture. Une manière de nommer ce qui bouge sans le forcer à "
            "prendre une forme prématurée."
            "<br/><br/>"
            "<i>Dans votre lecture complète, cette saison se décline sur les douze prochains mois — "
            "avec vos points d'inflexion personnels et les mois où votre ciel s'ouvre plus large.</i>"
        ),
        dialogue_question="Quelle est la couleur, la matière, le son de ce mois pour vous ?",
    )

    # ─── Page 5 : Invitation littéraire — épilogue ───
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
# Email delivery via Resend — best-effort, retourne None si KO
# ─────────────────────────────────────────────────────────────
async def send_lead_magnet_email(
    email: str,
    first_name: str,
    pdf_link: str,
) -> Optional[int]:
    """Envoie l'aperçu par email (lien de téléchargement). Non bloquant."""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    if not api_key:
        logger.warning("[lead_magnet] RESEND_API_KEY missing, email skipped")
        return None
    if not pdf_link:
        return None

    fn = _first_name_clean(first_name)
    subject = f"{fn}, votre aperçu Nocturne vous attend"
    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Fraunces',Georgia,serif;color:#F5F0E6;background:#0B1A2E;padding:48px 32px;">
      <div style="text-align:center;margin-bottom:32px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:0.32em;text-transform:uppercase;color:#B8935A;">
          Acte I &middot; Le Seuil
        </div>
      </div>
      <div style="background:#141B2E;border:1px solid rgba(184,147,90,0.22);border-radius:4px;padding:40px 32px;">
        <h1 style="font-family:'Fraunces',Georgia,serif;font-weight:400;font-size:32px;color:#F5F0E6;margin:0 0 20px;line-height:1.15;letter-spacing:-0.02em;">
          {fn},<br>
          <em style="color:#B8935A;font-style:italic;font-weight:300;">votre aperçu</em><br>vous attend.
        </h1>
        <hr style="border:0;border-top:1px solid #B8935A;width:48px;margin:24px 0;">
        <p style="font-family:'Inter Tight','Inter',sans-serif;color:rgba(245,240,230,0.86);line-height:1.65;font-size:15px;">
          Cinq pages composées pour vous seul(e) — votre Soleil, la saison que vous traversez,
          une invitation. Ce n'est pas une lecture entière : c'est une porte entrebâillée.
        </p>
        <div style="text-align:center;margin:40px 0 12px;">
          <a href="{pdf_link}"
             style="display:inline-block;padding:16px 32px;background:#B8935A;color:#0B1A2E;text-decoration:none;border-radius:2px;font-family:'Inter Tight','Inter',sans-serif;font-size:13px;letter-spacing:0.05em;font-weight:500;">
            Recevoir mon aperçu
          </a>
        </div>
        <p style="font-family:'Inter Tight',sans-serif;font-size:12px;color:rgba(245,240,230,0.5);text-align:center;font-style:italic;margin-top:8px;">
          Ce document reste accessible à ce lien.
        </p>
        <div style="margin-top:40px;padding-top:24px;border-top:1px solid rgba(184,147,90,0.18);text-align:center;">
          <div style="font-family:'Fraunces',Georgia,serif;font-style:italic;color:#F5F0E6;font-size:20px;font-weight:300;">— Soléna</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.28em;color:rgba(184,147,90,0.7);margin-top:8px;text-transform:uppercase;">
            Édition Nocturne &middot; 2026
          </div>
        </div>
      </div>
    </div>
    """

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [email], 'subject': subject, 'html': html},
            )
            if r.status_code >= 400:
                logger.warning(f"[lead_magnet] Resend {r.status_code}: {r.text[:200]}")
            return r.status_code
    except Exception as e:
        logger.warning(f"[lead_magnet] email error: {e}")
        return None
