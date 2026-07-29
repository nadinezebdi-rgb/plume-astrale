"""
Astral Paths Guidance Module
Provides spiritual guidance following the 9 major astral paths and celestial wisdom.
"""

from datetime import datetime
from enum import Enum


class AstralPath(Enum):
      """The 9 major astral paths for spiritual guidance"""
      AWAKENING = "awakening"
      TRANSFORMATION = "transformation"
      EMPOWERMENT = "empowerment"
      HEALING = "healing"
      WISDOM = "wisdom"
      HARMONY = "harmony"
      MANIFESTATION = "manifestation"
      SPIRITUAL_GROWTH = "spiritual_growth"
      ENLIGHTENMENT = "enlightenment"


ASTRAL_PATHS_GUIDANCE = {
      AstralPath.AWAKENING: {
                "name": "Path of Awakening",
                "description": "Discover your inner truth and spiritual purpose",
                "keywords": ["consciousness", "awareness", "realization"],
                "affirmations": [
                              "I am awakening to my true purpose",
                              "My consciousness expands with each moment",
                              "I embrace my spiritual journey with openness"
                ],
                "guidance": "This path invites you to open your eyes to deeper truths. Trust your intuition as your internal compass."
      },
      AstralPath.TRANSFORMATION: {
                "name": "Path of Transformation",
                "description": "Embrace change and evolve beyond your limitations",
                "keywords": ["change", "growth", "rebirth"],
                "affirmations": [
                              "I embrace transformation with courage",
                              "I release what no longer serves me",
                              "I emerge stronger from every change"
                ],
                "guidance": "Change is the cosmic constant. You have the strength to transform and rise to your highest self."
      },
      AstralPath.EMPOWERMENT: {
                "name": "Path of Empowerment",
                "description": "Reclaim your personal power and agency",
                "keywords": ["power", "strength", "sovereignty"],
                "affirmations": [
                              "I am powerful and capable",
                              "My will creates my reality",
                              "I own my choices and celebrate my strength"
                ],
                "guidance": "Your power lies within. Step into your authority with confidence and claim your rightful place."
      },
      AstralPath.HEALING: {
                "name": "Path of Healing",
                "description": "Mend your heart and restore inner balance",
                "keywords": ["healing", "wholeness", "peace"],
                "affirmations": [
                              "I am healing with love and light",
                              "My wounds become my wisdom",
                              "I am whole and at peace"
                ],
                "guidance": "Healing is a sacred journey. Honor your wounds and allow compassion to guide you toward wholeness."
      },
      AstralPath.WISDOM: {
                "name": "Path of Wisdom",
                "description": "Access ancient knowledge and cosmic understanding",
                "keywords": ["knowledge", "understanding", "insight"],
                "affirmations": [
                              "I tap into universal wisdom",
                              "My inner knowing guides my path",
                              "I am a channel for cosmic truth"
                ],
                "guidance": "The universe whispers its secrets to those who listen. Seek knowledge with humility and reverence."
      },
      AstralPath.HARMONY: {
                "name": "Path of Harmony",
                "description": "Balance all aspects of your being and life",
                "keywords": ["balance", "equilibrium", "unity"],
                "affirmations": [
                              "I am in harmony with myself and the universe",
                              "Balance flows naturally through my life",
                              "I honor all aspects of my being"
                ],
                "guidance": "True harmony comes from within. Seek balance in all things and dance with the rhythm of life."
      },
      AstralPath.MANIFESTATION: {
                "name": "Path of Manifestation",
                "description": "Bring your desires into physical reality",
                "keywords": ["creation", "abundance", "intention"],
                "affirmations": [
                              "I am a conscious creator",
                              "My thoughts shape my reality",
                              "I attract abundance effortlessly"
                ],
                "guidance": "Your thoughts are seeds. Plant them with intention and watch your dreams blossom into reality."
      },
      AstralPath.SPIRITUAL_GROWTH: {
                "name": "Path of Spiritual Growth",
                "description": "Expand your consciousness and connect with the divine",
                "keywords": ["evolution", "connection", "ascension"],
                "affirmations": [
                              "My spirit grows stronger each day",
                              "I am connected to all of existence",
                              "I ascend to higher consciousness"
                ],
                "guidance": "Spiritual growth is an eternal journey. Honor each step and trust the unfolding of your path."
      },
      AstralPath.ENLIGHTENMENT: {
                "name": "Path of Enlightenment",
                "description": "Transcend ego and experience ultimate liberation",
                "keywords": ["liberation", "transcendence", "unity"],
                "affirmations": [
                              "I transcend my limitations",
                              "I am one with all existence",
                              "I experience the light of truth"
                ],
                "guidance": "Enlightenment is not a destination but a state of being. Surrender to the infinite and find your freedom."
      }
}


