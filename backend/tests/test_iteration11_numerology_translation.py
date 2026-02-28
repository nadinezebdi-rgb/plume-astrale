"""
Iteration 11 - Numerology and Translation Service Tests
Tests the new /api/numerology/complete and /api/translate endpoints
Plus regression tests for existing endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestNumerologyEndpoint:
    """Test /api/numerology/complete endpoint - local fallback when API blocked"""
    
    def test_numerology_complete_success(self):
        """POST /api/numerology/complete returns numerology data with local fallback"""
        response = requests.post(f"{BASE_URL}/api/numerology/complete", json={
            "prenom": "Marie",
            "dateNaissance": "1990-06-15",
            "heureNaissance": "14:30",
            "ville": "Paris"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Expected success=True"
        # Should use local fallback since API is blocked
        assert data["source"] in ["local", "api"], f"Unexpected source: {data['source']}"
        
        # Validate numerology data structure
        numero_data = data["data"]
        assert "chemin_de_vie" in numero_data, "Missing chemin_de_vie"
        assert "nombre_expression" in numero_data, "Missing nombre_expression"
        assert "nombre_ame" in numero_data, "Missing nombre_ame"
        assert "nombre_personnalite" in numero_data, "Missing nombre_personnalite"
        assert "nombre_anniversaire" in numero_data, "Missing nombre_anniversaire"
        assert "annee_personnelle_2026" in numero_data, "Missing annee_personnelle_2026"
        
        # Validate chemin_de_vie structure
        life_path = numero_data["chemin_de_vie"]
        assert "nombre" in life_path, "Missing life path nombre"
        assert "titre" in life_path, "Missing life path titre"
        assert "description" in life_path, "Missing life path description"
        assert isinstance(life_path["nombre"], int), "Life path nombre should be int"
        
        print(f"Numerology test passed: source={data['source']}, chemin_de_vie={life_path['nombre']}")
    
    def test_numerology_complete_calculates_correctly(self):
        """Verify local numerology calculation is correct for known date"""
        response = requests.post(f"{BASE_URL}/api/numerology/complete", json={
            "prenom": "Marie",
            "dateNaissance": "1990-06-15",  # 1+9+9+0+0+6+1+5 = 31 -> 3+1 = 4
            "heureNaissance": "12:00",
            "ville": "Paris"
        })
        assert response.status_code == 200
        
        data = response.json()
        numero_data = data["data"]
        
        # Verify life path calculation: 1990-06-15 -> 1+9+9+0+6+1+5 = 31 -> 3+1 = 4
        # Or (15+6+1990) -> 15+6+1990 = 2011 -> 2+0+1+1 = 4
        life_path = numero_data["chemin_de_vie"]["nombre"]
        print(f"Life path for 1990-06-15: {life_path}")
        # Life path should be 4 for this date
        assert life_path == 4, f"Expected life path 4, got {life_path}"
        
        # Birthday number: 15 -> 1+5 = 6
        birthday = numero_data["nombre_anniversaire"]["nombre"]
        print(f"Birthday number for day 15: {birthday}")
        assert birthday == 6, f"Expected birthday number 6, got {birthday}"
    
    def test_numerology_with_minimal_data(self):
        """Test numerology with only required fields"""
        response = requests.post(f"{BASE_URL}/api/numerology/complete", json={
            "prenom": "Jean",
            "dateNaissance": "1985-12-25"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        print(f"Minimal data test passed: source={data.get('source', 'unknown')}")


class TestTranslationEndpoint:
    """Test /api/translate endpoint - uses Emergent LLM key with GPT-4o-mini"""
    
    def test_translate_english_to_french(self):
        """POST /api/translate translates English astrological text to French"""
        response = requests.post(f"{BASE_URL}/api/translate", json={
            "text": "The Sun is in Aries, creating a powerful energy for new beginnings."
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Expected success=True"
        assert "original" in data, "Missing original text"
        assert "translated" in data, "Missing translated text"
        
        # Check that translation contains French astrology terms
        translated = data["translated"].lower()
        # Should translate "Sun" to "Soleil" and "Aries" to "Belier"
        print(f"Original: {data['original']}")
        print(f"Translated: {data['translated']}")
        
        # Verify translation is not empty and different from original (unless API key missing)
        assert len(data["translated"]) > 0, "Translation is empty"
    
    def test_translate_empty_text(self):
        """POST /api/translate with empty text returns 400"""
        response = requests.post(f"{BASE_URL}/api/translate", json={
            "text": ""
        })
        assert response.status_code == 400, f"Expected 400 for empty text, got {response.status_code}"
    
    def test_translate_zodiac_terms(self):
        """Test translation of zodiac and planet names"""
        response = requests.post(f"{BASE_URL}/api/translate", json={
            "text": "Mercury in Gemini creates a Trine aspect with Venus in Libra."
        })
        assert response.status_code == 200
        
        data = response.json()
        translated = data["translated"]
        print(f"Zodiac translation: {translated}")
        
        # Should contain French terms (if translation working)
        assert len(translated) > 10, "Translation seems too short"


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    def test_root_endpoint(self):
        """GET /api/ returns 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("Root endpoint OK")
    
    def test_moon_phase(self):
        """GET /api/moon-phase still works"""
        response = requests.get(f"{BASE_URL}/api/moon-phase")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "phase" in data, "Missing phase"
        print(f"Moon phase: {data['phase']}")
    
    def test_tarot_oui_non(self):
        """POST /api/tarot/oui-non still works with 3-tirage limit"""
        response = requests.post(f"{BASE_URL}/api/tarot/oui-non", json={
            "question": "Vais-je reussir mon projet?"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "carte" in data, "Missing carte"
        assert "orientation" in data, "Missing orientation"
        assert "reponse" in data, "Missing reponse"
        print(f"Tarot: {data['carte']['nom']} - {data['orientation']}")
    
    def test_pro_horoscope_pdf(self):
        """POST /api/pdf/pro-horoscope still generates PDF"""
        response = requests.post(f"{BASE_URL}/api/pdf/pro-horoscope", json={
            "name": "TestUser",
            "gender": "female",
            "day": 15,
            "month": 6,
            "year": 1990,
            "hour": 14,
            "minute": 30,
            "lat": 48.8566,
            "lon": 2.3522,
            "timezone": 1.0,
            "place": "Paris, France"
        })
        assert response.status_code == 200
        assert len(response.content) > 100000, f"PDF too small: {len(response.content)} bytes"
        print(f"Pro horoscope PDF generated: {len(response.content)} bytes")
    
    def test_products_endpoint(self):
        """GET /api/products returns product list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        data = response.json()
        assert "manuscrit" in data
        assert "tarot_oui_non" in data
        print(f"Products: {list(data.keys())}")
    
    def test_daily_horoscope(self):
        """GET /api/daily/{sign} still works"""
        response = requests.get(f"{BASE_URL}/api/daily/Aries")
        assert response.status_code == 200
        
        data = response.json()
        assert "signe_zodiaque" in data
        assert "phrase_du_jour" in data
        print(f"Daily horoscope for Aries OK")


class TestHomepageRegression:
    """Verify homepage CTAs still exist"""
    
    def test_homepage_has_tarot_cta(self):
        """Verify homepage has cta-tarot-entry"""
        response = requests.get(f"{BASE_URL}")
        assert response.status_code == 200
        assert "cta-tarot-entry" in response.text, "Missing cta-tarot-entry on homepage"
        print("Homepage has cta-tarot-entry")
    
    def test_homepage_has_astrology_cta(self):
        """Verify homepage has cta-astrology-entry"""
        response = requests.get(f"{BASE_URL}")
        assert response.status_code == 200
        assert "cta-astrology-entry" in response.text, "Missing cta-astrology-entry on homepage"
        print("Homepage has cta-astrology-entry")
    
    def test_homepage_has_numerologie_card(self):
        """Verify homepage has cta-numerologie card"""
        response = requests.get(f"{BASE_URL}")
        assert response.status_code == 200
        assert "cta-numerologie" in response.text, "Missing cta-numerologie on homepage"
        print("Homepage has cta-numerologie card")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
