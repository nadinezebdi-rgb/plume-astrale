"""
Iteration 8 - Share Card Feature Tests
Tests for the new shareable astrological profile card (POST /api/share/generate-card)
- PNG image generation 1080x1350
- Content-type verification
- Image size validation
- Regression tests for PDF endpoints
"""
import pytest
import requests
import os
from io import BytesIO

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user data
TEST_USER_DATA = {
    "prenom": "Marie",
    "dateNaissance": "1990-06-15",
    "heureNaissance": "14:30",
    "ville": "Paris",
    "pays": "France",
    "genre": "female"
}


class TestShareCardGeneration:
    """Tests for the share card PNG generation endpoint"""
    
    def test_share_card_returns_200(self):
        """POST /api/share/generate-card returns HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ POST /api/share/generate-card returns HTTP 200")
    
    def test_share_card_returns_png_content_type(self):
        """POST /api/share/generate-card returns image/png content-type"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200
        content_type = response.headers.get('Content-Type', '')
        assert 'image/png' in content_type, f"Expected image/png, got {content_type}"
        print(f"✓ Content-Type is {content_type}")
    
    def test_share_card_has_content_disposition(self):
        """POST /api/share/generate-card has Content-Disposition attachment header"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp, f"Expected attachment in Content-Disposition, got {content_disp}"
        assert 'profil_astral' in content_disp, f"Expected profil_astral filename, got {content_disp}"
        print(f"✓ Content-Disposition: {content_disp}")
    
    def test_share_card_size_greater_than_10kb(self):
        """Share card image size is > 10KB"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200
        size_kb = len(response.content) / 1024
        assert size_kb > 10, f"Expected > 10KB, got {size_kb:.2f}KB"
        print(f"✓ Image size is {size_kb:.2f}KB (> 10KB)")
    
    def test_share_card_is_valid_png(self):
        """Share card is a valid PNG image"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200
        # PNG files start with these bytes
        png_header = b'\x89PNG\r\n\x1a\n'
        assert response.content[:8] == png_header, "Response is not a valid PNG file"
        print(f"✓ Response is a valid PNG file")
    
    def test_share_card_dimensions_1080x1350(self):
        """Share card image is 1080x1350 pixels"""
        from PIL import Image
        
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": TEST_USER_DATA},
            timeout=60
        )
        assert response.status_code == 200
        
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        assert width == 1080, f"Expected width 1080, got {width}"
        assert height == 1350, f"Expected height 1350, got {height}"
        print(f"✓ Image dimensions are {width}x{height} (1080x1350)")
    
    def test_share_card_with_minimal_data(self):
        """Share card works with minimal user data (just dateNaissance)"""
        minimal_data = {
            "dateNaissance": "1990-06-15"
        }
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json={"user_data": minimal_data},
            timeout=60
        )
        assert response.status_code == 200
        assert 'image/png' in response.headers.get('Content-Type', '')
        print(f"✓ Share card works with minimal data")


class TestRegressionPDFEndpoints:
    """Regression tests for existing PDF endpoints"""
    
    def test_pdf_pro_horoscope_still_works(self):
        """Regression: POST /api/pdf/pro-horoscope returns HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json={
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
            },
            timeout=90
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected PDF, got {content_type}"
        print(f"✓ Regression: POST /api/pdf/pro-horoscope returns HTTP 200 with PDF")
    
    def test_pdf_preview_still_works(self):
        """Regression: POST /api/pdf/preview returns HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/preview",
            json={"user_data": TEST_USER_DATA},
            timeout=90
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'previews' in data, "Expected previews in response"
        assert 'total_pages' in data, "Expected total_pages in response"
        print(f"✓ Regression: POST /api/pdf/preview returns HTTP 200 with {data.get('total_pages', 'N/A')} pages")
    
    def test_pdf_generate_still_works(self):
        """Regression: POST /api/pdf/generate returns HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json={"user_data": TEST_USER_DATA},
            timeout=90
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected PDF, got {content_type}"
        print(f"✓ Regression: POST /api/pdf/generate returns HTTP 200 with PDF")


class TestRegressionOtherEndpoints:
    """Regression tests for other endpoints"""
    
    def test_api_root_endpoint(self):
        """Regression: GET /api/ returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        assert response.status_code == 200
        print(f"✓ Regression: GET /api/ returns HTTP 200")
    
    def test_products_endpoint(self):
        """Regression: GET /api/products returns all products"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert 'manuscrit' in products
        assert products['manuscrit']['amount'] == 29.90
        print(f"✓ Regression: GET /api/products returns correct products")
    
    def test_discount_validate(self):
        """Regression: POST /api/discount/validate works"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] == True
        assert data['discount_percent'] == 100
        print(f"✓ Regression: POST /api/discount/validate works for PLUME2026")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