def get_guidance_by_path(path: AstralPath) -> dict:
      """Get complete guidance information for a specific astral path"""
      return ASTRAL_PATHS_GUIDANCE.get(path, {})


def get_all_paths() -> list:
      """Get all available astral paths"""
      return list(ASTRAL_PATHS_GUIDANCE.keys())


def get_path_by_name(name: str) -> AstralPath:
      """Get an astral path by its name (case-insensitive)"""
      for path in AstralPath:
                if path.value.lower() == name.lower():
                              return path
                      return None


def _extract_longitudes(date_time: datetime) -> dict:
      """
          Extract celestial longitudes from a given date/time.
              Returns a dictionary containing longitudinal positions for astrological bodies.
                  """
      if not isinstance(date_time, datetime):
                raise TypeError("date_time must be a datetime object")

      # Convert datetime to Julian Day for calculations
      year = date_time.year
    month = date_time.month
    day = date_time.day

    # Simplified Julian Day calculation
    if month <= 2:
              year -= 1
              month += 12

    a = year // 100
    b = 2 - a + (a // 4)

    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    jd += date_time.hour / 24.0
    jd += date_time.minute / 1440.0
    jd += date_time.second / 86400.0

    return {
              "julian_day": jd,
              "year": date_time.year,
              "month": date_time.month,
              "day": date_time.day,
              "hour": date_time.hour,
              "minute": date_time.minute
    }


def get_midpoints(longitude1: float, longitude2: float) -> dict:
      """
          Calculate the midpoints between two celestial longitudes.
              Returns both direct midpoint and the complementary midpoint.
                  """
      if not isinstance(longitude1, (int, float)) or not isinstance(longitude2, (int, float)):
                raise TypeError("Longitudes must be numeric values")

      # Normalize longitudes to 0-360 range
      lon1 = longitude1 % 360
    lon2 = longitude2 % 360

    # Calculate direct midpoint
    midpoint1 = (lon1 + lon2) / 2

    # Calculate complementary midpoint (opposite side of the zodiac)
    midpoint2 = (midpoint1 + 180) % 360

    return {
              "midpoint1": midpoint1,
              "midpoint2": midpoint2,
              "longitude1": lon1,
              "longitude2": lon2
    }


def get_asteroids_influence(asteroid_name: str, position: float) -> dict:
      """
          Provide astrological influence information for various asteroids.
              Returns guidance based on asteroid type and position.
                  """
      asteroid_meanings = {
          "chiron": {
              "name": "Chiron",
              "meaning": "The Wounded Healer",
              "influence": "Represents healing wounds and helping others transform pain into wisdom",
              "keywords": ["healing", "teaching", "mentorship"]
          },
          "ceres": {
              "name": "Ceres",
              "meaning": "The Nurturer",
              "influence": "Governs nourishment, care, and the cycles of life",
              "keywords": ["nurturing", "abundance", "cycles"]
          },
          "pallas": {
              "name": "Pallas Athena",
              "meaning": "The Wise Strategist",
              "influence": "Represents wisdom, strategy, and creative intelligence",
              "keywords": ["wisdom", "strategy", "creativity"]
          },
          "juno": {
              "name": "Juno",
              "meaning": "The Committed Partner",
              "influence": "Rules loyalty, commitment, and partnership dynamics",
              "keywords": ["commitment", "partnership", "loyalty"]
          },
          "vesta": {
              "name": "Vesta",
              "meaning": "The Devoted One",
              "influence": "Represents devotion, focus, and sacred service",
              "keywords": ["devotion", "focus", "service"]
          }
      }

    asteroid_lower = asteroid_name.lower()
    asteroid_data = asteroid_meanings.get(asteroid_lower, {
              "name": asteroid_name,
              "meaning": "Unknown Asteroid",
              "influence": "Position in your chart reveals hidden influences",
              "keywords": ["discovery", "mystery"]
    })

    return {
              "asteroid": asteroid_data,
              "position": position % 360,
              "house_influence": _get_house_by_position(position),
              "interpretation": f"{asteroid_data['meaning']} at {position:.1f}° suggests {asteroid_data['influence']}"
    }


def _get_house_by_position(position: float) -> int:
      """
          Determine astrological house based on longitudinal position.
              Houses are 30-degree segments of the zodiac.
                  """
      normalized_position = position % 360
      house = int(normalized_position / 30) + 1
      return min(house, 12)


# Export key functions and classes
__all__ = [
      'AstralPath',
      'ASTRAL_PATHS_GUIDANCE',
      'get_guidance_by_path',
      'get_all_paths',
      'get_path_by_name',
      '_extract_longitudes',
      'get_midpoints',
      'get_asteroids_influence'
]
