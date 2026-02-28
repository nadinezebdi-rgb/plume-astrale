"""
Iteration 10: Test Homepage Redesign and Tarot Oui/Non Flow
Tests the Phase 1 + P0 tasks:
- Homepage with 2 main CTAs (Tarot/Astrologie) 
- Tarot Oui/Non API endpoint
- Moon phase endpoint
- PDF pro-horoscope endpoint (regression)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRootAndHealth:
    """Basic API health checks"""
    
    def test_root_endpoint(self):
        """Test GET /api/ returns 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Root endpoint: {data}")


class TestTarotOuiNon:
    """Test Tarot Oui/Non API endpoint"""
    
    def test_tarot_oui_non_basic(self):
        """Test POST /api/tarot/oui-non returns valid response"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "Test question?"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "question" in data
        assert "carte" in data
        assert "orientation" in data
        assert "reponse" in data
        assert "date" in data
        
        # Verify carte structure
        carte = data["carte"]
        assert "numero" in carte
        assert "nom" in carte
        assert "energie" in carte
        assert "image" in carte
        
        # Verify orientation is valid
        assert data["orientation"] in ["oui", "non", "neutre"]
        
        print(f"✓ Tarot result: {carte['nom']} - {data['orientation']}")
    
    def test_tarot_oui_non_empty_question(self):
        """Test POST /api/tarot/oui-non with empty question returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": ""},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Empty question returns 400")
    
    def test_tarot_oui_non_whitespace_question(self):
        """Test POST /api/tarot/oui-non with whitespace question returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "   "},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Whitespace question returns 400")


class TestMoonPhase:
    """Test Moon Phase API endpoint"""
    
    def test_moon_phase_endpoint(self):
        """Test GET /api/moon-phase returns valid response"""
        response = requests.get(f"{BASE_URL}/api/moon-phase")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "phase" in data  # French phase name
        assert "phase_en" in data  # English phase name
        assert "conseil" in data  # Advice text
        assert "signification" in data  # Significance text
        
        # Verify French phase names
        french_phases = [
            "Nouvelle Lune", "Premier Croissant", "Premier Quartier",
            "Lune Gibbeuse", "Pleine Lune", "Lune Disséminante",
            "Dernier Quartier", "Lune Balsamique", "Dernier Croissant"
        ]
        assert data["phase"] in french_phases, f"Phase {data['phase']} not in expected list"
        
        print(f"✓ Moon phase: {data['phase']} ({data['phase_en']})")


class TestDailyContent:
    """Test Daily Content API endpoint"""
    
    def test_daily_content_with_moon_phase(self):
        """Test GET /api/daily/{sign} returns content with phase_lunaire"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini")
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic content structure
        assert "phrase_du_jour" in data
        assert "conseil_du_jour" in data
        assert "energie_du_jour" in data
        assert "horoscope" in data
        
        # Verify phase_lunaire section (from iteration 9)
        assert "phase_lunaire" in data
        phase_lunaire = data["phase_lunaire"]
        assert "phase" in phase_lunaire  # French phase
        assert "phase_en" in phase_lunaire  # English phase
        assert "conseil" in phase_lunaire  # French advice
        
        print(f"✓ Daily content with moon phase: {phase_lunaire['phase']}")
    
    def test_daily_invalid_sign(self):
        """Test GET /api/daily/{invalid} returns 400"""
        response = requests.get(f"{BASE_URL}/api/daily/InvalidSign")
        assert response.status_code == 400
        print("✓ Invalid sign returns 400")


class TestProHoroscopePDF:
    """Test PDF generation endpoint (regression)"""
    
    def test_pro_horoscope_pdf_generation(self):
        """Test POST /api/pdf/pro-horoscope generates PDF"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json={
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
                "place": "Paris"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        # Verify PDF size (should be > 500KB with chart)
        pdf_size = len(response.content)
        assert pdf_size > 500000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✓ Pro horoscope PDF generated: {pdf_size} bytes")


class TestDiscountCode:
    """Test discount code validation (regression)"""
    
    def test_valid_discount_code(self):
        """Test POST /api/discount/validate with PLUME2026"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        print(f"✓ Discount code PLUME2026 valid: {data['message']}")
    
    def test_invalid_discount_code(self):
        """Test POST /api/discount/validate with invalid code"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALIDCODE"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        print("✓ Invalid code returns valid=false")


class TestShareCard:
    """Test share card generation (regression)"""
    
    def test_share_card_generation(self):
        """Test POST /api/share/generate-card returns PNG"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={
                "user_data": {
                    "prenom": "Marie",
                    "dateNaissance": "1990-06-15",
                    "heureNaissance": "14:30",
                    "ville": "Paris"
                }
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        assert "image/png" in response.headers.get("content-type", "")
        
        # Verify image size
        img_size = len(response.content)
        assert img_size > 10000, f"Image too small: {img_size} bytes"
        
        print(f"✓ Share card PNG generated: {img_size} bytes")


class TestProducts:
    """Test products listing (regression)"""
    
    def test_get_products(self):
        """Test GET /api/products returns product list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected products exist
        expected_products = ["manuscrit", "tarot_oui_non", "tarologie_mediumnite"]
        for product_id in expected_products:
            assert product_id in data, f"Missing product: {product_id}"
        
        # Verify tarot_oui_non product
        tarot_product = data["tarot_oui_non"]
        assert tarot_product["amount"] == 4.99
        assert tarot_product["currency"] == "eur"
        
        print(f"✓ Products listed: {list(data.keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
