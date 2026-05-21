"""
Iteration 5 Backend Tests - Pro Horoscope PDF, Match Making/Compatibility, Tarot Images
Tests for:
1. POST /api/pdf/pro-horoscope - Pro horoscope 68-page PDF
2. POST /api/compatibility/generate - Match making PDF
3. POST /api/checkout/create for compatibilite product
4. GET /api/assets/tarot/{filename}.jpg - Tarot card images
5. POST /api/tarot/oui-non - Card data with image URL
"""

import pytest
import requests
import os
import time

# Use the public URL from frontend .env
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com')


class TestProHoroscopePDF:
    """Tests for Pro Horoscope PDF generation (68 pages)"""
    
    def test_pro_horoscope_pdf_generation(self):
        """Test POST /api/pdf/pro-horoscope returns a valid PDF URL"""
        # Test data as specified in the request
        payload = {
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
        
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=payload,
            timeout=120  # Pro API can take 10-30 seconds
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "pdf_url" in data, f"Response missing pdf_url: {data}"
        assert data["pdf_url"], "pdf_url should not be empty"
        assert data["pdf_url"].startswith("http"), f"pdf_url should be a valid URL: {data['pdf_url']}"
        
        print(f"SUCCESS: Pro horoscope PDF URL: {data['pdf_url'][:80]}...")
    
    def test_pro_horoscope_with_male_gender(self):
        """Test Pro horoscope works with male gender"""
        payload = {
            "name": "Pierre",
            "gender": "male",
            "day": 20,
            "month": 3,
            "year": 1985,
            "hour": 10,
            "minute": 0,
            "lat": 48.8566,
            "lon": 2.3522,
            "timezone": 1.0,
            "place": "Paris, France"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "pdf_url" in data
        assert data["pdf_url"]
        print(f"SUCCESS: Male pro horoscope PDF generated")


class TestCompatibilityMatchMaking:
    """Tests for Match Making / Compatibility PDF generation"""
    
    def test_compatibility_generate_pdf(self):
        """Test POST /api/compatibility/generate returns a valid match making PDF URL"""
        payload = {
            "person1": {
                "first_name": "Marie",
                "last_name": "Dupont",
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
            "person2": {
                "first_name": "Pierre",
                "last_name": "Martin",
                "gender": "male",
                "day": 20,
                "month": 3,
                "year": 1988,
                "hour": 8,
                "minute": 45,
                "lat": 45.7640,
                "lon": 4.8357,
                "timezone": 1.0,
                "place": "Lyon, France"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=120  # Match making API can take 10-30 seconds
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "pdf_url" in data, f"Response missing pdf_url: {data}"
        assert data["pdf_url"], "pdf_url should not be empty"
        assert data["pdf_url"].startswith("http"), f"pdf_url should be a valid URL: {data['pdf_url']}"
        
        print(f"SUCCESS: Compatibility PDF URL: {data['pdf_url'][:80]}...")
    
    def test_compatibility_gender_swap(self):
        """Test that male/female are correctly assigned regardless of person order"""
        # Person1 is male, Person2 is female (reversed order)
        payload = {
            "person1": {
                "first_name": "Pierre",
                "gender": "male",  # Male first
                "day": 20,
                "month": 3,
                "year": 1988,
                "hour": 8,
                "minute": 45
            },
            "person2": {
                "first_name": "Marie",
                "gender": "female",  # Female second
                "day": 15,
                "month": 6,
                "year": 1990,
                "hour": 14,
                "minute": 30
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/generate",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "pdf_url" in data
        print(f"SUCCESS: Compatibility with swapped gender order works")


class TestCompatibiliteCheckout:
    """Tests for Compatibilite product checkout (29.90 EUR)"""
    
    def test_checkout_create_compatibilite(self):
        """Test POST /api/checkout/create works for product_id 'compatibilite'"""
        payload = {
            "product_id": "compatibilite",
            "origin_url": "https://consultation-astro.preview.emergentagent.com",
            "user_email": "test@example.com",
            "user_data": {
                "person1": {"first_name": "Marie"},
                "person2": {"first_name": "Pierre"}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/checkout/create",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data, f"Response missing checkout URL: {data}"
        assert "session_id" in data, f"Response missing session_id: {data}"
        assert data["url"].startswith("https://checkout.stripe.com"), f"Invalid Stripe URL: {data['url']}"
        
        print(f"SUCCESS: Compatibilite checkout session created: {data['session_id']}")
    
    def test_compatibilite_product_in_catalog(self):
        """Test that compatibilite product exists with correct price (29.90 EUR)"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=10)
        
        assert response.status_code == 200
        products = response.json()
        
        assert "compatibilite" in products, f"compatibilite product not found in catalog: {products.keys()}"
        
        compat_product = products["compatibilite"]
        assert compat_product["amount"] == 29.90, f"Expected 29.90, got {compat_product['amount']}"
        assert compat_product["currency"] == "eur"
        
        print(f"SUCCESS: Compatibilite product: {compat_product['name']} - {compat_product['amount']} EUR")


class TestTarotCardImages:
    """Tests for Tarot card static images at /api/assets/tarot/"""
    
    # All 22 tarot card filenames from TAROT_IMAGE_MAP
    TAROT_CARDS = [
        "00_mat.jpg", "01_bateleur.jpg", "02_papesse.jpg",
        "03_imperatrice.jpg", "04_empereur.jpg", "05_pape.jpg",
        "06_amoureux.jpg", "07_chariot.jpg", "08_justice.jpg",
        "09_hermite.jpg", "10_roue_fortune.jpg", "11_force.jpg",
        "12_pendu.jpg", "13_arcane_sans_nom.jpg", "14_temperance.jpg",
        "15_diable.jpg", "16_maison_dieu.jpg", "17_etoile.jpg",
        "18_lune.jpg", "19_soleil.jpg", "20_jugement.jpg",
        "21_monde.jpg"
    ]
    
    def test_tarot_image_first_card(self):
        """Test that first tarot image (Le Mat) is served correctly"""
        response = requests.get(
            f"{BASE_URL}/api/assets/tarot/00_mat.jpg",
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get('Content-Type', '').startswith('image/'), f"Expected image content type"
        assert len(response.content) > 1000, "Image file seems too small"
        
        print(f"SUCCESS: Tarot image 00_mat.jpg served ({len(response.content)} bytes)")
    
    def test_tarot_image_all_22_cards(self):
        """Test that all 22 tarot card images are accessible"""
        failed = []
        success = 0
        
        for card in self.TAROT_CARDS:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/assets/tarot/{card}",
                    timeout=10
                )
                if response.status_code == 200 and len(response.content) > 500:
                    success += 1
                else:
                    failed.append(f"{card}: status={response.status_code}")
            except Exception as e:
                failed.append(f"{card}: {str(e)}")
        
        assert len(failed) == 0, f"Failed cards: {failed}"
        print(f"SUCCESS: All {success}/22 tarot card images accessible")
    
    def test_tarot_oui_non_includes_image_url(self):
        """Test POST /api/tarot/oui-non returns card data with image URL"""
        payload = {"question": "Vais-je trouver l'amour cette annee?"}
        
        response = requests.post(
            f"{BASE_URL}/api/tarot/oui-non",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "carte" in data, f"Response missing carte: {data}"
        assert "image" in data["carte"], f"Carte missing image field: {data['carte']}"
        
        image_url = data["carte"]["image"]
        assert image_url.startswith("/api/assets/tarot/"), f"Invalid image URL format: {image_url}"
        assert image_url.endswith(".jpg"), f"Image URL should end with .jpg: {image_url}"
        
        print(f"SUCCESS: Tarot oui-non returns image URL: {image_url}")


class TestTarologieImages:
    """Tests for Tarologie tirage with card images"""
    
    def test_tarologie_tirage_returns_images(self):
        """Test POST /api/tarologie/tirage returns 7 cards with image URLs"""
        payload = {
            "prenom": "Marie",
            "date_naissance": "1990-06-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tarologie/tirage",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "tirage" in data, f"Response missing tirage: {data}"
        assert len(data["tirage"]) == 7, f"Expected 7 cards, got {len(data['tirage'])}"
        
        # Check each card has image URL
        for i, item in enumerate(data["tirage"]):
            assert "carte" in item, f"Card {i} missing carte field"
            assert "image" in item["carte"], f"Card {i} missing image field"
            assert item["carte"]["image"].startswith("/api/assets/tarot/"), f"Card {i} invalid image URL"
        
        print(f"SUCCESS: Tarologie tirage returns 7 cards with image URLs")


class TestExistingFlowRegression:
    """Regression tests to ensure existing flows still work"""
    
    def test_discount_code_astro100(self):
        """Test ASTRO100 promo code still works"""
        payload = {"code": "ASTRO100"}
        
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 100
        
        print(f"SUCCESS: ASTRO100 code validates correctly")
    
    def test_free_access_with_astro100(self):
        """Test free access endpoint with ASTRO100"""
        payload = {
            "product_id": "manuscrit",
            "origin_url": "https://consultation-astro.preview.emergentagent.com",
            "discount_code": "ASTRO100",
            "user_email": "test@example.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        print(f"SUCCESS: Free access with ASTRO100 works")
    
    def test_pdf_generate_still_works(self):
        """Test original PDF generate endpoint still works"""
        payload = {
            "user_data": {
                "prenom": "Marie",
                "genre": "female",
                "email": "test@example.com",
                "dateNaissance": "1990-06-15",
                "heureNaissance": "14:30",
                "ville": "Paris",
                "pays": "France"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'application/pdf'
        assert len(response.content) > 10000, "PDF seems too small"
        
        print(f"SUCCESS: Original PDF generate works ({len(response.content)} bytes)")
    
    def test_products_endpoint(self):
        """Test products endpoint returns all products including new compatibilite"""
        response = requests.get(f"{BASE_URL}/api/products", timeout=10)
        
        assert response.status_code == 200
        products = response.json()
        
        expected = ["manuscrit", "livre", "tarot_oui_non", "tarologie_mediumnite", "compatibilite"]
        for product_id in expected:
            assert product_id in products, f"Missing product: {product_id}"
        
        # Verify prices
        assert products["manuscrit"]["amount"] == 29.90
        assert products["livre"]["amount"] == 49.90
        assert products["tarot_oui_non"]["amount"] == 4.99
        assert products["tarologie_mediumnite"]["amount"] == 35.00
        assert products["compatibilite"]["amount"] == 29.90
        
        print(f"SUCCESS: All products present with correct prices")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
