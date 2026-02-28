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
    
    async def get_natal_wheel_chart(self, date_str: str, time_str: str, lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[str]:
        """Get natal wheel chart SVG URL from the API"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("natal_wheel_chart", data)
        if result and result.get('status') and result.get('chart_url'):
            return result['chart_url']
        return None
    
    async def get_moon_phase_report(self) -> Optional[Dict]:
        """Get current moon phase report"""
        data = {}
        return await self._make_request("moon_phase_report", data)
    
    async def get_house_cusps_tropical(self, date_str: str, time_str: str, lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[Dict]:
        """Get detailed house cusps"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        return await self._make_request("house_cusps/tropical", data)
    
    async def get_numerological_numbers(self, date_str: str, time_str: str, name: str = "", lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[Dict]:
        """Get all numerological numbers (lifepath, expression, soul urge, etc.)"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        if name:
            data['name'] = name
        return await self._make_request("numero_table", data)
    
    async def get_natal_chart_interpretation(self, date_str: str, time_str: str, lat: float = 48.8566, lon: float = 2.3522, timezone: float = 1.0) -> Optional[Dict]:
        """Get natal chart interpretation text"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        return await self._make_request("natal_chart_interpretation", data)
    
    async def get_zodiac_compatibility(self, sign1: str, sign2: str) -> Optional[Dict]:
        """Get zodiac compatibility between two signs"""
        data = {"zodiac1": sign1, "zodiac2": sign2}
        return await self._make_request("zodiac_compatibility", data)
    
    async def get_tarot_predictions(self) -> Optional[Dict]:
        """Get tarot card predictions (Growth plan)"""
        return await self._make_request("tarot_predictions", {})
    
    async def get_yes_no_tarot(self) -> Optional[Dict]:
        """Get yes/no tarot reading (Growth plan)"""
        return await self._make_request("yes_no_tarot", {})
    
    @staticmethod
    def get_zodiac_sign_from_date(date_str: str) -> str:
        """Calculate zodiac sign from birth date"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day = date.day
        month = date.month
        
        # Zodiac date ranges (end dates for each sign)
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "aquarius"
        else:
            return "pisces"
    
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
