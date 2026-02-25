"""
Service AstrologyAPI PDF - Professional Horoscope & Match Making
Uses the separate PDF API credentials (pdf.astrologyapi.com)
"""
import os
import base64
import httpx
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

PDF_BASE_URL = "https://pdf.astrologyapi.com/v1"

COMPANY_BRANDING = {
    "footer_link": "plumeastrale.com",
    "logo_url": "",
    "company_name": "Plume Astrale",
    "company_info": "Votre guide spirituel personnalise - Astrologie, Tarot et Mediumnite",
    "domain_url": "https://plumeastrale.com",
    "company_email": "contact@plumeastrale.com",
    "company_landline": "+33 1 00 00 00 00",
    "company_mobile": "+33 6 00 00 00 00",
}


def _get_pdf_auth() -> str:
    user_id = os.environ.get("ASTROLOGY_PDF_USER_ID")
    api_key = os.environ.get("ASTROLOGY_PDF_API_KEY")
    if not user_id or not api_key:
        raise ValueError("ASTROLOGY_PDF_USER_ID and ASTROLOGY_PDF_API_KEY required")
    return base64.b64encode(f"{user_id}:{api_key}".encode()).decode()


async def generate_pro_horoscope_pdf(
    name: str,
    gender: str,
    day: int, month: int, year: int,
    hour: int, minute: int,
    lat: float, lon: float,
    timezone: float,
    place: str,
    language: str = "en"
) -> Optional[str]:
    """Generate a professional horoscope PDF (68 pages) via AstrologyAPI.
    Returns the PDF URL or None on error."""
    
    auth = _get_pdf_auth()
    
    data = {
        "name": name,
        "gender": gender,
        "day": day,
        "month": month,
        "year": year,
        "hour": hour,
        "min": minute,
        "lat": lat,
        "lon": lon,
        "tzone": timezone,
        "place": place,
        "language": language,
        "chart_style": "SOUTH_INDIAN",
        **COMPANY_BRANDING,
    }
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept-Language": language,
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{PDF_BASE_URL}/pro_horoscope_pdf",
                json=data,
                headers=headers,
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("status"):
                    pdf_url = result.get("pdf_url", "")
                    logger.info(f"Pro horoscope PDF generated: {pdf_url}")
                    return pdf_url
                else:
                    logger.error(f"PDF API error: {result.get('msg', 'Unknown error')}")
            else:
                logger.error(f"PDF API HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"PDF API request error: {e}")
    
    return None


async def generate_match_making_pdf(
    male_data: Dict,
    female_data: Dict,
    language: str = "en"
) -> Optional[str]:
    """Generate a match making PDF (24 pages) via AstrologyAPI.
    Returns the PDF URL or None on error."""
    
    auth = _get_pdf_auth()
    
    data = {
        "m_first_name": male_data.get("first_name", ""),
        "m_last_name": male_data.get("last_name", ""),
        "m_day": male_data["day"],
        "m_month": male_data["month"],
        "m_year": male_data["year"],
        "m_hour": male_data["hour"],
        "m_minute": male_data["minute"],
        "m_latitude": male_data["lat"],
        "m_longitude": male_data["lon"],
        "m_timezone": male_data.get("timezone", 1.0),
        "m_place": male_data.get("place", "Paris, France"),
        "f_first_name": female_data.get("first_name", ""),
        "f_last_name": female_data.get("last_name", ""),
        "f_day": female_data["day"],
        "f_month": female_data["month"],
        "f_year": female_data["year"],
        "f_hour": female_data["hour"],
        "f_minute": female_data["minute"],
        "f_latitude": female_data["lat"],
        "f_longitude": female_data["lon"],
        "f_timezone": female_data.get("timezone", 1.0),
        "f_place": female_data.get("place", "Paris, France"),
        "language": language,
        "ashtakoot": True,
        "dashakoot": True,
        "papasamyam": True,
        "chart_style": "SOUTH_INDIAN",
        **COMPANY_BRANDING,
    }
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept-Language": language,
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{PDF_BASE_URL}/match_making_pdf",
                json=data,
                headers=headers,
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("status"):
                    pdf_url = result.get("pdf_url", "")
                    logger.info(f"Match making PDF generated: {pdf_url}")
                    return pdf_url
                else:
                    logger.error(f"Match PDF API error: {result.get('msg', 'Unknown error')}")
            else:
                logger.error(f"Match PDF API HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Match PDF API request error: {e}")
    
    return None
