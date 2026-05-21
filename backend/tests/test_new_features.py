"""
Test suite for Plume Astrale new features (Iteration 4):
- Daily content API (GET /api/daily/{sign})
- Tarot Oui/Non API (POST /api/tarot/oui-non)
- Tarologie & Médiumnité API (POST /api/tarologie/tirage, /api/tarologie/pdf)
- PDF Preview API (POST /api/pdf/preview)
- New product checkouts (tarot_oui_non, tarologie_mediumnite)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Valid zodiac signs
VALID_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Test data
TEST_USER_DATA = {
    "prenom": "Marie",
    "dateNaissance": "1990-06-15",
    "heureNaissance": "14:30",
    "ville": "Paris"
}


class TestDailyContentAPI:
    """Tests for GET /api/daily/{sign} - Daily horoscope content"""
    
    def test_daily_content_all_signs(self):
        """Test daily content returns valid data for all 12 zodiac signs"""
        for sign in VALID_SIGNS:
            response = requests.get(f"{BASE_URL}/api/daily/{sign}")
            assert response.status_code == 200, f"Failed for {sign}: {response.text}"
            
            data = response.json()
            # Verify required fields
            assert "signe" in data
            assert data["signe"] == sign
            assert "signe_fr" in data
            assert "element" in data
            assert "phrase_du_jour" in data
            assert "conseil_du_jour" in data
            assert "horoscope" in data
            assert "energie_du_jour" in data
            assert "numeros_chance" in data
            assert "couleur_du_jour" in data
    
    def test_daily_content_aries_structure(self):
        """Test daily content structure for Aries"""
        response = requests.get(f"{BASE_URL}/api/daily/Aries")
        assert response.status_code == 200
        
        data = response.json()
        # Check horoscope sections
        horoscope = data["horoscope"]
        assert "amour" in horoscope
        assert "carriere" in horoscope
        assert "sante" in horoscope
        assert "spirituel" in horoscope
        
        # Each section should have texte and score
        for section in ["amour", "carriere", "sante", "spirituel"]:
            assert "texte" in horoscope[section]
            assert "score" in horoscope[section]
            assert isinstance(horoscope[section]["score"], int)
            assert 1 <= horoscope[section]["score"] <= 10
    
    def test_daily_content_invalid_sign(self):
        """Test daily content returns 400 for invalid sign"""
        response = requests.get(f"{BASE_URL}/api/daily/InvalidSign")
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_daily_content_lucky_numbers(self):
        """Test that lucky numbers are valid"""
        response = requests.get(f"{BASE_URL}/api/daily/Leo")
        assert response.status_code == 200
        
        data = response.json()
        lucky_numbers = data["numeros_chance"]
        assert isinstance(lucky_numbers, list)
        assert len(lucky_numbers) == 3
        for num in lucky_numbers:
            assert isinstance(num, int)
            assert 1 <= num <= 49


class TestTarotOuiNonAPI:
    """Tests for POST /api/tarot/oui-non - Tarot Yes/No reading"""
    
    def test_tarot_oui_non_valid_question(self):
        """Test tarot oui/non with valid question"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "Vais-je trouver l'amour cette année?"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "question" in data
        assert "carte" in data
        assert "orientation" in data
        assert "reponse" in data
        assert "date" in data
        
        # Check carte structure
        carte = data["carte"]
        assert "numero" in carte
        assert "nom" in carte
        assert "energie" in carte
        
        # Check orientation is valid
        assert data["orientation"] in ["oui", "non", "neutre"]
    
    def test_tarot_oui_non_empty_question(self):
        """Test tarot oui/non with empty question returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": ""}
        )
        assert response.status_code == 400
    
    def test_tarot_oui_non_different_questions(self):
        """Test different questions can get different cards"""
        questions = [
            "Vais-je réussir mon examen?",
            "Est-ce le bon moment pour investir?",
            "Dois-je changer de travail?"
        ]
        
        results = []
        for q in questions:
            response = requests.post(
                f"{BASE_URL}/api/tarot/oui-non",
                json={"question": q}
            )
            assert response.status_code == 200
            results.append(response.json()["carte"]["nom"])
        
        # Results may vary (not asserting uniqueness since it's random)
        assert len(results) == 3


class TestTarologieMediumniteAPI:
    """Tests for POST /api/tarologie/tirage and /api/tarologie/pdf"""
    
    def test_tarologie_tirage_valid(self):
        """Test tarologie tirage with valid data"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json={"prenom": "Marie", "date_naissance": "1990-06-15"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "prenom" in data
        assert data["prenom"] == "Marie"
        assert "date_naissance" in data
        assert "tirage" in data
        assert "lecture_mediumnique" in data
        assert "date" in data
        
        # Check tirage has 7 cards
        tirage = data["tirage"]
        assert len(tirage) == 7
        
        # Check each card structure
        for i, item in enumerate(tirage):
            assert "position" in item
            assert "carte" in item
            assert "message" in item
            assert "numero" in item["carte"]
            assert "nom" in item["carte"]
            assert "energie" in item["carte"]
    
    def test_tarologie_tirage_lecture_mediumnique(self):
        """Test lecture mediumnique structure"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json={"prenom": "Jean", "date_naissance": "1985-03-20"}
        )
        assert response.status_code == 200
        
        lecture = response.json()["lecture_mediumnique"]
        assert "passe" in lecture
        assert "present" in lecture
        assert "futur" in lecture
        assert "conseil_ame" in lecture
    
    def test_tarologie_tirage_empty_prenom(self):
        """Test tarologie tirage with empty prenom returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json={"prenom": "", "date_naissance": "1990-06-15"}
        )
        assert response.status_code == 400
    
    def test_tarologie_pdf_generation(self):
        """Test tarologie PDF generation"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/pdf",
            json={"prenom": "Marie", "date_naissance": "1990-06-15"}
        )
        assert response.status_code == 200
        
        # Check it's a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type
        
        # Check PDF is not empty (should be > 10KB)
        assert len(response.content) > 10000
        
        # Check it starts with PDF magic bytes
        assert response.content[:4] == b'%PDF'


class TestPdfPreviewAPI:
    """Tests for POST /api/pdf/preview - PDF manuscript preview"""
    
    def test_pdf_preview_valid(self):
        """Test PDF preview with valid user data"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "previews" in data
        assert "total_pages" in data
        
        # Should have 3 preview images
        assert len(data["previews"]) == 3
        
        # Each preview should be base64 encoded JPEG
        for preview in data["previews"]:
            assert preview.startswith("data:image/jpeg;base64,")
        
        # Should have more than 10 pages
        assert data["total_pages"] >= 10
    
    def test_pdf_preview_minimal_data(self):
        """Test PDF preview with minimal user data"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": {"prenom": "Test"}}
        )
        assert response.status_code == 200


class TestNewProductCheckouts:
    """Tests for checkout with new products"""
    
    def test_checkout_tarot_oui_non(self):
        """Test checkout creation for tarot_oui_non product (4.99€)"""
        response = requests.post(
            f"{BASE_URL}/api/checkout/create",
            json={
                "product_id": "tarot_oui_non",
                "origin_url": "https://consultation-astro.preview.emergentagent.com",
                "user_data": {"question": "Test question"}
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "url" in data
        assert "session_id" in data
        assert data["url"].startswith("https://checkout.stripe.com")
    
    def test_checkout_tarologie_mediumnite(self):
        """Test checkout creation for tarologie_mediumnite product (35€)"""
        response = requests.post(
            f"{BASE_URL}/api/checkout/create",
            json={
                "product_id": "tarologie_mediumnite",
                "origin_url": "https://consultation-astro.preview.emergentagent.com",
                "user_data": {"prenom": "Marie", "dateNaissance": "1990-06-15"}
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "url" in data
        assert "session_id" in data
    
    def test_checkout_invalid_product(self):
        """Test checkout with invalid product returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/checkout/create",
            json={
                "product_id": "invalid_product",
                "origin_url": "https://example.com"
            }
        )
        assert response.status_code == 400


