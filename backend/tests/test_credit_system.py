"""
Credit System Backend Tests - Iteration 19
Tests for: Auth (register, login, me), Wallet (balance, transactions), 
Credits (packs, service-costs, checkout, use, check-free-tarot)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com')

# Test user credentials for this iteration
TEST_EMAIL = f"test_iter19_{uuid.uuid4().hex[:8]}@plume.com"
TEST_PASSWORD = "Pass123456"
TEST_BIRTH_DATE = "1990-05-15"
TEST_BIRTH_TIME = "14:30"
TEST_BIRTH_PLACE = "Paris"
TEST_BIRTH_COUNTRY = "France"


class TestPublicEndpoints:
    """Test public endpoints (no auth required)"""
    
    def test_root_endpoint(self):
        """GET / - should return hello world"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"Root endpoint: {data}")
    
    def test_get_credit_packs(self):
        """GET /api/credits/packs - should return 3 credit packs"""
        response = requests.get(f"{BASE_URL}/api/credits/packs")
        assert response.status_code == 200
        data = response.json()
        assert "packs" in data
        packs = data["packs"]
        assert len(packs) == 3, f"Expected 3 packs, got {len(packs)}"
        
        # Verify pack IDs
        pack_ids = [p["id"] for p in packs]
        assert "decouverte" in pack_ids
        assert "exploration" in pack_ids
        assert "premium" in pack_ids
        
        # Verify Découverte pack: 10 credits, 9€
        decouverte = next(p for p in packs if p["id"] == "decouverte")
        assert decouverte["credits"] == 10
        assert decouverte["amount"] == 9.00
        assert decouverte["currency"] == "eur"
        
        # Verify Exploration pack: 50 credits, 24.99€
        exploration = next(p for p in packs if p["id"] == "exploration")
        assert exploration["credits"] == 50
        assert exploration["amount"] == 24.99
        
        # Verify Premium pack: 100 credits, 44.99€
        premium = next(p for p in packs if p["id"] == "premium")
        assert premium["credits"] == 100
        assert premium["amount"] == 44.99
        
        print(f"Credit packs: {packs}")
    
    def test_get_service_costs(self):
        """GET /api/credits/service-costs - should return service costs"""
        response = requests.get(f"{BASE_URL}/api/credits/service-costs")
        assert response.status_code == 200
        data = response.json()
        assert "costs" in data
        costs = data["costs"]
        
        # Verify tarot_oui_non costs 2 credits
        assert costs.get("tarot_oui_non") == 2
        print(f"Service costs: {costs}")


class TestUserRegistration:
    """Test user registration flow"""
    
    @pytest.fixture(scope="class")
    def registered_user(self):
        """Register a new test user and return auth data"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        return response.json()
    
    def test_registration_returns_token(self, registered_user):
        """POST /api/auth/register - should return JWT token"""
        assert "token" in registered_user
        assert isinstance(registered_user["token"], str)
        assert len(registered_user["token"]) > 10
        print(f"Token received: {registered_user['token'][:20]}...")
    
    def test_registration_returns_user_profile(self, registered_user):
        """POST /api/auth/register - should return user profile with astro data"""
        assert "user" in registered_user
        user = registered_user["user"]
        assert user["email"] == TEST_EMAIL.lower()
        assert user["birth_date"] == TEST_BIRTH_DATE
        assert user["birth_time"] == TEST_BIRTH_TIME
        assert user["birth_place"] == TEST_BIRTH_PLACE
        assert user["birth_country"] == TEST_BIRTH_COUNTRY
        assert "id" in user
        print(f"User profile: {user}")
    
    def test_registration_gives_20_bonus_credits(self, registered_user):
        """POST /api/auth/register - should give 20 bonus credits"""
        assert "credit_balance" in registered_user
        assert registered_user["credit_balance"] == 20
        print(f"Credit balance after registration: {registered_user['credit_balance']}")
    
    def test_duplicate_registration_fails(self, registered_user):
        """POST /api/auth/register - should fail with duplicate email"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert response.status_code == 400
        assert "déjà utilisé" in response.json().get("detail", "").lower()
        print(f"Duplicate registration correctly rejected")


