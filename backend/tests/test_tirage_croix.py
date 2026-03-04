"""
Iteration 6 Backend Tests - Tirage en Croix (5 cards)
Tests for the new Tarologie cross spread feature:
1. POST /api/tarologie/tirage - returns 5 cards with position_id (centre, obstacle, conseil, futur, synthese)
2. POST /api/tarologie/pdf - generates PDF for cross spread
3. Regression: POST /api/tarot/oui-non and GET /api/products
"""

import pytest
import requests
import os

# Use the public URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://plume-astrale-daily.preview.emergentagent.com')


class TestTirageEnCroix:
    """Tests for the new Tirage en Croix (5 cards) feature"""
    
    def test_tirage_returns_5_cards(self):
        """Test POST /api/tarologie/tirage returns exactly 5 cards"""
        payload = {
            "prenom": "Marie",
            "date_naissance": "1990-06-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "tirage" in data, f"Response missing 'tirage' key: {data}"
        assert len(data["tirage"]) == 5, f"Expected 5 cards, got {len(data['tirage'])}"
        
        print(f"SUCCESS: Tirage returns exactly 5 cards")
    
    def test_tirage_has_type_croix(self):
        """Test that tirage response includes type='croix'"""
        payload = {
            "prenom": "Pierre",
            "date_naissance": "1985-03-20"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "type" in data, f"Response missing 'type' field: {data.keys()}"
        assert data["type"] == "croix", f"Expected type='croix', got type='{data['type']}'"
        
        print(f"SUCCESS: Tirage has type='croix'")
    
    def test_tirage_has_all_position_ids(self):
        """Test that tirage includes all 5 position_ids: centre, obstacle, conseil, futur, synthese"""
        payload = {
            "prenom": "Sophie",
            "date_naissance": "1992-08-10"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        expected_positions = ["centre", "obstacle", "conseil", "futur", "synthese"]
        actual_positions = [card["position_id"] for card in data["tirage"]]
        
        for pos in expected_positions:
            assert pos in actual_positions, f"Missing position_id: {pos}. Found: {actual_positions}"
        
        print(f"SUCCESS: All 5 position_ids present: {actual_positions}")
    
    def test_each_card_has_interpretation(self):
        """Test that each card has a non-empty 'interpretation' field"""
        payload = {
            "prenom": "Lucas",
            "date_naissance": "1988-12-01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for i, card in enumerate(data["tirage"]):
            assert "interpretation" in card, f"Card {i} missing 'interpretation' field"
            assert len(card["interpretation"]) > 50, f"Card {i} interpretation too short: {len(card['interpretation'])} chars"
        
        print(f"SUCCESS: All cards have detailed interpretations")
    
    def test_each_card_has_position_nom_and_description(self):
        """Test that each card has position_nom and position_description"""
        payload = {
            "prenom": "Emma",
            "date_naissance": "1995-04-25"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for i, card in enumerate(data["tirage"]):
            assert "position_nom" in card, f"Card {i} missing 'position_nom'"
            assert "position_description" in card, f"Card {i} missing 'position_description'"
            assert card["position_nom"], f"Card {i} position_nom is empty"
            assert card["position_description"], f"Card {i} position_description is empty"
        
        print(f"SUCCESS: All cards have position_nom and position_description")
    
    def test_cards_have_image_urls(self):
        """Test that each card has a valid image URL"""
        payload = {
            "prenom": "Thomas",
            "date_naissance": "1991-07-18"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for i, card in enumerate(data["tirage"]):
            assert "carte" in card, f"Card {i} missing 'carte' object"
            assert "image" in card["carte"], f"Card {i} missing 'image' in carte"
            image_url = card["carte"]["image"]
            assert image_url.startswith("/api/assets/tarot/"), f"Card {i} invalid image URL: {image_url}"
            assert image_url.endswith(".jpg"), f"Card {i} image should be .jpg: {image_url}"
        
        print(f"SUCCESS: All cards have valid image URLs")
    
    def test_cards_have_mots_cles_and_description_arcane(self):
        """Test that cards include mots_cles and description_arcane"""
        payload = {
            "prenom": "Julie",
            "date_naissance": "1993-09-05"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for i, card in enumerate(data["tirage"]):
            carte = card["carte"]
            assert "mots_cles" in carte, f"Card {i} missing 'mots_cles'"
            assert "description_arcane" in carte, f"Card {i} missing 'description_arcane'"
            assert len(carte["description_arcane"]) > 50, f"Card {i} description_arcane too short"
        
        print(f"SUCCESS: All cards have mots_cles and description_arcane")
    
    def test_tirage_has_lecture_mediumnique(self):
        """Test that tirage includes lecture_mediumnique with all sections"""
        payload = {
            "prenom": "Antoine",
            "date_naissance": "1989-02-14"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "lecture_mediumnique" in data, "Response missing 'lecture_mediumnique'"
        lecture = data["lecture_mediumnique"]
        
        expected_keys = ["passe", "present", "futur", "conseil_ame"]
        for key in expected_keys:
            assert key in lecture, f"Lecture missing '{key}' section"
            assert len(lecture[key]) > 20, f"Lecture '{key}' too short"
        
        print(f"SUCCESS: Lecture mediumnique has all 4 sections")


class TestTarologiePDF:
    """Tests for PDF generation of cross spread"""
    
    def test_pdf_generation(self):
        """Test POST /api/tarologie/pdf generates a valid PDF"""
        payload = {
            "prenom": "Marie",
            "date_naissance": "1990-06-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/pdf",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get('Content-Type') == 'application/pdf', "Expected PDF content type"
        
        # Check it's actually a PDF (starts with %PDF)
        content = response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF file"
        assert len(content) > 10000, f"PDF seems too small: {len(content)} bytes"
        
        print(f"SUCCESS: PDF generated, {len(content)} bytes")
    
    def test_pdf_has_correct_filename(self):
        """Test PDF response has correct Content-Disposition header"""
        payload = {
            "prenom": "TestUser",
            "date_naissance": "1985-03-20"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/pdf",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disposition, "Missing attachment in Content-Disposition"
        assert 'tarologie_croix_TestUser.pdf' in content_disposition, f"Filename incorrect: {content_disposition}"
        
        print(f"SUCCESS: PDF has correct filename in header")


class TestRegressionTarotOuiNon:
    """Regression tests for existing Tarot Oui/Non feature"""
    
    def test_tarot_oui_non_still_works(self):
        """Test POST /api/tarot/oui-non still returns correct structure"""
        payload = {"question": "Vais-je reussir mon projet?"}
        
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "question" in data
        assert "carte" in data
        assert "orientation" in data
        assert "reponse" in data
        
        # Verify card structure
        carte = data["carte"]
        assert "numero" in carte
        assert "nom" in carte
        assert "image" in carte
        
        # Verify orientation is valid
        assert data["orientation"] in ["oui", "non", "neutre"], f"Invalid orientation: {data['orientation']}"
        
        print(f"SUCCESS: Tarot oui-non returns {data['carte']['nom']} ({data['orientation']})")


class TestRegressionProducts:
    """Regression tests for products endpoint"""
    
    def test_products_endpoint(self):
        """Test GET /api/products returns all products"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=10)
        
        assert response.status_code == 200
        products = response.json()
        
        # Check required products exist
        required = ["manuscrit", "tarologie_mediumnite", "tarot_oui_non"]
        for product_id in required:
            assert product_id in products, f"Missing product: {product_id}"
        
        # Verify tarologie_mediumnite price
        assert products["tarologie_mediumnite"]["amount"] == 35.00
        assert products["tarologie_mediumnite"]["currency"] == "eur"
        
        print(f"SUCCESS: Products endpoint returns all expected products")
    
    def test_discount_code_plume2026(self):
        """Test PLUME2026 promo code for free access to all products"""
        payload = {"code": "PLUME2026"}
        
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        
        print(f"SUCCESS: PLUME2026 discount code validates correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
