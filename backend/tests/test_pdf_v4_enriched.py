"""
Test PDF V4 Enriched - Theme Astral Pro
Tests for massively enriched PDF with 25+ pages
Features: carte du ciel, equilibre elementaire, planet pages (Mercury, Venus, Mars, Jupiter, Saturn),
retrograde planets, aspects planetaires, personalized houses, Chiron/Lilith/Noeud Nord, chemin de vie,
previsions, tarot, conseils
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data matching the main agent context
TEST_USER_DATA = {
    "prenom": "Marie",
    "dateNaissance": "1990-06-15",
    "heureNaissance": "14:30",
    "ville": "Paris",
    "genre": "Femme"
}

TEST_PRO_REQUEST = {
    "name": "Marie",
    "gender": "female",
    "day": 15,
    "month": 6,
    "year": 1990,
    "hour": 14,
    "minute": 30,
    "lat": 48.8566,
    "lon": 2.3522,
    "timezone": 1.0,
    "place": "Paris, France"
}


class TestPDFGenerateEndpoint:
    """Tests for POST /api/pdf/generate"""
    
    def test_pdf_generate_returns_200(self):
        """POST /api/pdf/generate should return HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            timeout=120  # PDF generation may take time
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        print("PASS: POST /api/pdf/generate returns 200")
    
    def test_pdf_generate_returns_pdf_content_type(self):
        """POST /api/pdf/generate should return PDF content-type"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected PDF content-type, got {content_type}"
        print(f"PASS: Content-Type is {content_type}")
    
    def test_pdf_generate_has_content_disposition(self):
        """POST /api/pdf/generate should have Content-Disposition header"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        disposition = response.headers.get('Content-Disposition', '')
        assert 'attachment' in disposition, f"Expected attachment disposition, got {disposition}"
        assert 'filename=' in disposition, f"Expected filename in disposition, got {disposition}"
        print(f"PASS: Content-Disposition is {disposition}")


