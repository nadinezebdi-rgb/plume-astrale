import httpx
import base64
import os
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AstrologyAPIService:
    """Service for interacting with AstrologyAPI.com"""
    
    BASE_URL = "https://json.astrologyapi.com/v1"
    
    def __init__(self):
        self.user_id = os.environ.get('ASTROLOGY_API_USER_ID')
        self.api_key = os.environ.get('ASTROLOGY_API_KEY')
        
        if not self.user_id or not self.api_key:
            raise ValueError("ASTROLOGY_API_USER_ID and ASTROLOGY_API_KEY must be set")
        
        # Create Basic Auth header
        credentials = f"{self.user_id}:{self.api_key}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Make a POST request to the API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {str(e)}")
            return None
    
    def _parse_birth_data(self, date_str: str, time_str: str, lat: float, lon: float, timezone: float = 1.0) -> Dict:
        """Parse birth data into API format"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        hour, minute = map(int, time_str.split(":"))
        
        return {
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "hour": hour,
            "min": minute,
            "lat": lat,
            "lon": lon,
            "tzone": timezone
        }
    
    async def get_western_horoscope(self, date_str: str, time_str: str, lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[Dict]:
        """Get western horoscope with planets, houses, and aspects"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        return await self._make_request("western_horoscope", data)
    
    async def get_planets_tropical(self, date_str: str, time_str: str, lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[Dict]:
        """Get tropical planet positions"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        return await self._make_request("planets/tropical", data)
    
    async def get_daily_horoscope(self, zodiac_sign: str, timezone: float = 1.0) -> Optional[Dict]:
        """Get daily horoscope prediction for a zodiac sign"""
        # Valid signs: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces
        zodiac_sign = zodiac_sign.lower()
        data = {"timezone": timezone}
        return await self._make_request(f"sun_sign_prediction/daily/{zodiac_sign}", data)
    
    async def get_weekly_horoscope(self, zodiac_sign: str, timezone: float = 1.0) -> Optional[Dict]:
        """Get weekly horoscope prediction"""
        zodiac_sign = zodiac_sign.lower()
        data = {"timezone": timezone}
        return await self._make_request(f"sun_sign_prediction/weekly/{zodiac_sign}", data)
    
    async def get_monthly_horoscope(self, zodiac_sign: str, timezone: float = 1.0) -> Optional[Dict]:
        """Get monthly horoscope prediction"""
        zodiac_sign = zodiac_sign.lower()
        data = {"timezone": timezone}
        return await self._make_request(f"sun_sign_prediction/monthly/{zodiac_sign}", data)
    
    async def get_geo_details(self, place: str) -> Optional[Dict]:
        """Get latitude, longitude and timezone for a place"""
        # Use just the city name for better results
        city_name = place.split(",")[0].strip()
        data = {"place": city_name, "maxRows": 1}
        result = await self._make_request("geo_details", data)
        
        if result and "geonames" in result and len(result["geonames"]) > 0:
            return result["geonames"]
        return None
    
    @staticmethod
    def get_zodiac_sign_from_date(date_str: str) -> str:
        """Calculate zodiac sign from birth date"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day = date.day
        month = date.month
        
        zodiac_dates = [
            (1, 20, "capricorn"), (2, 19, "aquarius"), (3, 20, "pisces"),
            (4, 20, "aries"), (5, 21, "taurus"), (6, 21, "gemini"),
            (7, 22, "cancer"), (8, 23, "leo"), (9, 23, "virgo"),
            (10, 23, "libra"), (11, 22, "scorpio"), (12, 22, "sagittarius"),
            (13, 0, "capricorn")  # For December 22-31
        ]
        
        for i, (m, d, sign) in enumerate(zodiac_dates):
            if month == m and day <= d:
                return zodiac_dates[i-1][2] if i > 0 else "capricorn"
            elif month < m:
                return zodiac_dates[i-1][2] if i > 0 else "capricorn"
        
        return "sagittarius"
    
    @staticmethod
    def get_zodiac_french_name(sign: str) -> str:
        """Get French name for zodiac sign"""
        names = {
            "aries": "Bélier", "taurus": "Taureau", "gemini": "Gémeaux",
            "cancer": "Cancer", "leo": "Lion", "virgo": "Vierge",
            "libra": "Balance", "scorpio": "Scorpion", "sagittarius": "Sagittaire",
            "capricorn": "Capricorne", "aquarius": "Verseau", "pisces": "Poissons"
        }
        return names.get(sign.lower(), sign)


# Singleton instance
astrology_service = None

def get_astrology_service() -> AstrologyAPIService:
    global astrology_service
    if astrology_service is None:
        astrology_service = AstrologyAPIService()
    return astrology_service
