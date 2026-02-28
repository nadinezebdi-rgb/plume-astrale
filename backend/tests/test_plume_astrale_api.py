"""
Backend API Tests for Plume Astrale - Astrology Theme Generator
Tests: Discount validation, Astrology API, PDF generation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://thema-enhanced.preview.emergentagent.com')

# Test data based on provided test context
TEST_USER_DATA = {
    "prenom": "Marie",
    "dateNaissance": "1990-06-15",
    "heureNaissance": "14:30",
    "ville": "Paris",
    "pays": "France"
}


class TestHealthAndRoot:
    """Basic health and root endpoint tests"""
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Root endpoint returns: {data}")

    def test_products_endpoint(self):
        """Test products listing"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "manuscrit" in data
        assert data["manuscrit"]["amount"] == 29.90
        print(f"✓ Products endpoint returns manuscrit at {data['manuscrit']['amount']}€")


class TestDiscountValidation:
    """Tests for discount code validation"""
    
    def test_valid_promo_code_astro100(self):
        """Test ASTRO100 promo code gives 100% discount"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "ASTRO100"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        assert "Accès gratuit complet" in data["message"]
        print(f"✓ ASTRO100 code validated: {data}")

    def test_invalid_promo_code(self):
        """Test invalid promo code returns invalid response"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALID123"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert data["discount_percent"] is None
        print(f"✓ Invalid code correctly rejected: {data}")

    def test_promo_code_case_insensitive(self):
        """Test promo code is case insensitive"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "astro100"},  # lowercase
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        print("✓ Promo code is case insensitive")


class TestFreeAccess:
    """Tests for free access endpoint with ASTRO100"""
    
    def test_free_access_with_astro100(self):
        """Test granting free access with ASTRO100 code"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "manuscrit",
                "origin_url": "https://thema-enhanced.preview.emergentagent.com",
                "user_email": "test@example.com",
                "user_data": TEST_USER_DATA,
                "discount_code": "ASTRO100"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "redirect_url" in data
        print(f"✓ Free access granted: {data}")

    def test_free_access_without_code(self):
        """Test free access fails without discount code"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "manuscrit",
                "origin_url": "https://thema-enhanced.preview.emergentagent.com",
                "user_email": "test@example.com",
                "user_data": TEST_USER_DATA
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Free access correctly rejected without code")


class TestAstrologyAPI:
    """Tests for astrology API endpoints"""
    
    def test_planets_endpoint(self):
        """Test POST /api/astrology/planets returns planetary data"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/planets",
            json={
                "date_naissance": TEST_USER_DATA["dateNaissance"],
                "heure_naissance": TEST_USER_DATA["heureNaissance"],
                "ville": TEST_USER_DATA["ville"],
                "pays": TEST_USER_DATA["pays"]
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        # Verify planets data structure
        planets = data["data"]
        assert isinstance(planets, list)
        assert len(planets) > 0
        # Check for Sun planet
        sun_data = next((p for p in planets if p.get("name") == "Sun"), None)
        assert sun_data is not None
        assert "sign" in sun_data
        print(f"✓ Planets endpoint returns data with {len(planets)} planets")
        print(f"  Sun sign: {sun_data.get('sign')}")

    def test_horoscope_endpoint(self):
        """Test POST /api/astrology/horoscope returns horoscope data"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/horoscope",
            json={
                "date_naissance": TEST_USER_DATA["dateNaissance"],
                "heure_naissance": TEST_USER_DATA["heureNaissance"],
                "ville": TEST_USER_DATA["ville"],
                "pays": TEST_USER_DATA["pays"]
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "zodiac_sign" in data
        assert "zodiac_french" in data
        assert "data" in data
        print(f"✓ Horoscope endpoint returns: zodiac_sign={data['zodiac_sign']}, french={data['zodiac_french']}")

    def test_zodiac_from_date(self):
        """Test GET /api/astrology/zodiac/{date} returns zodiac sign"""
        response = requests.get(f"{BASE_URL}/api/astrology/zodiac/1990-06-15")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["zodiac_sign"] == "gemini"
        assert data["zodiac_french"] == "Gémeaux"
        print(f"✓ Zodiac from date: {data}")


class TestPDFGeneration:
    """Tests for PDF generation endpoint"""
    
    def test_pdf_generate_endpoint(self):
        """Test POST /api/pdf/generate returns valid PDF"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        # Check content type is PDF
        assert "application/pdf" in response.headers.get("Content-Type", "")
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "manuscrit_plume_Marie.pdf" in content_disp
        # Check PDF starts with PDF magic bytes
        assert response.content[:4] == b'%PDF'
        # Check PDF has reasonable size (at least 10KB for a multi-page document)
        assert len(response.content) > 10000
        print(f"✓ PDF generated successfully: {len(response.content)} bytes")

    def test_pdf_generate_without_prenom(self):
        """Test PDF generation without prenom (optional field)"""
        user_data = {
            "dateNaissance": "1990-06-15",
            "heureNaissance": "14:30",
            "ville": "Paris"
        }
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": user_data},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("Content-Type", "")
        print("✓ PDF generated without prenom")


class TestDailyHoroscope:
    """Tests for daily horoscope endpoints"""
    
    def test_daily_horoscope_gemini(self):
        """Test daily horoscope for Gemini"""
        response = requests.get(f"{BASE_URL}/api/astrology/daily/gemini")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "zodiac_sign" in data
        assert data["zodiac_french"] == "Gémeaux"
        print(f"✓ Daily horoscope for Gemini received")

    def test_weekly_horoscope_gemini(self):
        """Test weekly horoscope for Gemini"""
        response = requests.get(f"{BASE_URL}/api/astrology/weekly/gemini")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Weekly horoscope for Gemini received")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
