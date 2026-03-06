"""
Iteration 23 - Homepage Feature Tests
Tests for the newly redesigned homepage with cosmic features:
1. Daily Tarot API endpoint
2. User registration with 20 bonus credits
3. Base API accessibility
"""

import pytest
import requests
import os
import uuid

# Base URL from environment - NO default, fail fast if missing
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://astral-credits.preview.emergentagent.com"


class TestApiHealthCheck:
    """Test basic API health and accessibility"""
    
    def test_api_root_returns_200(self):
        """GET /api/ returns 200 and Hello World message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data
        assert data["message"] == "Hello World"
        print("SUCCESS: /api/ returns 200 with Hello World message")


class TestDailyTarotEndpoint:
    """Test /api/tarot/jour endpoint for daily tarot card"""
    
    def test_tarot_jour_returns_200(self):
        """GET /api/tarot/jour returns 200"""
        response = requests.get(f"{BASE_URL}/api/tarot/jour")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("SUCCESS: /api/tarot/jour returns 200")
    
    def test_tarot_jour_returns_valid_data(self):
        """GET /api/tarot/jour returns valid tarot data structure"""
        response = requests.get(f"{BASE_URL}/api/tarot/jour")
        assert response.status_code == 200
        data = response.json()
        
        # Check success flag
        assert data.get("success") is True, "Expected success=True"
        
        # Check data structure
        assert "data" in data, "Missing 'data' field"
        tirage_data = data["data"]
        
        # Check required fields
        assert "type" in tirage_data, "Missing 'type' field"
        assert "date" in tirage_data, "Missing 'date' field"
        assert "date_fr" in tirage_data, "Missing 'date_fr' field"
        assert "carte" in tirage_data, "Missing 'carte' field"
        print(f"SUCCESS: Tarot du jour data structure valid - {tirage_data.get('type')}")
    
    def test_tarot_jour_carte_has_required_fields(self):
        """Verify the carte object has all required fields"""
        response = requests.get(f"{BASE_URL}/api/tarot/jour")
        assert response.status_code == 200
        data = response.json()
        carte = data["data"]["carte"]
        
        required_fields = ["numero", "nom", "orientation", "orientation_fr", 
                          "element", "planete", "interpretation_generale"]
        
        for field in required_fields:
            assert field in carte, f"Missing required field: {field}"
        
        # Verify orientation is valid
        assert carte["orientation"] in ["droit", "renverse"], \
            f"Invalid orientation: {carte['orientation']}"
        
        print(f"SUCCESS: Carte '{carte['nom']}' has all required fields - {carte['orientation_fr']}")
    
    def test_tarot_jour_has_message_energie(self):
        """Verify the tirage has message_energie for UI display"""
        response = requests.get(f"{BASE_URL}/api/tarot/jour")
        assert response.status_code == 200
        data = response.json()
        tirage_data = data["data"]
        
        assert "message_energie" in tirage_data, "Missing 'message_energie' field"
        assert len(tirage_data["message_energie"]) > 0, "message_energie is empty"
        print(f"SUCCESS: message_energie present: '{tirage_data['message_energie'][:50]}...'")
    
    def test_tarot_jour_has_affirmation_du_jour(self):
        """Verify affirmation_du_jour is present"""
        response = requests.get(f"{BASE_URL}/api/tarot/jour")
        assert response.status_code == 200
        data = response.json()
        tirage_data = data["data"]
        
        assert "affirmation_du_jour" in tirage_data, "Missing 'affirmation_du_jour' field"
        assert len(tirage_data["affirmation_du_jour"]) > 0, "affirmation_du_jour is empty"
        print(f"SUCCESS: affirmation_du_jour present")


class TestUserRegistration:
    """Test user registration with 20 bonus credits"""
    
    def test_registration_returns_201_or_200(self):
        """POST /api/auth/register returns success with token"""
        unique_email = f"test_iter23_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "birth_place": "Paris",
            "birth_country": "France"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        # FastAPI returns 200 for successful registration in this app
        assert response.status_code in [200, 201], \
            f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Missing token in response"
        assert "user" in data, "Missing user in response"
        print(f"SUCCESS: Registration returns token for {unique_email}")
    
    def test_registration_gives_20_bonus_credits(self):
        """New user registration gives exactly 20 bonus credits"""
        unique_email = f"test_credits23_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1995-08-20",
            "birth_time": "10:00",
            "birth_place": "Lyon",
            "birth_country": "France"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code in [200, 201]
        
        data = response.json()
        assert "credit_balance" in data, "Missing credit_balance in response"
        assert data["credit_balance"] == 20, \
            f"Expected 20 bonus credits, got {data['credit_balance']}"
        
        print(f"SUCCESS: New user receives 20 bonus credits")
    
    def test_registration_user_data_stored(self):
        """Verify user data is correctly stored and returned"""
        unique_email = f"test_profile23_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1988-12-25",
            "birth_time": "08:15",
            "birth_place": "Marseille",
            "birth_country": "France"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code in [200, 201]
        
        data = response.json()
        user = data["user"]
        
        assert user["email"] == unique_email, "Email mismatch"
        assert user["birth_date"] == payload["birth_date"], "Birth date mismatch"
        assert user["birth_time"] == payload["birth_time"], "Birth time mismatch"
        assert user["birth_place"] == payload["birth_place"], "Birth place mismatch"
        
        print(f"SUCCESS: User profile data correctly stored")
    
    def test_duplicate_email_rejected(self):
        """Duplicate email registration is rejected"""
        unique_email = f"test_dup23_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_country": "France"
        }
        
        # First registration
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response1.status_code in [200, 201]
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response2.status_code == 400, \
            f"Expected 400 for duplicate, got {response2.status_code}"
        
        print("SUCCESS: Duplicate email correctly rejected with 400")


class TestLoginFlow:
    """Test login functionality"""
    
    def test_login_with_valid_credentials(self):
        """Login with valid credentials returns token and balance"""
        # First register a user
        unique_email = f"test_login23_{uuid.uuid4().hex[:8]}@test.com"
        password = "TestPass123!"
        
        register_payload = {
            "email": unique_email,
            "password": password,
            "birth_date": "1992-06-15",
            "birth_time": "16:30",
            "birth_place": "Nice",
            "birth_country": "France"
        }
        
        requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        
        # Now login
        login_payload = {"email": unique_email, "password": password}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "token" in data, "Missing token"
        assert "user" in data, "Missing user"
        assert "credit_balance" in data, "Missing credit_balance"
        
        print("SUCCESS: Login returns token, user, and credit_balance")
    
    def test_login_invalid_credentials_rejected(self):
        """Login with invalid credentials returns 401"""
        login_payload = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        assert response.status_code == 401, \
            f"Expected 401 for invalid credentials, got {response.status_code}"
        
        print("SUCCESS: Invalid credentials correctly rejected with 401")


class TestShareCardGeneration:
    """Test shareable card generation endpoint"""
    
    def test_share_card_without_auth_still_generates(self):
        """POST /api/share/generate-card generates card even without auth (public endpoint)"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": {"prenom": "Test", "dateNaissance": "1990-01-01"}}
        )
        
        # Endpoint is public and generates a generic card
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"
        
        print("SUCCESS: Share card endpoint is accessible (public or auth)")
    
    def test_share_card_with_auth(self):
        """POST /api/share/generate-card with auth returns image"""
        # Register and get token
        unique_email = f"test_share23_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "birth_place": "Paris",
            "birth_country": "France"
        })
        
        token = reg_response.json()["token"]
        
        # Generate share card
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": {
                "prenom": "TestUser",
                "dateNaissance": "1990-05-15",
                "heureNaissance": "14:30",
                "ville": "Paris"
            }},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify content type is image
        content_type = response.headers.get("Content-Type", "")
        assert "image" in content_type or "octet-stream" in content_type, \
            f"Expected image content type, got {content_type}"
        
        print("SUCCESS: Share card generation works with authentication")


class TestServiceCosts:
    """Test service costs endpoint"""
    
    def test_get_service_costs(self):
        """GET /api/credits/service-costs returns costs"""
        response = requests.get(f"{BASE_URL}/api/credits/service-costs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "costs" in data, "Missing 'costs' field"
        
        costs = data["costs"]
        expected_services = ["tarot_oui_non", "lecture_tarot", "numerologie"]
        
        for service in expected_services:
            assert service in costs, f"Missing service: {service}"
        
        print(f"SUCCESS: Service costs returned: {costs}")


class TestCreditPacks:
    """Test credit packs endpoint"""
    
    def test_get_credit_packs(self):
        """GET /api/credits/packs returns available packs"""
        response = requests.get(f"{BASE_URL}/api/credits/packs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "packs" in data, "Missing 'packs' field"
        
        packs = data["packs"]
        assert len(packs) >= 3, f"Expected at least 3 packs, got {len(packs)}"
        
        # Verify pack structure
        for pack in packs:
            assert "id" in pack, "Missing pack id"
            assert "name" in pack, "Missing pack name"
            assert "credits" in pack, "Missing pack credits"
            assert "amount" in pack, "Missing pack amount"
        
        print(f"SUCCESS: {len(packs)} credit packs returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
