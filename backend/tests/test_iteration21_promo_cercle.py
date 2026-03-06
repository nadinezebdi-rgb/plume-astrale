"""
Iteration 21 - Testing NEW features:
1. Credit Promo Codes System (POST /api/credits/promo)
   - PLUMEASTRALE gives 100 credits (one-time per user)
   - TESTPLUME gives 200 credits (one-time per user)
   - BIENVENUE gives 50 credits (one-time per user)
   - Invalid code returns error
   - Duplicate use returns error

2. Carte du Jour for Cercle page (GET /api/tarot/jour)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Generate unique test user emails
def get_unique_email():
    return f"test_promo_{uuid.uuid4().hex[:8]}@plume.com"

class TestPromoCodeSystem:
    """Tests for the credit promo code system"""
    
    @pytest.fixture
    def test_user(self):
        """Create a unique test user and return credentials + token"""
        email = get_unique_email()
        password = "TestPass123!"
        
        # Register user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": password,
            "birth_date": "1990-06-15",
            "birth_time": "14:30",
            "birth_place": "Paris",
            "birth_country": "France"
        })
        
        if reg_res.status_code == 200:
            data = reg_res.json()
            return {
                "email": email,
                "password": password,
                "token": data.get("token"),
                "user_id": data.get("user", {}).get("id"),
                "initial_credits": data.get("credit_balance", 20)
            }
        
        pytest.skip(f"Could not create test user: {reg_res.text}")
    
    def test_promo_code_plumeastrale_100_credits(self, test_user):
        """Test PLUMEASTRALE promo code gives 100 credits"""
        token = test_user["token"]
        initial_credits = test_user["initial_credits"]
        
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "PLUMEASTRALE"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data["success"] is True
        assert data["credits_added"] == 100
        assert "100 crédits" in data["description"]
        assert data["credit_balance"] == initial_credits + 100
        
        print(f"✓ PLUMEASTRALE code: +100 credits, balance now {data['credit_balance']}")
    
    def test_promo_code_testplume_200_credits(self, test_user):
        """Test TESTPLUME promo code gives 200 credits"""
        token = test_user["token"]
        initial_credits = test_user["initial_credits"]
        
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "TESTPLUME"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data["success"] is True
        assert data["credits_added"] == 200
        assert data["credit_balance"] == initial_credits + 200
        
        print(f"✓ TESTPLUME code: +200 credits, balance now {data['credit_balance']}")
    
    def test_promo_code_bienvenue_50_credits(self, test_user):
        """Test BIENVENUE promo code gives 50 credits"""
        token = test_user["token"]
        initial_credits = test_user["initial_credits"]
        
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "BIENVENUE"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data["success"] is True
        assert data["credits_added"] == 50
        assert data["credit_balance"] == initial_credits + 50
        
        print(f"✓ BIENVENUE code: +50 credits, balance now {data['credit_balance']}")
    
    def test_promo_code_invalid_returns_error(self, test_user):
        """Test that invalid promo code returns 400 error"""
        token = test_user["token"]
        
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "INVALID_CODE_XYZ123"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        data = res.json()
        assert "invalide" in data.get("detail", "").lower()
        
        print(f"✓ Invalid promo code returns 400 error correctly")
    
    def test_promo_code_duplicate_use_returns_error(self, test_user):
        """Test that using same promo code twice returns error"""
        token = test_user["token"]
        
        # First use - should succeed
        res1 = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "BIENVENUE"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res1.status_code == 200, f"First use should succeed: {res1.text}"
        
        # Second use - should fail
        res2 = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "BIENVENUE"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res2.status_code == 400, f"Expected 400 for duplicate use, got {res2.status_code}"
        data = res2.json()
        assert "déjà" in data.get("detail", "").lower()
        
        print(f"✓ Duplicate promo code use returns error correctly")
    
    def test_promo_code_case_insensitive(self, test_user):
        """Test that promo code is case insensitive"""
        token = test_user["token"]
        
        # Try lowercase
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "bienvenue"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert res.status_code == 200, f"Expected 200 for lowercase code, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["credits_added"] == 50
        
        print(f"✓ Promo codes are case insensitive")
    
    def test_promo_code_requires_auth(self):
        """Test that promo code endpoint requires authentication"""
        res = requests.post(f"{BASE_URL}/api/credits/promo", 
            json={"code": "TESTPLUME"}
        )
        
        assert res.status_code == 401, f"Expected 401 without auth, got {res.status_code}"
        print(f"✓ Promo code endpoint requires authentication (401)")


class TestCarteDuJour:
    """Tests for the daily tarot card (Cercle page)"""
    
    def test_tarot_jour_returns_card(self):
        """Test GET /api/tarot/jour returns a daily card"""
        res = requests.get(f"{BASE_URL}/api/tarot/jour")
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data.get("success") is True
        assert "data" in data
        
        card_data = data["data"]
        # Check that card has expected structure
        assert "carte" in card_data or "nom" in card_data
        
        print(f"✓ Carte du jour endpoint returns valid card data")


class TestCreditPacksAndServiceCosts:
    """Verify credit packs and service costs still work"""
    
    def test_credit_packs_available(self):
        """Test GET /api/credits/packs returns packs"""
        res = requests.get(f"{BASE_URL}/api/credits/packs")
        
        assert res.status_code == 200
        data = res.json()
        
        assert "packs" in data
        packs = data["packs"]
        assert len(packs) == 3
        
        pack_ids = [p["id"] for p in packs]
        assert "decouverte" in pack_ids
        assert "exploration" in pack_ids
        assert "premium" in pack_ids
        
        print(f"✓ Credit packs: {len(packs)} packs available")
    
    def test_service_costs_available(self):
        """Test GET /api/credits/service-costs returns costs"""
        res = requests.get(f"{BASE_URL}/api/credits/service-costs")
        
        assert res.status_code == 200
        data = res.json()
        
        assert "costs" in data
        costs = data["costs"]
        
        # Verify key service costs
        assert costs.get("tarot_oui_non") == 2
        assert costs.get("lecture_tarot") == 10
        assert costs.get("numerologie") == 10
        assert costs.get("cartographie_premium") == 60
        
        print(f"✓ Service costs verified: {costs}")


class TestNumerologyEndpoint:
    """Verify numerology endpoint works (for Numérologie page)"""
    
    def test_numerology_complete_endpoint(self):
        """Test POST /api/numerology/complete"""
        res = requests.post(f"{BASE_URL}/api/numerology/complete", json={
            "prenom": "Marie",
            "dateNaissance": "1990-06-15",
            "heureNaissance": "14:30",
            "ville": "Paris"
        })
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert data.get("success") is True
        assert "data" in data
        
        # Check key numerology numbers exist
        num_data = data["data"]
        assert "chemin_de_vie" in num_data
        
        print(f"✓ Numerology endpoint returns valid data")


class TestTarologieTirage:
    """Verify tarologie tirage en croix endpoint works"""
    
    def test_tarologie_tirage_endpoint(self):
        """Test POST /api/tarologie/tirage"""
        res = requests.post(f"{BASE_URL}/api/tarologie/tirage", json={
            "prenom": "Jean",
            "date_naissance": "1985-03-22"
        })
        
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        # Verify tirage structure
        assert "tirage" in data
        tirage = data["tirage"]
        assert len(tirage) == 5, "Should have 5 cards for tirage en croix"
        
        # Verify positions exist
        positions = [c["position_id"] for c in tirage]
        assert "centre" in positions
        assert "obstacle" in positions
        assert "conseil" in positions
        assert "futur" in positions
        assert "synthese" in positions
        
        print(f"✓ Tarologie tirage en croix returns 5 cards with correct positions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
