"""
Iteration 13 - Visual Redesign Testing
Tests for the major visual redesign from purple SaaS to dark editorial design.
All business logic and APIs must remain functional.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBackendAPIs:
    """Test all backend API endpoints still work after redesign"""
    
    def test_root_endpoint(self):
        """Test API root endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"SUCCESS: Root endpoint returns: {data}")
    
    def test_tarot_oui_non(self):
        """Test tarot oui-non endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "Test question for redesign iteration"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "carte" in data
        assert "orientation" in data
        assert "reponse" in data
        assert data["orientation"] in ["oui", "non", "neutre"]
        
        # Verify carte structure
        carte = data["carte"]
        assert "nom" in carte
        assert "numero" in carte
        print(f"SUCCESS: Tarot oui-non returned carte: {carte['nom']} ({data['orientation']})")
    
    def test_numerology_complete(self):
        """Test numerology complete endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/numerology/complete",
            json={
                "prenom": "Marie",
                "dateNaissance": "1990-06-15",
                "heureNaissance": "14:30",
                "ville": "Paris"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "data" in data
        
        # Verify numerology data
        numerology_data = data["data"]
        assert "chemin_de_vie" in numerology_data
        assert "nombre_expression" in numerology_data
        
        print(f"SUCCESS: Numerology returned chemin_de_vie: {numerology_data['chemin_de_vie']['nombre']}")
    
    def test_daily_horoscope(self):
        """Test daily horoscope endpoint"""
        response = requests.get(f"{BASE_URL}/api/daily/Cancer")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "phrase_du_jour" in data
        assert "energie_du_jour" in data
        assert "horoscope" in data
        
        print(f"SUCCESS: Daily horoscope returned phrase: {data['phrase_du_jour'][:50]}...")


class TestDiscountCodes:
    """Test promo code functionality preserved after redesign"""
    
    def test_discount_validate_plume2026(self):
        """Test PLUME2026 discount code validation"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        print(f"SUCCESS: PLUME2026 validates with 100% discount")
    
    def test_discount_validate_invalid_code(self):
        """Test invalid discount code returns proper response"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALIDCODE123"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        print(f"SUCCESS: Invalid code properly rejected")
    
    def test_discount_case_insensitive(self):
        """Test discount code is case insensitive"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "plume2026"}  # lowercase
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        print(f"SUCCESS: Discount code is case insensitive")
    
    def test_free_access_with_promo(self):
        """Test free access endpoint with promo code"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "tarologie_mediumnite",
                "discount_code": "PLUME2026",
                "user_data": {"prenom": "Test", "dateNaissance": "1990-01-01"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        print(f"SUCCESS: Free access granted with PLUME2026")


class TestTarologieTirage:
    """Test tarologie cross spread functionality"""
    
    def test_tarologie_tirage(self):
        """Test tarologie tirage endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json={
                "prenom": "Marie",
                "date_naissance": "1990-06-15"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response has tirage
        assert "tirage" in data
        assert len(data["tirage"]) == 5  # 5 cards in cross spread
        
        # Verify each card has required fields
        positions = ["centre", "obstacle", "conseil", "futur", "synthese"]
        for card in data["tirage"]:
            assert "position_id" in card
            assert "carte" in card
            assert "interpretation" in card
            assert card["position_id"] in positions
        
        print(f"SUCCESS: Tarologie tirage returned 5 cards with interpretations")


class TestProducts:
    """Test product listing endpoint"""
    
    def test_products_list(self):
        """Test products endpoint returns product list"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify product structure
        for product in data:
            assert "id" in product
            assert "name" in product
        
        print(f"SUCCESS: Products endpoint returned {len(data)} products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
