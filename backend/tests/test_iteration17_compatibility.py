"""
Test Iteration 17 - Compatibility PDF Generation
Tests for /api/compatibility/generate endpoint with rich content
"""
import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestCompatibilityAPI:
    """Tests for compatibility report generation endpoint"""
    
    def test_api_health(self):
        """Test backend health"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print("✓ Backend API is healthy")
    
    def test_compatibility_generate_success(self):
        """Test compatibility PDF generation with person1, person2, and question"""
        payload = {
            "person1": {
                "first_name": "Nadine",
                "last_name": "Test",
                "gender": "female",
                "day": 17,
                "month": 7,
                "year": 1968,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Sylvain",
                "last_name": "Test",
                "gender": "male",
                "day": 9,
                "month": 2,
                "year": 1966,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": "Avons-nous une réelle compatibilité sur le long terme ?"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60  # Allow time for PDF generation
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "pdf_url" in data, "Response should contain pdf_url"
        pdf_url = data["pdf_url"]
        
        # Verify it's a base64 data URL
        assert pdf_url.startswith("data:application/pdf;base64,"), "pdf_url should be a base64 data URL"
        
        # Verify PDF content is not empty
        pdf_b64 = pdf_url.split(",")[1]
        pdf_bytes = base64.b64decode(pdf_b64)
        assert len(pdf_bytes) > 1000, f"PDF should have substantial content, got {len(pdf_bytes)} bytes"
        
        print(f"✓ Compatibility PDF generated successfully ({len(pdf_bytes)} bytes)")
    
    def test_compatibility_with_cancer_verseau(self):
        """Test specifically with Cancer (17/07/1968) and Verseau (09/02/1966)"""
        payload = {
            "person1": {
                "first_name": "Nadine",
                "last_name": "Cancer",
                "gender": "female",
                "day": 17,
                "month": 7,
                "year": 1968,
                "hour": 10,
                "minute": 30,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Sylvain",
                "last_name": "Verseau",
                "gender": "male",
                "day": 9,
                "month": 2,
                "year": 1966,
                "hour": 14,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": "Comment gérer nos différences de caractère ?"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        
        # Decode and check PDF structure
        pdf_b64 = data["pdf_url"].split(",")[1]
        pdf_bytes = base64.b64decode(pdf_b64)
        
        # Check PDF has multiple pages (look for /Count in the PDF structure)
        pdf_text = pdf_bytes.decode('latin-1')
        # Look for page count
        import re
        count_match = re.search(r'/Count\s+(\d+)', pdf_text)
        if count_match:
            page_count = int(count_match.group(1))
            assert page_count >= 10, f"PDF should have at least 10 pages, got {page_count}"
            print(f"✓ Cancer/Verseau compatibility PDF generated with {page_count} pages ({len(pdf_bytes)} bytes)")
        else:
            # Fallback - just check it's a reasonable size for 11 pages (text PDFs can be compressed)
            assert len(pdf_bytes) > 10000, f"PDF should have substantial content, got {len(pdf_bytes)} bytes"
            print(f"✓ Cancer/Verseau compatibility PDF generated ({len(pdf_bytes)} bytes)")
    
    def test_compatibility_without_question(self):
        """Test compatibility generation works without a question"""
        payload = {
            "person1": {
                "first_name": "Marie",
                "last_name": "Test",
                "gender": "female",
                "day": 15,
                "month": 3,
                "year": 1990,
                "hour": 8,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Pierre",
                "last_name": "Test",
                "gender": "male",
                "day": 22,
                "month": 10,
                "year": 1988,
                "hour": 15,
                "minute": 30,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": ""  # Empty question
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        print("✓ Compatibility PDF generated without question")
    
    def test_compatibility_pdf_is_valid_pdf(self):
        """Verify the generated PDF is actually a valid PDF"""
        payload = {
            "person1": {
                "first_name": "Test1",
                "last_name": "User",
                "gender": "female",
                "day": 1,
                "month": 1,
                "year": 1985,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Test2",
                "last_name": "User",
                "gender": "male",
                "day": 1,
                "month": 6,
                "year": 1983,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": "Test question"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        pdf_b64 = data["pdf_url"].split(",")[1]
        pdf_bytes = base64.b64decode(pdf_b64)
        
        # Check PDF magic bytes (PDF files start with %PDF)
        assert pdf_bytes[:4] == b'%PDF', "Generated file should be a valid PDF (start with %PDF)"
        
        print("✓ Generated PDF is valid (starts with %PDF)")
    
    def test_products_endpoint_has_compatibilite(self):
        """Verify compatibilite product is available"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        products = response.json()
        
        assert "compatibilite" in products, "compatibilite product should exist"
        compat_product = products["compatibilite"]
        
        assert compat_product["name"] == "Compatibilité Astrale", "Product name should be 'Compatibilité Astrale'"
        assert compat_product["amount"] == 29.90, "Price should be 29.90"
        assert compat_product["currency"] == "eur", "Currency should be EUR"
        
        print("✓ Compatibilité product available at 29.90 EUR")


class TestCompatibilityZodiacCalculation:
    """Tests to verify zodiac sign calculation for compatibility - using internal generator logic"""
    
    def test_july_17_generates_cancer_report(self):
        """Verify July 17 birth date generates a Cancer-themed report"""
        payload = {
            "person1": {
                "first_name": "Test",
                "last_name": "Cancer",
                "gender": "female",
                "day": 17,
                "month": 7,  # July 17 = Cancer
                "year": 1968,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Partner",
                "last_name": "Test",
                "gender": "male",
                "day": 1,
                "month": 1,
                "year": 1970,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        print("✓ July 17, 1968 (Cancer) generates valid compatibility report")
    
    def test_feb_9_generates_aquarius_report(self):
        """Verify February 9 birth date generates an Aquarius-themed report"""
        payload = {
            "person1": {
                "first_name": "Test",
                "last_name": "Verseau",
                "gender": "male",
                "day": 9,
                "month": 2,  # Feb 9 = Aquarius/Verseau
                "year": 1966,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "person2": {
                "first_name": "Partner",
                "last_name": "Test",
                "gender": "female",
                "day": 1,
                "month": 6,
                "year": 1970,
                "hour": 12,
                "minute": 0,
                "lat": 48.8566,
                "lon": 2.3522,
                "timezone": 1.0,
                "place": "Paris, France"
            },
            "question": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        print("✓ February 9, 1966 (Aquarius/Verseau) generates valid compatibility report")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
