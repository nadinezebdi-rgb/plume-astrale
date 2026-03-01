"""
Iteration 14 Tests - Dark Violet Redesign with Twinkling Stars
Tests for: visual redesign, sparkle effects, golden writing, promo codes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestBackendAPIs:
    """Backend API functionality tests"""

    def test_health_check(self):
        """API root returns 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✓ API health check passed")

    def test_tarot_oui_non(self):
        """Tarot Oui/Non tirage API works"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "Test question for iteration 14"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "carte" in data
        assert "orientation" in data
        assert "reponse" in data
        print(f"✓ Tarot API works - Card: {data['carte']['nom']}, Orientation: {data['orientation']}")

    def test_numerology_complete(self):
        """Numerology API returns complete data"""
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
        assert data.get("success") == True
        assert "data" in data
        assert "chemin_de_vie" in data["data"]
        print(f"✓ Numerology API works - Life Path: {data['data']['chemin_de_vie']['nombre']}")

    def test_daily_horoscope(self):
        """Daily horoscope API for Aries"""
        response = requests.get(f"{BASE_URL}/api/daily/Aries")
        assert response.status_code == 200
        data = response.json()
        assert "phrase_du_jour" in data
        assert "horoscope" in data
        print(f"✓ Daily API works - Phrase: {data['phrase_du_jour'][:50]}...")

    def test_promo_code_valid(self):
        """Promo code PLUME2026 validates correctly with 100% discount"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True
        assert data.get("discount_percent") == 100
        print(f"✓ Promo code PLUME2026 valid - {data['discount_percent']}% discount")

    def test_promo_code_invalid(self):
        """Invalid promo code returns proper error"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALIDCODE123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == False
        print("✓ Invalid promo code correctly rejected")

    def test_free_access_with_promo(self):
        """Free access endpoint works with valid promo code"""
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
        print("✓ Free access with promo code works")

    def test_tarologie_tirage(self):
        """Tarologie tirage returns 5 cards"""
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json={
                "prenom": "TestUser",
                "date_naissance": "1990-06-15"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "tirage" in data
        assert len(data["tirage"]) == 5
        positions = [c["position_id"] for c in data["tirage"]]
        assert "centre" in positions
        assert "obstacle" in positions
        assert "conseil" in positions
        assert "futur" in positions
        assert "synthese" in positions
        print(f"✓ Tarologie tirage works - {len(data['tirage'])} cards returned")

    def test_products_catalog(self):
        """Products catalog returns available products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "products" in data
        print("✓ Products catalog API works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
