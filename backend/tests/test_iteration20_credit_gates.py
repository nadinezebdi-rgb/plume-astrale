"""
Iteration 20 - Comprehensive test for credit-gated services and enhanced buy credits page.
Testing: Auth (register/login), Credit system (use credits for services), Service cost validation
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthSystem:
    """Test authentication endpoints with astrological profile"""
    
    def test_register_creates_user_with_20_bonus_credits(self):
        """POST /api/auth/register - creates user with 20 bonus credits"""
        unique_email = f"test_iter20_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "birth_place": "Lyon",
            "birth_country": "France"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify token returned
        assert "token" in data, "Token not returned"
        assert len(data["token"]) > 0, "Empty token"
        
        # Verify credit balance is 20
        assert data.get("credit_balance") == 20, f"Expected 20 bonus credits, got {data.get('credit_balance')}"
        
        # Verify user data
        assert data["user"]["email"] == unique_email
        assert data["user"]["birth_date"] == "1990-05-15"
        assert data["user"]["birth_time"] == "14:30"
        assert data["user"]["birth_place"] == "Lyon"
        print(f"PASS: Register creates user with 20 bonus credits - user: {unique_email}")
    
    def test_login_returns_jwt_and_credit_balance(self):
        """POST /api/auth/login - returns JWT + credit balance"""
        # First register a user
        unique_email = f"test_login_{uuid.uuid4().hex[:8]}@plume.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1988-12-25",
            "birth_time": "08:00",
            "birth_place": "Marseille",
            "birth_country": "France"
        })
        assert reg_response.status_code == 200
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "TestPass123!"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "token" in data, "Token not in login response"
        assert "credit_balance" in data, "credit_balance not in login response"
        assert data["credit_balance"] >= 20, f"Expected at least 20 credits, got {data['credit_balance']}"
        print(f"PASS: Login returns JWT + credit balance ({data['credit_balance']} credits)")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - returns 401 for invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@plume.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Login returns 401 for invalid credentials")


class TestCreditUseTarotOuiNon:
    """Test credit deduction for Tarot Oui/Non - first is free, then 2 credits"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a fresh user for each test"""
        self.email = f"test_tarot_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.email,
            "password": "TestPass123!",
            "birth_date": "1995-03-21",
            "birth_time": "16:45",
            "birth_place": "Bordeaux",
            "birth_country": "France"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.initial_balance = response.json()["credit_balance"]  # Should be 20
    
    def test_tarot_oui_non_first_is_free(self):
        """POST /api/credits/use for tarot_oui_non - first draw is free"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "tarot_oui_non"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("free_draw") == True, "First draw should be free"
        assert data.get("credit_balance") == self.initial_balance, f"Balance should stay at {self.initial_balance}"
        print(f"PASS: Tarot Oui/Non first draw is FREE - balance: {data['credit_balance']}")
    
    def test_tarot_oui_non_second_deducts_2_credits(self):
        """POST /api/credits/use for tarot_oui_non - second deducts 2 credits"""
        # First draw (free)
        requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "tarot_oui_non"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # Second draw (costs 2 credits)
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "tarot_oui_non"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("free_draw") == False, "Second draw should not be free"
        expected_balance = self.initial_balance - 2
        assert data.get("credit_balance") == expected_balance, f"Expected {expected_balance}, got {data['credit_balance']}"
        print(f"PASS: Tarot Oui/Non second draw deducts 2 credits - balance: {data['credit_balance']}")


class TestCreditUseLectureTarot:
    """Test credit deduction for lecture_tarot - 10 credits"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a fresh user for each test"""
        self.email = f"test_lecture_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.email,
            "password": "TestPass123!",
            "birth_date": "1992-07-04",
            "birth_time": "11:30",
            "birth_place": "Nice",
            "birth_country": "France"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.initial_balance = response.json()["credit_balance"]
    
    def test_lecture_tarot_deducts_10_credits(self):
        """POST /api/credits/use for lecture_tarot - deducts 10 credits"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "lecture_tarot"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        expected_balance = self.initial_balance - 10
        assert data.get("credit_balance") == expected_balance, f"Expected {expected_balance}, got {data['credit_balance']}"
        print(f"PASS: Lecture Tarot deducts 10 credits - balance: {data['credit_balance']}")


class TestCreditUseNumerologie:
    """Test credit deduction for numerologie - 10 credits"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a fresh user for each test"""
        self.email = f"test_numero_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.email,
            "password": "TestPass123!",
            "birth_date": "1985-11-11",
            "birth_time": "22:00",
            "birth_place": "Strasbourg",
            "birth_country": "France"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.initial_balance = response.json()["credit_balance"]
    
    def test_numerologie_deducts_10_credits(self):
        """POST /api/credits/use for numerologie - deducts 10 credits"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "numerologie"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        expected_balance = self.initial_balance - 10
        assert data.get("credit_balance") == expected_balance, f"Expected {expected_balance}, got {data['credit_balance']}"
        print(f"PASS: Numerologie deducts 10 credits - balance: {data['credit_balance']}")


class TestCreditUseLectureAstrologique:
    """Test credit deduction for lecture_astrologique (Compatibilité) - 10 credits"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a fresh user for each test"""
        self.email = f"test_astro_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.email,
            "password": "TestPass123!",
            "birth_date": "1998-02-14",
            "birth_time": "06:30",
            "birth_place": "Toulouse",
            "birth_country": "France"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.initial_balance = response.json()["credit_balance"]
    
    def test_lecture_astrologique_deducts_10_credits(self):
        """POST /api/credits/use for lecture_astrologique - deducts 10 credits"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "lecture_astrologique"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        expected_balance = self.initial_balance - 10
        assert data.get("credit_balance") == expected_balance, f"Expected {expected_balance}, got {data['credit_balance']}"
        print(f"PASS: Lecture Astrologique deducts 10 credits - balance: {data['credit_balance']}")


class TestCreditUseCartographiePremium:
    """Test credit deduction for cartographie_premium - 60 credits"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create a fresh user for each test"""
        self.email = f"test_premium_{uuid.uuid4().hex[:8]}@plume.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.email,
            "password": "TestPass123!",
            "birth_date": "2000-01-01",
            "birth_time": "00:00",
            "birth_place": "Nantes",
            "birth_country": "France"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.initial_balance = response.json()["credit_balance"]  # 20
    
    def test_cartographie_premium_insufficient_credits(self):
        """POST /api/credits/use for cartographie_premium - returns 402 when insufficient (20 < 60)"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "cartographie_premium"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 402, f"Expected 402 (insufficient credits), got {response.status_code}: {response.text}"
        print(f"PASS: Cartographie Premium returns 402 when insufficient credits (has 20, needs 60)")


class TestCreditPacks:
    """Test credit packs endpoint"""
    
    def test_get_credit_packs(self):
        """GET /api/credits/packs - returns 3 packs with correct values"""
        response = requests.get(f"{BASE_URL}/api/credits/packs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        packs = data.get("packs", [])
        assert len(packs) == 3, f"Expected 3 packs, got {len(packs)}"
        
        # Verify pack contents
        pack_ids = {p["id"]: p for p in packs}
        
        # Pack Découverte
        assert "decouverte" in pack_ids
        assert pack_ids["decouverte"]["credits"] == 10
        assert pack_ids["decouverte"]["amount"] == 9.00
        
        # Pack Exploration
        assert "exploration" in pack_ids
        assert pack_ids["exploration"]["credits"] == 50
        assert pack_ids["exploration"]["amount"] == 24.99
        
        # Pack Premium
        assert "premium" in pack_ids
        assert pack_ids["premium"]["credits"] == 100
        assert pack_ids["premium"]["amount"] == 44.99
        
        print(f"PASS: Credit packs endpoint returns 3 correct packs")


class TestServiceCosts:
    """Test service costs endpoint"""
    
    def test_get_service_costs(self):
        """GET /api/credits/service-costs - returns correct service costs"""
        response = requests.get(f"{BASE_URL}/api/credits/service-costs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        costs = data.get("costs", {})
        
        assert costs.get("tarot_oui_non") == 2, f"Expected tarot_oui_non cost 2, got {costs.get('tarot_oui_non')}"
        assert costs.get("lecture_tarot") == 10, f"Expected lecture_tarot cost 10, got {costs.get('lecture_tarot')}"
        assert costs.get("numerologie") == 10, f"Expected numerologie cost 10, got {costs.get('numerologie')}"
        assert costs.get("lecture_astrologique") == 10, f"Expected lecture_astrologique cost 10, got {costs.get('lecture_astrologique')}"
        assert costs.get("cartographie_premium") == 60, f"Expected cartographie_premium cost 60, got {costs.get('cartographie_premium')}"
        
        print(f"PASS: Service costs endpoint returns correct costs")


class TestCreditUseUnknownService:
    """Test credit use with unknown service"""
    
    def test_unknown_service_returns_400(self):
        """POST /api/credits/use - returns 400 for unknown service"""
        # Register user first
        email = f"test_unknown_{uuid.uuid4().hex[:8]}@plume.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "birth_date": "1990-06-15",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_country": "France"
        })
        token = reg_response.json()["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "unknown_service"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASS: Unknown service returns 400")


class TestCreditUseAuthRequired:
    """Test credit use without authentication"""
    
    def test_use_credits_without_auth_returns_401(self):
        """POST /api/credits/use - returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/credits/use",
            json={"service_id": "tarot_oui_non"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Credit use without auth returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