class TestUserLogin:
    """Test user login flow"""
    
    @pytest.fixture(scope="class")
    def login_test_user(self):
        """Register a user for login tests"""
        email = f"login_test_{uuid.uuid4().hex[:8]}@plume.com"
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert register_resp.status_code == 200
        return {"email": email, "password": TEST_PASSWORD, "reg_data": register_resp.json()}
    
    def test_login_success(self, login_test_user):
        """POST /api/auth/login - should return JWT and credit balance"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": login_test_user["email"],
            "password": login_test_user["password"],
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert "user" in data
        assert "credit_balance" in data
        assert data["user"]["email"] == login_test_user["email"].lower()
        assert data["credit_balance"] == 20  # Registration bonus
        print(f"Login successful, balance: {data['credit_balance']}")
    
    def test_login_invalid_password(self, login_test_user):
        """POST /api/auth/login - should fail with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": login_test_user["email"],
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        print("Invalid password correctly rejected")
    
    def test_login_nonexistent_user(self):
        """POST /api/auth/login - should fail for non-existent user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": TEST_PASSWORD,
        })
        assert response.status_code == 401
        print("Non-existent user correctly rejected")


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""
    
    @pytest.fixture(scope="class")
    def auth_user(self):
        """Create an authenticated user"""
        email = f"auth_test_{uuid.uuid4().hex[:8]}@plume.com"
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert register_resp.status_code == 200
        data = register_resp.json()
        return {"token": data["token"], "user": data["user"], "initial_balance": data["credit_balance"]}
    
    def test_get_me_returns_profile(self, auth_user):
        """GET /api/auth/me - should return user profile + credit balance"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {auth_user['token']}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "credit_balance" in data
        assert data["credit_balance"] == 20  # Registration bonus
        print(f"GET /me: balance = {data['credit_balance']}")
    
    def test_get_me_without_auth_fails(self):
        """GET /api/auth/me - should fail without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("Unauthenticated /me correctly rejected")
    
    def test_wallet_balance(self, auth_user):
        """GET /api/wallet/balance - should return credit balance"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers={
            "Authorization": f"Bearer {auth_user['token']}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "credit_balance" in data
        assert data["credit_balance"] == 20
        print(f"Wallet balance: {data['credit_balance']}")
    
    def test_wallet_transactions(self, auth_user):
        """GET /api/wallet/transactions - should return transaction history"""
        response = requests.get(f"{BASE_URL}/api/wallet/transactions", headers={
            "Authorization": f"Bearer {auth_user['token']}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        
        # Should have at least the registration bonus transaction
        txs = data["transactions"]
        assert len(txs) >= 1
        
        # Find the registration bonus transaction
        bonus_tx = next((t for t in txs if "inscription" in t.get("description", "").lower()), None)
        assert bonus_tx is not None, "Registration bonus transaction not found"
        assert bonus_tx["credits_amount"] == 20
        print(f"Transactions: {len(txs)} found, bonus tx: {bonus_tx}")
    
    def test_check_free_tarot_not_used(self, auth_user):
        """GET /api/credits/check-free-tarot - should be false for new user"""
        response = requests.get(f"{BASE_URL}/api/credits/check-free-tarot", headers={
            "Authorization": f"Bearer {auth_user['token']}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "free_used" in data
        assert data["free_used"] is False
        print(f"Free tarot used: {data['free_used']}")


class TestCreditUsage:
    """Test credit usage for services"""
    
    @pytest.fixture(scope="class")
    def credit_user(self):
        """Create a user for credit usage tests"""
        email = f"credit_test_{uuid.uuid4().hex[:8]}@plume.com"
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert register_resp.status_code == 200
        data = register_resp.json()
        return {"token": data["token"], "user_id": data["user"]["id"]}
    
    def test_first_tarot_free(self, credit_user):
        """POST /api/credits/use - first tarot_oui_non should be free"""
        response = requests.post(f"{BASE_URL}/api/credits/use", 
            json={"service_id": "tarot_oui_non"},
            headers={"Authorization": f"Bearer {credit_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["free_draw"] is True
        assert data["credit_balance"] == 20  # No deduction
        print(f"First tarot free: balance = {data['credit_balance']}")
    
    def test_second_tarot_costs_credits(self, credit_user):
        """POST /api/credits/use - second tarot_oui_non costs 2 credits"""
        # Check free tarot is now used
        check_resp = requests.get(f"{BASE_URL}/api/credits/check-free-tarot", headers={
            "Authorization": f"Bearer {credit_user['token']}"
        })
        assert check_resp.status_code == 200
        assert check_resp.json()["free_used"] is True
        
        # Second usage should cost credits
        response = requests.post(f"{BASE_URL}/api/credits/use", 
            json={"service_id": "tarot_oui_non"},
            headers={"Authorization": f"Bearer {credit_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["free_draw"] is False
        assert data["credit_balance"] == 18  # 20 - 2
        print(f"Second tarot charged: balance = {data['credit_balance']}")
    
    def test_invalid_service_fails(self, credit_user):
        """POST /api/credits/use - unknown service should fail"""
        response = requests.post(f"{BASE_URL}/api/credits/use", 
            json={"service_id": "unknown_service"},
            headers={"Authorization": f"Bearer {credit_user['token']}"}
        )
        assert response.status_code == 400
        print("Unknown service correctly rejected")


class TestCreditCheckout:
    """Test Stripe checkout for credit packs"""
    
    @pytest.fixture(scope="class")
    def checkout_user(self):
        """Create a user for checkout tests"""
        email = f"checkout_test_{uuid.uuid4().hex[:8]}@plume.com"
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "birth_date": TEST_BIRTH_DATE,
            "birth_time": TEST_BIRTH_TIME,
            "birth_place": TEST_BIRTH_PLACE,
            "birth_country": TEST_BIRTH_COUNTRY,
        })
        assert register_resp.status_code == 200
        data = register_resp.json()
        return {"token": data["token"]}
    
    def test_create_checkout_session(self, checkout_user):
        """POST /api/credits/checkout - should create Stripe session"""
        response = requests.post(f"{BASE_URL}/api/credits/checkout", 
            json={
                "pack_id": "decouverte",
                "origin_url": "https://consultation-astro.preview.emergentagent.com"
            },
            headers={"Authorization": f"Bearer {checkout_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "session_id" in data
        assert "checkout.stripe.com" in data["url"] or "stripe.com" in data["url"]
        print(f"Checkout session created: {data['session_id']}")
    
    def test_checkout_invalid_pack_fails(self, checkout_user):
        """POST /api/credits/checkout - invalid pack should fail"""
        response = requests.post(f"{BASE_URL}/api/credits/checkout", 
            json={
                "pack_id": "invalid_pack",
                "origin_url": "https://consultation-astro.preview.emergentagent.com"
            },
            headers={"Authorization": f"Bearer {checkout_user['token']}"}
        )
        assert response.status_code == 400
        print("Invalid pack correctly rejected")
    
    def test_checkout_without_auth_fails(self):
        """POST /api/credits/checkout - should fail without auth"""
        response = requests.post(f"{BASE_URL}/api/credits/checkout", 
            json={
                "pack_id": "decouverte",
                "origin_url": "https://consultation-astro.preview.emergentagent.com"
            }
        )
        assert response.status_code == 401
        print("Unauthenticated checkout correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
