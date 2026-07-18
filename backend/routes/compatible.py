"""
Endpoints pour la compatibilité amoureuse et le texte mystérieux.
- /api/couple/mystery - Génère un texte mystérieux basé sur les prénoms (gratuit, OpenAI)
- /api/couple/compatibility - Étude complète de compatibilité (payant, AstrologyIO)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from middleware.auth import get_optional_user
from services.couple_mystery_service import (
    generate_couple_mystery_text,
    generate_couple_detailed_analysis,
    get_fallback_text
)
from services import wallet_service
from services.compatibility_pdf_generator import generate_compatibility_pdf
from services.astrology_io_service import (
    make_birth_data, synastry_chart, relationship_compatibility_score
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/couple', tags=['couple'])


class MysteryRequest(BaseModel):
    """Requête pour générer le texte mystérieux."""
    prenom1: str
    prenom2: str


class CompatibilityRequest(BaseModel):
    """Requête pour l'étude de compatibilité."""
    prenom1: str
    prenom2: str
    birth_date1: str  # YYYY-MM-DD
    birth_time1: str  # HH:MM
    birth_place1: str
    birth_country1: str
    
    birth_date2: str  # YYYY-MM-DD
    birth_time2: str  # HH:MM
    birth_place2: str
    birth_country2: str
    
    email: str
    language: str = "fr"


@router.post("/mystery")
async def get_couple_mystery(request: MysteryRequest):
    """
    Génère une analyse détaillée et pédagogique basée sur les prénoms.
    GRATUIT - utilise OpenAI + calcul numérologique + astrology-api.io en backend.
    Retourne une analyse markdown formatée prête pour affichage.
    """
    try:
        prenom1 = request.prenom1.strip()
        prenom2 = request.prenom2.strip()
        
        if not prenom1 or not prenom2:
            raise HTTPException(status_code=400, detail="Les deux prénoms sont requis")
        
        if len(prenom1) > 50 or len(prenom2) > 50:
            raise HTTPException(status_code=400, detail="Prénoms trop longs")
        
        # Génère analyse détaillée (numérologie + OpenAI)
        analysis = await generate_couple_detailed_analysis(prenom1, prenom2)
        logger.info(f"[couple/mystery] Analysis result: {analysis}")
        
        # Fallback si tout échoue
        if not analysis or not analysis.get("mystery_text"):
            logger.warning(f"[couple/mystery] Analysis was empty or missing mystery_text, using fallback")
            mystery_text = get_fallback_text(prenom1, prenom2)
            analysis = {
                "prenom1": prenom1,
                "prenom2": prenom2,
                "mystery_text": mystery_text,
            }
        
        return {
            "prenom1": analysis.get("prenom1"),
            "prenom2": analysis.get("prenom2"),
            "text": analysis.get("mystery_text"),
            "compatibility_number": analysis.get("compatibility_number"),
            "universal_year": analysis.get("universal_year"),
            "letters_prenom1": analysis.get("letters_prenom1"),
            "letters_prenom2": analysis.get("letters_prenom2"),
            "total_letters": analysis.get("total_letters"),
            "year": analysis.get("year"),
            "interpretation": analysis.get("interpretation", {}),
            "numerology_1": analysis.get("numerology_1", {}),
            "numerology_2": analysis.get("numerology_2", {}),
            "compatibility": analysis.get("compatibility", {}),
            "personal_year": analysis.get("personal_year"),
            "cta_label": "Découvrir la Synastrie Complète",
            "cta_link": f"/outils/compatibilite?p1={prenom1}&p2={prenom2}"
        }
        
    except Exception as e:
        logger.error(f"[couple/mystery] error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération")


@router.post("/compatibility/preview")
async def get_compatibility_preview(request: CompatibilityRequest, current_user = Depends(get_optional_user)):
    """
    Génère un aperçu de compatibilité avec les calculs AstrologyIO.
    Coût: 5 crédits ou accès premium.
    """
    try:
        # Vérifier les crédits si utilisateur authentifié
        if current_user:
            user_credits = await wallet_service.get_balance(current_user['user_id'])
            if user_credits < 5:
                raise HTTPException(
                    status_code=402,
                    detail=f"Crédits insuffisants (besoin: 5, possédé: {user_credits})"
                )
        else:
            # Non authentifié = proposition de paiement
            raise HTTPException(
                status_code=401,
                detail="Authentification requise pour l'étude complète"
            )
        
        # Déduire les crédits
        await wallet_service.deduct_credits(
            current_user['user_id'],
            5,
            reason="compatibility_study",
            metadata={"prenom1": request.prenom1, "prenom2": request.prenom2}
        )
        
        # Générer le PDF de compatibilité
        pdf_buffer = await generate_compatibility_pdf({
            "prenom": request.prenom1,
            "birth_date": request.birth_date1,
            "birth_time": request.birth_time1,
            "birth_place": request.birth_place1,
            "birth_country": request.birth_country1,
        }, {
            "prenom": request.prenom2,
            "birth_date": request.birth_date2,
            "birth_time": request.birth_time2,
            "birth_place": request.birth_place2,
            "birth_country": request.birth_country2,
        })
        
        return {
            "status": "success",
            "message": "Étude de compatibilité générée",
            "credits_deducted": 5,
            "pdf_ready": True
        }
        
    except Exception as e:
        logger.error(f"[couple/compatibility] error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