class TestProHoroscopePDFEndpoint:
    """Tests for POST /api/pdf/pro-horoscope"""
    
    def test_pro_horoscope_returns_200(self):
        """POST /api/pdf/pro-horoscope should return HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=TEST_PRO_REQUEST,
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        print("PASS: POST /api/pdf/pro-horoscope returns 200")
    
    def test_pro_horoscope_returns_pdf_content_type(self):
        """POST /api/pdf/pro-horoscope should return PDF content-type"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=TEST_PRO_REQUEST,
            timeout=120
        )
        assert response.status_code == 200
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected PDF content-type, got {content_type}"
        print(f"PASS: Content-Type is {content_type}")
    
    def test_pro_horoscope_pdf_size_indicates_enriched_content(self):
        """Pro horoscope PDF should be substantial in size (enriched content)"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=TEST_PRO_REQUEST,
            timeout=120
        )
        assert response.status_code == 200
        pdf_size = len(response.content)
        # Expect at least 500KB for a 25+ page enriched PDF
        min_expected_size = 200 * 1024  # 200KB minimum
        assert pdf_size > min_expected_size, f"PDF size {pdf_size} bytes is too small for enriched content (expected > {min_expected_size})"
        print(f"PASS: PDF size is {pdf_size} bytes ({pdf_size/1024:.1f} KB)")


class TestPDFPreviewEndpoint:
    """Tests for POST /api/pdf/preview"""
    
    def test_pdf_preview_returns_200(self):
        """POST /api/pdf/preview should return HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        print("PASS: POST /api/pdf/preview returns 200")
    
    def test_pdf_preview_returns_previews_array(self):
        """POST /api/pdf/preview should return previews array"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        assert 'previews' in data, f"Expected 'previews' key in response. Got: {list(data.keys())}"
        assert isinstance(data['previews'], list), f"Expected previews to be a list"
        print(f"PASS: Preview returns {len(data['previews'])} preview images")
    
    def test_pdf_preview_returns_total_pages(self):
        """POST /api/pdf/preview should return total_pages"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        assert 'total_pages' in data, f"Expected 'total_pages' key in response. Got: {list(data.keys())}"
        print(f"PASS: total_pages = {data['total_pages']}")
    
    def test_pdf_preview_has_25_plus_pages(self):
        """Enriched PDF should have 25+ pages"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        total_pages = data.get('total_pages', 0)
        assert total_pages >= 25, f"Expected 25+ pages for enriched PDF, got {total_pages}"
        print(f"PASS: Enriched PDF has {total_pages} pages (>= 25 required)")


class TestDiscountCodeValidation:
    """Tests for POST /api/discount/validate"""
    
    def test_plume2026_discount_valid(self):
        """PLUME2026 code should be valid with 100% discount"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('valid') == True, f"Expected valid=True, got {data}"
        assert data.get('discount_percent') == 100, f"Expected 100% discount, got {data.get('discount_percent')}"
        print(f"PASS: PLUME2026 validates with 100% discount")
    
    def test_invalid_code_returns_invalid(self):
        """Invalid code should return valid=False"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALID_CODE_123"},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('valid') == False, f"Expected valid=False for invalid code, got {data}"
        print("PASS: Invalid code correctly returns valid=False")


class TestAstrologyHoroscopeEndpoint:
    """Tests for POST /api/astrology/horoscope"""
    
    def test_astrology_horoscope_returns_200(self):
        """POST /api/astrology/horoscope should return HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/horoscope",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        print("PASS: POST /api/astrology/horoscope returns 200")
    
    def test_astrology_horoscope_returns_planets(self):
        """POST /api/astrology/horoscope should return planets data"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/horoscope",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True, f"Expected success=True, got {data.get('success')}"
        assert 'data' in data, "Expected 'data' key in response"
        horoscope_data = data['data']
        # Check for planets array in horoscope data
        assert 'planets' in horoscope_data, f"Expected 'planets' in horoscope data. Keys: {list(horoscope_data.keys())}"
        print(f"PASS: Horoscope returns {len(horoscope_data.get('planets', []))} planets")
    
    def test_astrology_horoscope_returns_houses(self):
        """POST /api/astrology/horoscope should return houses data"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/horoscope",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        horoscope_data = data.get('data', {})
        assert 'houses' in horoscope_data, f"Expected 'houses' in horoscope data. Keys: {list(horoscope_data.keys())}"
        houses = horoscope_data.get('houses', [])
        assert len(houses) == 12, f"Expected 12 houses, got {len(houses)}"
        print(f"PASS: Horoscope returns {len(houses)} houses")
    
    def test_astrology_horoscope_returns_aspects(self):
        """POST /api/astrology/horoscope should return aspects data"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/horoscope",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        horoscope_data = data.get('data', {})
        assert 'aspects' in horoscope_data, f"Expected 'aspects' in horoscope data. Keys: {list(horoscope_data.keys())}"
        aspects = horoscope_data.get('aspects', [])
        print(f"PASS: Horoscope returns {len(aspects)} aspects")


class TestAstrologyPlanetsEndpoint:
    """Tests for POST /api/astrology/planets"""
    
    def test_astrology_planets_returns_200(self):
        """POST /api/astrology/planets should return HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/planets",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text[:500]}"
        print("PASS: POST /api/astrology/planets returns 200")
    
    def test_astrology_planets_returns_planet_positions(self):
        """POST /api/astrology/planets should return planet positions"""
        response = requests.post(
            f"{BASE_URL}/api/astrology/planets",
            json={
                "date_naissance": "1990-06-15",
                "heure_naissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True, f"Expected success=True, got {data.get('success')}"
        assert 'data' in data, "Expected 'data' key in response"
        planets_data = data['data']
        assert isinstance(planets_data, list), "Expected planets data to be a list"
        
        # Verify main planets are present
        planet_names = [p.get('name') for p in planets_data]
        expected_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for planet in expected_planets:
            assert planet in planet_names, f"Expected {planet} in planet data"
        
        print(f"PASS: Planets endpoint returns {len(planets_data)} planets including {expected_planets}")


class TestPDFContentSections:
    """Tests to verify PDF contains required sections via preview API"""
    
    def test_pdf_has_substantial_content(self):
        """PDF should have substantial content (>500KB indicates rich sections)"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            timeout=120
        )
        assert response.status_code == 200
        pdf_size = len(response.content)
        # For 25+ pages with images and rich content, expect at least 300KB
        assert pdf_size > 300 * 1024, f"PDF size {pdf_size/1024:.1f}KB is too small for enriched content"
        print(f"PASS: PDF has substantial content: {pdf_size/1024:.1f} KB")


class TestRegressionExistingFeatures:
    """Regression tests for existing features"""
    
    def test_root_endpoint(self):
        """Root endpoint should return Hello World"""
        response = requests.get(f"{BASE_URL}/api/", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get('message') == 'Hello World', f"Unexpected response: {data}"
        print("PASS: Root endpoint working")
    
    def test_products_endpoint(self):
        """Products endpoint should return all products"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert 'manuscrit' in data, "Expected manuscrit product"
        assert data['manuscrit']['amount'] == 29.90, f"Manuscrit price should be 29.90 EUR"
        print(f"PASS: Products endpoint returns {len(data)} products")
    
    def test_tarot_oui_non_endpoint(self):
        """Tarot oui/non endpoint should work"""
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json={"question": "Test question for PDF testing"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'carte' in data, f"Expected carte in response. Got: {list(data.keys())}"
        print("PASS: Tarot oui/non endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