class TestProductsAPI:
    """Tests for GET /api/products - Product catalog"""
    
    def test_products_list(self):
        """Test products endpoint returns all products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check new products exist
        assert "tarot_oui_non" in data
        assert "tarologie_mediumnite" in data
        
        # Check tarot_oui_non price
        assert data["tarot_oui_non"]["amount"] == 4.99
        assert data["tarot_oui_non"]["currency"] == "eur"
        
        # Check tarologie_mediumnite price
        assert data["tarologie_mediumnite"]["amount"] == 35.00
        assert data["tarologie_mediumnite"]["currency"] == "eur"


class TestExistingFlowRegression:
    """Regression tests for existing functionality"""
    
    def test_discount_validate_astro100(self):
        """Test ASTRO100 promo code still works"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "ASTRO100"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] is True
        assert data["discount_percent"] == 100
    
    def test_free_access_with_astro100(self):
        """Test free access with ASTRO100 code"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "manuscrit",
                "origin_url": "https://consultation-astro.preview.emergentagent.com",
                "user_data": TEST_USER_DATA,
                "discount_code": "ASTRO100"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_pdf_generate(self):
        """Test PDF generation still works"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA}
        )
        assert response.status_code == 200
        
        # Should be a PDF
        assert response.content[:4] == b'%PDF'


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
