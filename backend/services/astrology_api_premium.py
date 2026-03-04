"""
Service d'intégration Astrology API - Plan Growth
Endpoints Premium pour Plume Astrale
"""
import httpx
import base64
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AstrologyAPIPremium:
    """
    Service Premium pour AstrologyAPI.com - Plan Growth
    Intègre tous les endpoints avancés pour les produits Premium
    """
    
    BASE_URL = "https://json.astrologyapi.com/v1"
    
    def __init__(self):
        self.user_id = os.environ.get('ASTROLOGY_API_USER_ID')
        self.api_key = os.environ.get('ASTROLOGY_API_KEY')
        
        if not self.user_id or not self.api_key:
            logger.warning("ASTROLOGY_API credentials not set - using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
            credentials = f"{self.user_id}:{self.api_key}"
            self.auth_header = base64.b64encode(credentials.encode()).decode()
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Make a POST request to the API"""
        if self.mock_mode:
            return self._get_mock_response(endpoint, data)
        
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
    
    def _parse_dual_birth_data(self, person1: Dict, person2: Dict) -> Dict:
        """Parse birth data for two persons (compatibility/synastry)"""
        p1 = self._parse_birth_data(
            person1['date'], person1['time'],
            person1['lat'], person1['lon'],
            person1.get('timezone', 1.0)
        )
        p2 = self._parse_birth_data(
            person2['date'], person2['time'],
            person2['lat'], person2['lon'],
            person2.get('timezone', 1.0)
        )
        
        return {
            "p_day": p1["day"], "p_month": p1["month"], "p_year": p1["year"],
            "p_hour": p1["hour"], "p_min": p1["min"],
            "p_lat": p1["lat"], "p_lon": p1["lon"], "p_tzone": p1["tzone"],
            "s_day": p2["day"], "s_month": p2["month"], "s_year": p2["year"],
            "s_hour": p2["hour"], "s_min": p2["min"],
            "s_lat": p2["lat"], "s_lon": p2["lon"], "s_tzone": p2["tzone"]
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # OFFRE AMOUR (49€) - Compatibilité Premium
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def get_zodiac_compatibility(self, sign1: str, sign2: str) -> Optional[Dict]:
        """
        Compatibilité de base entre deux signes zodiacaux
        Retourne: score, analyse générale
        """
        data = {"zodiac1": sign1.lower(), "zodiac2": sign2.lower()}
        result = await self._make_request("zodiac_compatibility", data)
        return self._format_compatibility(result, sign1, sign2)
    
    async def get_synastry_horoscope(self, person1: Dict, person2: Dict) -> Optional[Dict]:
        """
        Analyse synastrique complète - Comparaison des thèmes nataux
        Retourne: aspects inter-charts, points de connexion, défis
        """
        data = self._parse_dual_birth_data(person1, person2)
        result = await self._make_request("synastry_horoscope", data)
        return self._format_synastry(result)
    
    async def get_romantic_personality_report(self, date_str: str, time_str: str, 
                                               lat: float, lon: float, 
                                               timezone: float = 1.0) -> Optional[Dict]:
        """
        Rapport de personnalité romantique
        Retourne: style amoureux, besoins émotionnels, points forts/faibles
        """
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("romantic_personality_report/tropical", data)
        return self._format_romantic_report(result)
    
    async def get_love_compatibility_full(self, person1: Dict, person2: Dict) -> Dict:
        """
        Analyse Amour Complète - Combinaison de tous les endpoints
        Pour l'offre Premium 49€
        """
        # Récupérer toutes les données en parallèle
        import asyncio
        
        sign1 = self._get_zodiac_from_date(person1['date'])
        sign2 = self._get_zodiac_from_date(person2['date'])
        
        zodiac_compat, synastry, romantic1, romantic2 = await asyncio.gather(
            self.get_zodiac_compatibility(sign1, sign2),
            self.get_synastry_horoscope(person1, person2),
            self.get_romantic_personality_report(
                person1['date'], person1['time'],
                person1['lat'], person1['lon'],
                person1.get('timezone', 1.0)
            ),
            self.get_romantic_personality_report(
                person2['date'], person2['time'],
                person2['lat'], person2['lon'],
                person2.get('timezone', 1.0)
            )
        )
        
        return {
            "type": "love_analysis_premium",
            "persons": {
                "person1": {
                    "sign": sign1,
                    "sign_fr": self._get_sign_french(sign1),
                    "romantic_profile": romantic1
                },
                "person2": {
                    "sign": sign2,
                    "sign_fr": self._get_sign_french(sign2),
                    "romantic_profile": romantic2
                }
            },
            "compatibility": zodiac_compat,
            "synastry": synastry,
            "synthesis": self._generate_love_synthesis(zodiac_compat, synastry, romantic1, romantic2),
            "generated_at": datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # LE CERCLE (14,90€/mois) - Contenu Quotidien Premium
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def get_tarot_predictions(self) -> Optional[Dict]:
        """
        Prédictions Tarot du jour
        Retourne: carte tirée, signification, conseil
        """
        result = await self._make_request("tarot_predictions", {})
        return self._format_tarot_predictions(result)
    
    async def get_lunar_metrics(self) -> Optional[Dict]:
        """
        Métriques lunaires complètes
        Retourne: phase, énergie, rituels recommandés
        """
        result = await self._make_request("moon_phase_report", {})
        return self._format_lunar_metrics(result)
    
    async def get_daily_horoscope_premium(self, zodiac_sign: str) -> Optional[Dict]:
        """
        Horoscope quotidien enrichi
        Retourne: prévisions détaillées par domaine
        """
        data = {"timezone": 1.0}
        result = await self._make_request(f"sun_sign_prediction/daily/{zodiac_sign.lower()}", data)
        return self._format_daily_horoscope(result, zodiac_sign)
    
    async def get_circle_daily_content(self, zodiac_sign: str) -> Dict:
        """
        Contenu quotidien complet pour Le Cercle
        Combinaison: tarot + lune + horoscope
        """
        import asyncio
        
        tarot, lunar, horoscope = await asyncio.gather(
            self.get_tarot_predictions(),
            self.get_lunar_metrics(),
            self.get_daily_horoscope_premium(zodiac_sign)
        )
        
        return {
            "type": "circle_daily",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "zodiac_sign": zodiac_sign,
            "zodiac_sign_fr": self._get_sign_french(zodiac_sign),
            "tarot": tarot,
            "lunar": lunar,
            "horoscope": horoscope,
            "daily_message": self._generate_daily_message(tarot, lunar, horoscope),
            "generated_at": datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # PROFIL UTILISATEUR - Rapports de Personnalité
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def get_karma_destiny_report(self, date_str: str, time_str: str,
                                        lat: float, lon: float,
                                        timezone: float = 1.0) -> Optional[Dict]:
        """
        Rapport Karma et Destinée
        Retourne: nœuds lunaires, leçons karmiques, mission d'âme
        """
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("karma_destiny_report", data)
        return self._format_karma_report(result)
    
    async def get_personality_report_tropical(self, date_str: str, time_str: str,
                                               lat: float, lon: float,
                                               timezone: float = 1.0) -> Optional[Dict]:
        """
        Rapport de Personnalité (système tropical)
        Retourne: analyse complète de la personnalité
        """
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("personality_report/tropical", data)
        return self._format_personality_report(result)
    
    async def get_lifepath_number(self, date_str: str) -> Optional[Dict]:
        """
        Calcul du Chemin de Vie numérologique
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        data = {"day": date.day, "month": date.month, "year": date.year}
        result = await self._make_request("lifepath_number", data)
        return self._format_lifepath(result)
    
    async def get_soul_urge_number(self, name: str) -> Optional[Dict]:
        """
        Calcul du Nombre de l'Âme (Soul Urge)
        """
        data = {"name": name}
        result = await self._make_request("soul_urge_number", data)
        return self._format_soul_urge(result)
    
    async def get_challenge_numbers(self, date_str: str) -> Optional[Dict]:
        """
        Calcul des Nombres de Défi
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        data = {"day": date.day, "month": date.month, "year": date.year}
        result = await self._make_request("challenge_numbers", data)
        return self._format_challenges(result)
    
    async def get_expression_number(self, name: str) -> Optional[Dict]:
        """
        Calcul du Nombre d'Expression
        """
        data = {"name": name}
        result = await self._make_request("expression_number", data)
        return self._format_expression(result)
    
    async def get_full_numerology_profile(self, date_str: str, name: str) -> Dict:
        """
        Profil numérologique complet
        """
        import asyncio
        
        lifepath, soul, expression, challenges = await asyncio.gather(
            self.get_lifepath_number(date_str),
            self.get_soul_urge_number(name),
            self.get_expression_number(name),
            self.get_challenge_numbers(date_str)
        )
        
        return {
            "type": "numerology_profile",
            "name": name,
            "birth_date": date_str,
            "lifepath": lifepath,
            "soul_urge": soul,
            "expression": expression,
            "challenges": challenges,
            "synthesis": self._generate_numerology_synthesis(lifepath, soul, expression, challenges),
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_full_user_profile(self, user_data: Dict) -> Dict:
        """
        Profil utilisateur complet - Combinaison de tous les rapports
        """
        import asyncio
        
        date_str = user_data['date']
        time_str = user_data['time']
        lat = user_data['lat']
        lon = user_data['lon']
        timezone = user_data.get('timezone', 1.0)
        name = user_data.get('name', '')
        
        karma, personality, numerology = await asyncio.gather(
            self.get_karma_destiny_report(date_str, time_str, lat, lon, timezone),
            self.get_personality_report_tropical(date_str, time_str, lat, lon, timezone),
            self.get_full_numerology_profile(date_str, name) if name else None
        )
        
        return {
            "type": "full_user_profile",
            "user_data": user_data,
            "karma_destiny": karma,
            "personality": personality,
            "numerology": numerology,
            "generated_at": datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # RAPPORTS PLANÉTAIRES ET MAISONS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_general_sign_report(self, date_str: str, time_str: str,
                                       lat: float, lon: float,
                                       timezone: float, planet: str) -> Optional[Dict]:
        """Rapport général d'un signe pour une planète donnée"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request(f"general_sign_report/tropical/{planet}", data)
        if result and 'report' in result:
            paragraphs = result['report']
            return {"planet": planet, "report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs]}
        return None

    async def get_general_house_report(self, date_str: str, time_str: str,
                                        lat: float, lon: float,
                                        timezone: float, planet: str) -> Optional[Dict]:
        """Rapport général d'une maison pour une planète donnée"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request(f"general_house_report/tropical/{planet}", data)
        if result and 'report' in result:
            paragraphs = result['report']
            return {"planet": planet, "report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs]}
        return None

    async def get_friendship_report(self, date_str: str, time_str: str,
                                     lat: float, lon: float,
                                     timezone: float) -> Optional[Dict]:
        """Rapport d'amitié"""
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("friendship_report", data)
        if result and 'report' in result:
            paragraphs = result['report']
            return {"report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs]}
        return None

    async def get_all_planet_reports(self, date_str: str, time_str: str,
                                      lat: float, lon: float,
                                      timezone: float = 1.0) -> Dict:
        """Récupère les rapports pour toutes les planètes principales"""
        import asyncio
        planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        
        sign_tasks = [self.get_general_sign_report(date_str, time_str, lat, lon, timezone, p) for p in planets]
        house_tasks = [self.get_general_house_report(date_str, time_str, lat, lon, timezone, p) for p in planets]
        
        results = await asyncio.gather(*sign_tasks, *house_tasks, return_exceptions=True)
        
        sign_reports = {}
        house_reports = {}
        for i, planet in enumerate(planets):
            r = results[i]
            if r and not isinstance(r, Exception):
                sign_reports[planet] = r
            r2 = results[len(planets) + i]
            if r2 and not isinstance(r2, Exception):
                house_reports[planet] = r2
        
        return {"sign_reports": sign_reports, "house_reports": house_reports}

    # ═══════════════════════════════════════════════════════════════════════════
    # CARTE DU CIEL VISUELLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def get_natal_wheel_chart(self, date_str: str, time_str: str,
                                     lat: float, lon: float,
                                     timezone: float = 1.0) -> Optional[Dict]:
        """
        Génère la carte du ciel visuelle (SVG)
        """
        data = self._parse_birth_data(date_str, time_str, lat, lon, timezone)
        result = await self._make_request("natal_wheel_chart", data)
        
        if result and result.get('status') and result.get('chart_url'):
            return {
                "chart_url": result['chart_url'],
                "format": "svg",
                "generated_at": datetime.now().isoformat()
            }
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # FORMATEURS DE DONNÉES PREMIUM
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _format_compatibility(self, result: Optional[Dict], sign1: str, sign2: str) -> Dict:
        """Formate les données de compatibilité"""
        if not result:
            return self._get_default_compatibility(sign1, sign2)
        
        return {
            "sign1": sign1,
            "sign2": sign2,
            "sign1_fr": self._get_sign_french(sign1),
            "sign2_fr": self._get_sign_french(sign2),
            "overall_score": result.get('compatibility_percentage', 75),
            "analysis": result.get('compatibility_report', ''),
        }
    
    def _format_synastry(self, result: Optional[Dict]) -> Dict:
        """Formate les données de synastrie"""
        if not result:
            return {
                "aspects": [],
                "dominant_themes": ["Communication émotionnelle", "Attraction magnétique"],
                "karmic_connections": [],
                "growth_areas": ["Patience mutuelle", "Compréhension des différences"]
            }
        
        aspects = []
        if 'aspects' in result:
            for asp in result['aspects']:
                aspects.append({
                    "planet1": asp.get('planet1', ''),
                    "planet2": asp.get('planet2', ''),
                    "aspect_type": asp.get('aspect', ''),
                    "orb": asp.get('orb', 0),
                    "interpretation": asp.get('interpretation', '')
                })
        
        return {
            "aspects": aspects,
            "dominant_themes": result.get('themes', []),
            "karmic_connections": result.get('karmic', []),
            "growth_areas": result.get('growth', [])
        }
    
    def _format_romantic_report(self, result: Optional[Dict]) -> Dict:
        """Formate le rapport romantique - API retourne {report: [paragraphs]}"""
        if not result or 'report' not in result:
            return {
                "report_paragraphs": [],
                "love_style": "Passionné et attentionné",
                "emotional_needs": ["Sécurité émotionnelle", "Attention sincère"],
            }
        
        paragraphs = result.get('report', [])
        return {
            "report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs],
            "love_style": paragraphs[0] if paragraphs else "",
            "emotional_needs": [],
        }
    
    def _format_tarot_predictions(self, result: Optional[Dict]) -> Dict:
        """Formate les prédictions tarot"""
        if not result:
            return {
                "card": "L'Étoile",
                "card_number": 17,
                "position": "droit",
                "meaning": "Espoir, inspiration et renouveau spirituel",
                "advice": "Suivez votre étoile intérieure, elle vous guide vers votre vérité",
                "lucky_number": 17,
                "lucky_color": "Bleu céleste"
            }
        
        return {
            "card": result.get('card_name', ''),
            "card_number": result.get('card_number', 0),
            "position": result.get('position', 'droit'),
            "meaning": result.get('meaning', ''),
            "advice": result.get('advice', ''),
            "lucky_number": result.get('lucky_number', 0),
            "lucky_color": result.get('lucky_color', '')
        }
    
    def _format_lunar_metrics(self, result: Optional[Dict]) -> Dict:
        """Formate les métriques lunaires"""
        moon_phases_fr = {
            "New Moon": "Nouvelle Lune",
            "Waxing Crescent": "Premier Croissant",
            "First Quarter": "Premier Quartier",
            "Waxing Gibbous": "Lune Gibbeuse Croissante",
            "Full Moon": "Pleine Lune",
            "Waning Gibbous": "Lune Gibbeuse Décroissante",
            "Last Quarter": "Dernier Quartier",
            "Waning Crescent": "Dernier Croissant"
        }
        
        if not result:
            return {
                "phase": "Pleine Lune",
                "phase_en": "Full Moon",
                "illumination": 100,
                "energy_level": "haute",
                "rituals": ["Méditation de gratitude", "Libération des blocages"],
                "advice": "Moment idéal pour célébrer vos réussites et lâcher prise"
            }
        
        phase = result.get('moon_phase', 'Full Moon')
        return {
            "phase": moon_phases_fr.get(phase, phase),
            "phase_en": phase,
            "illumination": result.get('illumination', 50),
            "energy_level": self._get_energy_level(result.get('illumination', 50)),
            "rituals": self._get_moon_rituals(phase),
            "advice": result.get('report', '')
        }
    
    def _format_daily_horoscope(self, result: Optional[Dict], zodiac_sign: str) -> Dict:
        """Formate l'horoscope quotidien"""
        if not result:
            return {
                "sign": zodiac_sign,
                "sign_fr": self._get_sign_french(zodiac_sign),
                "prediction": "Une journée favorable aux nouvelles initiatives...",
                "love": "Ouverture émotionnelle recommandée",
                "career": "Des opportunités se présentent",
                "health": "Prenez soin de votre énergie",
                "lucky_number": 7,
                "lucky_color": "Or",
                "mood": "Optimiste"
            }
        
        return {
            "sign": zodiac_sign,
            "sign_fr": self._get_sign_french(zodiac_sign),
            "prediction": result.get('prediction', ''),
            "love": result.get('love', ''),
            "career": result.get('career', ''),
            "health": result.get('health', ''),
            "lucky_number": result.get('lucky_number', 0),
            "lucky_color": result.get('lucky_color', ''),
            "mood": result.get('mood', '')
        }
    
    def _format_karma_report(self, result: Optional[Dict]) -> Dict:
        """Formate le rapport karma/destinée - API retourne {karma_destiny_report: [paragraphs]}"""
        if not result or 'karma_destiny_report' not in result:
            return {
                "report_paragraphs": [],
                "karmic_lessons": ["Apprendre l'équilibre entre vie personnelle et ambitions"],
                "soul_mission": "Développer la compassion et l'intelligence émotionnelle",
            }
        
        paragraphs = result.get('karma_destiny_report', [])
        return {
            "report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs],
            "karmic_lessons": [],
            "soul_mission": paragraphs[0] if paragraphs else "",
        }
    
    def _format_personality_report(self, result: Optional[Dict]) -> Dict:
        """Formate le rapport de personnalité - API retourne {report: [paragraphs]}"""
        if not result or 'report' not in result:
            return {
                "report_paragraphs": [],
                "sun_analysis": "Votre Soleil révèle votre essence profonde...",
            }
        
        paragraphs = result.get('report', [])
        return {
            "report_paragraphs": paragraphs if isinstance(paragraphs, list) else [paragraphs],
            "sun_analysis": paragraphs[0] if paragraphs else "",
        }
    
    def _format_lifepath(self, result: Optional[Dict]) -> Dict:
        """Formate le chemin de vie"""
        if not result:
            return {
                "number": 7,
                "title": "Le Chercheur",
                "meaning": "Quête de sagesse et de vérité intérieure",
                "traits": ["Analytique", "Spirituel", "Introspectif"],
                "career_paths": ["Recherche", "Enseignement", "Spiritualité"],
                "life_lessons": ["Faire confiance à l'intuition", "Partager sa sagesse"]
            }
        
        return {
            "number": result.get('number', 0),
            "title": result.get('title', ''),
            "meaning": result.get('meaning', ''),
            "traits": result.get('traits', []),
            "career_paths": result.get('careers', []),
            "life_lessons": result.get('lessons', [])
        }
    
    def _format_soul_urge(self, result: Optional[Dict]) -> Dict:
        """Formate le nombre de l'âme"""
        if not result:
            return {
                "number": 6,
                "meaning": "Désir profond d'harmonie et de service aux autres",
                "inner_desires": ["Paix intérieure", "Relations harmonieuses"],
                "motivations": ["Aider les autres", "Créer la beauté"]
            }
        
        return {
            "number": result.get('number', 0),
            "meaning": result.get('meaning', ''),
            "inner_desires": result.get('desires', []),
            "motivations": result.get('motivations', [])
        }
    
    def _format_expression(self, result: Optional[Dict]) -> Dict:
        """Formate le nombre d'expression"""
        if not result:
            return {
                "number": 3,
                "meaning": "Expression créative et communication inspirante",
                "talents": ["Créativité", "Communication", "Optimisme"],
                "ideal_expressions": ["Arts", "Écriture", "Enseignement"]
            }
        
        return {
            "number": result.get('number', 0),
            "meaning": result.get('meaning', ''),
            "talents": result.get('talents', []),
            "ideal_expressions": result.get('expressions', [])
        }
    
    def _format_challenges(self, result: Optional[Dict]) -> Dict:
        """Formate les nombres de défi"""
        if not result:
            return {
                "first_challenge": {"number": 2, "meaning": "Apprendre la coopération"},
                "second_challenge": {"number": 4, "meaning": "Construire des bases solides"},
                "third_challenge": {"number": 2, "meaning": "Équilibre émotionnel"},
                "main_challenge": {"number": 6, "meaning": "Responsabilité et amour"}
            }
        
        return {
            "first_challenge": result.get('first', {}),
            "second_challenge": result.get('second', {}),
            "third_challenge": result.get('third', {}),
            "main_challenge": result.get('main', {})
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # GÉNÉRATEURS DE SYNTHÈSES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_love_synthesis(self, compat: Dict, synastry: Dict, 
                                  romantic1: Dict, romantic2: Dict) -> Dict:
        """Génère une synthèse de l'analyse amoureuse"""
        overall_score = compat.get('overall_score', 75) if compat else 75
        
        if overall_score >= 80:
            harmony_level = "Excellente"
            message = "Votre connexion est profonde et naturelle. Les astres favorisent cette union."
        elif overall_score >= 60:
            harmony_level = "Bonne"
            message = "Une belle complémentarité existe entre vous. Cultivez la communication."
        else:
            harmony_level = "À développer"
            message = "Des défis existent mais peuvent être transformés en forces. La conscience est la clé."
        
        return {
            "harmony_level": harmony_level,
            "overall_message": message,
            "key_strengths": [
                "Communication émotionnelle",
                "Complémentarité des énergies"
            ],
            "growth_opportunities": [
                "Patience mutuelle",
                "Respect des différences"
            ],
            "cosmic_advice": "Laissez l'amour grandir naturellement, sans forcer les choses."
        }
    
    def _generate_daily_message(self, tarot: Dict, lunar: Dict, horoscope: Dict) -> str:
        """Génère le message quotidien personnalisé"""
        phase = lunar.get('phase', 'Pleine Lune') if lunar else 'Pleine Lune'
        card = tarot.get('card', 'L\'Étoile') if tarot else 'L\'Étoile'
        
        messages = {
            "Nouvelle Lune": f"Aujourd'hui, sous la Nouvelle Lune et l'influence de {card}, plantez les graines de vos intentions.",
            "Pleine Lune": f"La Pleine Lune amplifie l'énergie de {card}. Moment de culmination et de gratitude.",
            "Premier Quartier": f"L'énergie croissante s'allie à {card}. Avancez avec confiance.",
            "Dernier Quartier": f"Phase de lâcher-prise. {card} vous guide vers la libération."
        }
        
        return messages.get(phase, f"Les énergies de {card} et de la Lune vous accompagnent aujourd'hui.")
    
    def _generate_numerology_synthesis(self, lifepath: Dict, soul: Dict, 
                                        expression: Dict, challenges: Dict) -> Dict:
        """Génère une synthèse du profil numérologique"""
        lp_num = lifepath.get('number', 1) if lifepath else 1
        
        return {
            "core_message": f"Votre Chemin de Vie {lp_num} vous guide vers votre mission d'âme.",
            "life_purpose": lifepath.get('meaning', '') if lifepath else '',
            "inner_drive": soul.get('meaning', '') if soul else '',
            "natural_expression": expression.get('meaning', '') if expression else '',
            "current_challenge": challenges.get('main_challenge', {}).get('meaning', '') if challenges else '',
            "advice": "Alignez vos actions avec votre chemin de vie pour une vie plus épanouie."
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_zodiac_from_date(self, date_str: str) -> str:
        """Calcule le signe zodiacal à partir de la date"""
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day, month = date.day, date.month
        
        signs = [
            ((3, 21), (4, 19), "aries"), ((4, 20), (5, 20), "taurus"),
            ((5, 21), (6, 20), "gemini"), ((6, 21), (7, 22), "cancer"),
            ((7, 23), (8, 22), "leo"), ((8, 23), (9, 22), "virgo"),
            ((9, 23), (10, 22), "libra"), ((10, 23), (11, 21), "scorpio"),
            ((11, 22), (12, 21), "sagittarius"), ((12, 22), (1, 19), "capricorn"),
            ((1, 20), (2, 18), "aquarius"), ((2, 19), (3, 20), "pisces")
        ]
        
        for (start_m, start_d), (end_m, end_d), sign in signs:
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                return sign
        return "capricorn"
    
    def _get_sign_french(self, sign: str) -> str:
        """Retourne le nom français du signe"""
        names = {
            "aries": "Bélier", "taurus": "Taureau", "gemini": "Gémeaux",
            "cancer": "Cancer", "leo": "Lion", "virgo": "Vierge",
            "libra": "Balance", "scorpio": "Scorpion", "sagittarius": "Sagittaire",
            "capricorn": "Capricorne", "aquarius": "Verseau", "pisces": "Poissons"
        }
        return names.get(sign.lower(), sign)
    
    def _get_energy_level(self, illumination: int) -> str:
        """Retourne le niveau d'énergie basé sur l'illumination lunaire"""
        if illumination >= 90:
            return "très haute"
        elif illumination >= 70:
            return "haute"
        elif illumination >= 40:
            return "modérée"
        elif illumination >= 20:
            return "basse"
        else:
            return "introspective"
    
    def _get_moon_rituals(self, phase: str) -> List[str]:
        """Retourne les rituels recommandés selon la phase lunaire"""
        rituals = {
            "New Moon": ["Définir ses intentions", "Méditation de visualisation", "Nouveau départ"],
            "Waxing Crescent": ["Actions vers les objectifs", "Affirmations positives"],
            "First Quarter": ["Prendre des décisions", "Surmonter les obstacles"],
            "Waxing Gibbous": ["Peaufiner les projets", "Ajuster sa trajectoire"],
            "Full Moon": ["Méditation de gratitude", "Libération des blocages", "Célébration"],
            "Waning Gibbous": ["Partage et enseignement", "Gratitude"],
            "Last Quarter": ["Lâcher-prise", "Pardon", "Clôture"],
            "Waning Crescent": ["Repos", "Introspection", "Préparation au renouveau"]
        }
        return rituals.get(phase, ["Méditation", "Introspection"])
    
    def _get_default_compatibility(self, sign1: str, sign2: str) -> Dict:
        """Retourne une compatibilité par défaut"""
        return {
            "sign1": sign1,
            "sign2": sign2,
            "sign1_fr": self._get_sign_french(sign1),
            "sign2_fr": self._get_sign_french(sign2),
            "overall_score": 72,
            "love_score": 70,
            "trust_score": 75,
            "communication_score": 68,
            "emotional_score": 74,
            "analysis": "Une connexion intéressante avec des potentiels de croissance mutuelle.",
            "strengths": ["Complémentarité", "Attraction naturelle"],
            "challenges": ["Communication", "Différences de rythme"],
            "advice": "Cultivez la patience et l'écoute mutuelle."
        }
    
    def _get_mock_response(self, endpoint: str, data: Dict) -> Dict:
        """Retourne des données de mock pour le développement"""
        # Implement mock responses for testing without API
        return {}


# Singleton instance
_premium_service = None

def get_premium_astrology_service() -> AstrologyAPIPremium:
    """Get or create the premium astrology service instance"""
    global _premium_service
    if _premium_service is None:
        _premium_service = AstrologyAPIPremium()
    return _premium_service
