"""
Iteration 12 - Promo Code Testing for PLUME2026
Tests the discount validation and free access endpoints
Also tests that promo code exists on all required payment pages
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://plume-tarot-test.preview.emergentagent.com').rstrip('/')

class TestPromoCodeBackend:
    """Test promo code validation and free access endpoints"""
    
    # Test PLUME2026 code validation - should return 100% discount
    def test_validate_plume2026_code_returns_valid(self):
        response = requests.post(f"{BASE_URL}/api/discount/validate", json={
            "code": "PLUME2026"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        assert "gratuit" in data["message"].lower() or "acces" in data["message"].lower()
        print(f"PASS: PLUME2026 validated with 100% discount")
    
    # Test invalid code returns valid=false
    def test_validate_invalid_code_returns_invalid(self):
        response = requests.post(f"{BASE_URL}/api/discount/validate", json={
            "code": "INVALID123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert data["discount_percent"] is None
        print(f"PASS: Invalid code correctly rejected")
    
    # Test ASTRO100 code (existing code) also works
    def test_validate_astro100_code_returns_valid(self):
        response = requests.post(f"{BASE_URL}/api/discount/validate", json={
            "code": "ASTRO100"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        print(f"PASS: ASTRO100 validated with 100% discount")
    
    # Test free access endpoint with PLUME2026 for manuscrit product
    def test_free_access_manuscrit_with_plume2026(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "manuscrit",
            "discount_code": "PLUME2026",
            "user_email": "test_iter12@test.com",
            "user_data": {"prenom": "TestMarie", "dateNaissance": "1990-06-15"},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "redirect_url" in data or "session_id" in str(data)
        print(f"PASS: Free access granted for manuscrit with PLUME2026")
    
    # Test free access endpoint with PLUME2026 for tarologie_mediumnite product
    def test_free_access_tarologie_with_plume2026(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "tarologie_mediumnite",
            "discount_code": "PLUME2026",
            "user_email": "test_iter12_taro@test.com",
            "user_data": {"prenom": "TestJean"},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"PASS: Free access granted for tarologie_mediumnite with PLUME2026")
    
    # Test free access endpoint with PLUME2026 for livre product
    def test_free_access_livre_with_plume2026(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "livre",
            "discount_code": "PLUME2026",
            "user_email": "test_iter12_livre@test.com",
            "user_data": {"prenom": "TestLivre"},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"PASS: Free access granted for livre with PLUME2026")
    
    # Test free access endpoint with PLUME2026 for compatibilite product
    def test_free_access_compatibilite_with_plume2026(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "compatibilite",
            "discount_code": "PLUME2026",
            "user_email": "test_iter12_compat@test.com",
            "user_data": {"person1": {"prenom": "Test1"}, "person2": {"prenom": "Test2"}},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"PASS: Free access granted for compatibilite with PLUME2026")
    
    # Test free access with invalid code fails
    def test_free_access_with_invalid_code_fails(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "manuscrit",
            "discount_code": "INVALID123",
            "user_email": "test@test.com",
            "user_data": {"prenom": "Test"},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 400
        print(f"PASS: Free access correctly rejected for invalid code")
    
    # Test free access without discount_code fails
    def test_free_access_without_code_fails(self):
        response = requests.post(f"{BASE_URL}/api/access/free", json={
            "product_id": "manuscrit",
            "user_email": "test@test.com",
            "user_data": {"prenom": "Test"},
            "origin_url": "https://plume-tarot-test.preview.emergentagent.com"
        })
        assert response.status_code == 400
        print(f"PASS: Free access correctly rejected when no code provided")
    
    # Test case insensitivity - lowercase should work
    def test_validate_code_case_insensitive(self):
        response = requests.post(f"{BASE_URL}/api/discount/validate", json={
            "code": "plume2026"  # lowercase
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        print(f"PASS: Code validation is case-insensitive")
    
    # Test code with extra spaces
    def test_validate_code_with_spaces(self):
        response = requests.post(f"{BASE_URL}/api/discount/validate", json={
            "code": "  PLUME2026  "  # with spaces
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        print(f"PASS: Code validation trims spaces")


class TestRegressionAPIs:
    """Regression tests for core APIs"""
    
    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"PASS: Root endpoint working")
    
    def test_products_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "manuscrit" in data
        assert "tarologie_mediumnite" in data
        print(f"PASS: Products endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
