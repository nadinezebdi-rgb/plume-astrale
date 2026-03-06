"""
Iteration 22 - Streak System Tests
Tests for daily check-in streak with milestone bonuses
- GET /api/streak/status: returns streak_count, checked_in_today, next_milestone (requires auth)
- POST /api/streak/checkin: first checkin gives streak_count=1, credits_earned=1; second same-day gives already_checked_in=true
- Credits are added to wallet after checkin
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials - fresh user for streak testing
TEST_EMAIL = f"streaktest_{uuid.uuid4().hex[:8]}@plume.fr"
TEST_PASSWORD = "TestStreak123!"


class TestStreakSystem:
    """Test streak system - daily check-in with milestone bonuses"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Register a fresh user and get auth token"""
        # Register new user
        register_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "birth_date": "1995-03-15",
            "birth_time": "14:30",
            "birth_place": "Lyon",
            "birth_country": "France"
        })
        
        if register_response.status_code == 200:
            data = register_response.json()
            print(f"Registered new user: {TEST_EMAIL}")
            return data.get("token")
        elif register_response.status_code == 400:
            # User might exist, try login
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            if login_response.status_code == 200:
                return login_response.json().get("token")
            pytest.skip(f"Could not authenticate: {login_response.text}")
        else:
            pytest.skip(f"Registration failed: {register_response.text}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    # ==================== STREAK STATUS TESTS ====================
    
    def test_streak_status_requires_auth(self, session):
        """Test GET /api/streak/status requires authentication"""
        response = session.get(f"{BASE_URL}/api/streak/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Streak status requires authentication")
    
    def test_streak_status_initial(self, session, auth_headers):
        """Test GET /api/streak/status returns initial state for new user"""
        response = session.get(f"{BASE_URL}/api/streak/status", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "streak_count" in data, "Missing streak_count"
        assert "checked_in_today" in data, "Missing checked_in_today"
        assert "next_milestone" in data, "Missing next_milestone"
        assert "longest_streak" in data, "Missing longest_streak"
        assert "total_checkins" in data, "Missing total_checkins"
        
        # For new user, streak_count should be 0, checked_in_today should be False
        assert data["streak_count"] == 0, f"Expected streak_count=0 for new user, got {data['streak_count']}"
        assert data["checked_in_today"] == False, f"Expected checked_in_today=False for new user"
        
        # Next milestone should be day 7 with bonus 3
        assert data["next_milestone"]["days"] == 7, f"Expected next milestone day 7, got {data['next_milestone']}"
        assert data["next_milestone"]["bonus"] == 3, f"Expected next milestone bonus 3"
        
        print(f"PASS: Initial streak status correct: {data}")
    
    # ==================== CHECKIN TESTS ====================
    
    def test_checkin_requires_auth(self, session):
        """Test POST /api/streak/checkin requires authentication"""
        response = session.post(f"{BASE_URL}/api/streak/checkin")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Checkin requires authentication")
    
    def test_first_checkin_success(self, session, auth_headers):
        """Test POST /api/streak/checkin - first checkin gives streak_count=1, credits_earned=1"""
        # Get initial wallet balance
        wallet_response = session.get(f"{BASE_URL}/api/wallet/balance", headers=auth_headers)
        assert wallet_response.status_code == 200
        initial_balance = wallet_response.json().get("credit_balance", 0)
        print(f"Initial balance: {initial_balance}")
        
        # Perform first checkin
        response = session.post(f"{BASE_URL}/api/streak/checkin", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "already_checked_in" in data, "Missing already_checked_in"
        assert "streak_count" in data, "Missing streak_count"
        assert "credits_earned" in data, "Missing credits_earned"
        assert "next_milestone" in data, "Missing next_milestone"
        assert "credit_balance" in data, "Missing credit_balance"
        
        # First checkin should NOT be already_checked_in
        assert data["already_checked_in"] == False, "First checkin should not be already_checked_in"
        
        # First checkin should give streak_count=1
        assert data["streak_count"] == 1, f"Expected streak_count=1, got {data['streak_count']}"
        
        # First checkin should give credits_earned=1 (daily credit)
        assert data["credits_earned"] == 1, f"Expected credits_earned=1, got {data['credits_earned']}"
        
        # No milestone bonus on day 1
        assert data.get("milestone_bonus", 0) == 0, f"Expected no milestone bonus on day 1"
        
        # Verify credits were added to wallet
        expected_balance = initial_balance + 1
        assert data["credit_balance"] == expected_balance, f"Expected balance {expected_balance}, got {data['credit_balance']}"
        
        print(f"PASS: First checkin successful: streak={data['streak_count']}, credits={data['credits_earned']}, balance={data['credit_balance']}")
    
    def test_second_checkin_same_day_blocked(self, session, auth_headers):
        """Test POST /api/streak/checkin - second same-day checkin gives already_checked_in=true"""
        response = session.post(f"{BASE_URL}/api/streak/checkin", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Second checkin same day should return already_checked_in=true
        assert data["already_checked_in"] == True, f"Expected already_checked_in=True for second checkin same day"
        
        # Should give 0 credits
        assert data["credits_earned"] == 0, f"Expected credits_earned=0 for same-day duplicate, got {data['credits_earned']}"
        
        # Streak count should still be 1
        assert data["streak_count"] == 1, f"Expected streak_count=1, got {data['streak_count']}"
        
        print(f"PASS: Second same-day checkin blocked correctly: already_checked_in={data['already_checked_in']}, credits={data['credits_earned']}")
    
    def test_streak_status_after_checkin(self, session, auth_headers):
        """Test GET /api/streak/status after checkin shows correct state"""
        response = session.get(f"{BASE_URL}/api/streak/status", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # After first checkin
        assert data["streak_count"] == 1, f"Expected streak_count=1, got {data['streak_count']}"
        assert data["checked_in_today"] == True, f"Expected checked_in_today=True"
        assert data["total_checkins"] == 1, f"Expected total_checkins=1, got {data['total_checkins']}"
        assert data["longest_streak"] == 1, f"Expected longest_streak=1, got {data['longest_streak']}"
        
        # Next milestone should still be day 7
        assert data["next_milestone"]["days"] == 7
        assert data["next_milestone"]["remaining"] == 6, f"Expected remaining=6, got {data['next_milestone']['remaining']}"
        
        print(f"PASS: Streak status after checkin: {data}")
    
    def test_wallet_balance_increased(self, session, auth_headers):
        """Test that wallet balance increased after checkin"""
        response = session.get(f"{BASE_URL}/api/wallet/balance", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # New user gets 20 bonus credits + 1 from checkin = 21
        # But if user already existed, just check it's at least 1
        assert data["credit_balance"] >= 1, f"Expected credit_balance >= 1, got {data['credit_balance']}"
        
        print(f"PASS: Wallet balance after checkin: {data['credit_balance']}")
    
    def test_transactions_show_checkin(self, session, auth_headers):
        """Test that transaction history shows the checkin credit"""
        response = session.get(f"{BASE_URL}/api/wallet/transactions", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        transactions = data.get("transactions", [])
        
        # Find the checkin transaction
        checkin_tx = None
        for tx in transactions:
            if "Check-in" in tx.get("description", ""):
                checkin_tx = tx
                break
        
        assert checkin_tx is not None, "Expected to find check-in transaction in history"
        assert checkin_tx["credits_amount"] == 1, f"Expected checkin credits_amount=1, got {checkin_tx['credits_amount']}"
        # Type is 'purchase' for adding credits (from add_credits function)
        assert checkin_tx["type"] in ["purchase", "credit", "bonus"], f"Expected valid type, got {checkin_tx['type']}"
        
        print(f"PASS: Transaction history shows checkin: {checkin_tx}")


class TestStreakMilestones:
    """Test streak milestone definitions (7, 14, 30, 60, 100 days)"""
    
    def test_milestone_bonuses_defined(self):
        """Verify milestone bonuses are correctly defined"""
        # These are the expected milestones from the requirement
        expected_milestones = {
            7: 3,    # Day 7: +3 credits bonus
            14: 5,   # Day 14: +5 credits bonus
            30: 10,  # Day 30: +10 credits bonus
            60: 15,  # Day 60: +15 credits bonus
            100: 25, # Day 100: +25 credits bonus
        }
        
        # Import from streak_service to verify
        import sys
        sys.path.insert(0, '/app/backend')
        from services.streak_service import STREAK_MILESTONES, DAILY_CHECKIN_CREDIT
        
        assert STREAK_MILESTONES == expected_milestones, f"Milestones mismatch: {STREAK_MILESTONES}"
        assert DAILY_CHECKIN_CREDIT == 1, f"Daily credit should be 1, got {DAILY_CHECKIN_CREDIT}"
        
        print(f"PASS: Milestone bonuses correctly defined: {STREAK_MILESTONES}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
