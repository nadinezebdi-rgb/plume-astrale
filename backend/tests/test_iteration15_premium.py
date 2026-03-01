"""
Iteration 15 - Premium Experience API Tests
Tests the Premium 199€ experience endpoints:
- /api/products (premium product)
- /api/premium/generate (5-step content generation)
- /api/premium/pdf (PDF generation)
- /api/discount/validate (PLUME2026 promo code)
- /api/access/free (free access with promo code)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ API root responds: {response.json()}")


class TestPremiumProducts:
    """Test premium product listing"""
    
    def test_products_endpoint(self):
        """GET /api/products returns products including premium"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "premium" in data, "Premium product should exist in products"
        print(f"✓ Products endpoint returns data with {len(data)} products")
    
    def test_premium_product_details(self):
        """Premium product should have correct amount (199€)"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        
        premium = data.get("premium")
        assert premium is not None, "Premium product must exist"
        assert premium.get("amount") == 199.00, f"Premium should cost 199€, got {premium.get('amount')}"
        assert premium.get("currency") == "eur", "Premium currency should be EUR"
        assert "Experience Premium" in premium.get("name", ""), "Premium name should contain 'Experience Premium'"
        print(f"✓ Premium product: {premium['name']} @ {premium['amount']}€")


class TestDiscountCode:
    """Test discount code validation"""
    
    def test_plume2026_valid(self):
        """POST /api/discount/validate with PLUME2026 returns valid=true, 100% discount"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("valid") == True, "PLUME2026 should be valid"
        assert data.get("discount_percent") == 100, "PLUME2026 should give 100% discount"
        print(f"✓ PLUME2026 valid: {data['discount_percent']}% discount - {data.get('message')}")
    
    def test_plume2026_lowercase(self):
        """Discount code should work regardless of case"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "plume2026"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True, "Lowercase code should work"
        print(f"✓ PLUME2026 lowercase valid")
    
    def test_invalid_code(self):
        """Invalid discount code returns valid=false"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "INVALID123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == False, "Invalid code should return valid=false"
        print(f"✓ Invalid code rejected: {data.get('message')}")


class TestFreeAccess:
    """Test free access with promo code"""
    
    def test_free_access_with_plume2026(self):
        """POST /api/access/free with PLUME2026 grants free access"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "premium",
                "discount_code": "PLUME2026",
                "user_email": "test@example.com",
                "origin_url": "https://example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True, "Free access should succeed"
        assert "redirect_url" in data, "Should return redirect URL"
        print(f"✓ Free access granted: {data.get('message')}")
    
    def test_free_access_without_code(self):
        """POST /api/access/free without code returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "premium",
                "user_email": "test@example.com",
                "origin_url": "https://example.com"
            }
        )
        assert response.status_code == 400, "Should require discount code"
        print(f"✓ Free access correctly requires discount code")
    
    def test_free_access_invalid_product(self):
        """POST /api/access/free with invalid product returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/access/free",
            json={
                "product_id": "nonexistent",
                "discount_code": "PLUME2026",
                "user_email": "test@example.com",
                "origin_url": "https://example.com"
            }
        )
        assert response.status_code == 400, "Should reject invalid product"
        print(f"✓ Invalid product rejected")


class TestPremiumGenerate:
    """Test premium content generation (LLM-powered - may be slow)"""
    
    def test_premium_generate_request(self):
        """POST /api/premium/generate with user data returns 5 steps
        NOTE: This test may take 30-90 seconds due to LLM calls"""
        
        payload = {
            "prenom": "Marie",
            "dateNaissance": "1990-05-15",
            "heureNaissance": "14:30",
            "ville": "Paris"
        }
        
        print("⏳ Testing premium generate (may take 30-90s)...")
        start = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/premium/generate",
            json=payload,
            timeout=150  # Extended timeout for LLM calls
        )
        
        elapsed = time.time() - start
        print(f"⏱ Response received in {elapsed:.1f}s")
        
        assert response.status_code == 200, f"Premium generate failed: {response.text[:200]}"
        data = response.json()
        
        assert data.get("success") == True, "Should return success=true"
        assert "data" in data, "Should return data object"
        
        premium_data = data["data"]
        
        # Verify user data
        assert premium_data.get("prenom") == "Marie", "Should return prenom"
        assert "signe" in premium_data, "Should return signe"
        
        # Verify all 5 steps exist
        steps = premium_data.get("steps", {})
        expected_steps = [
            "step_1_fondement",
            "step_2_chemin_ame",
            "step_3_cycle",
            "step_4_schemas",
            "step_5_projection"
        ]
        
        for step_key in expected_steps:
            assert step_key in steps, f"Missing step: {step_key}"
            step = steps[step_key]
            assert "title" in step, f"{step_key} should have title"
            assert "interpretation" in step, f"{step_key} should have interpretation"
            print(f"  ✓ {step_key}: '{step.get('title')}'")
        
        print(f"✓ Premium generate returned 5 steps for {premium_data.get('signe')}")


class TestPremiumPDF:
    """Test premium PDF generation"""
    
    def test_premium_pdf_generation(self):
        """POST /api/premium/pdf generates a valid PDF from premium data"""
        
        # Sample premium data structure (mimicking what generate returns)
        premium_data = {
            "prenom": "TestUser",
            "signe": "Taureau",
            "date_naissance": "1990-05-15",
            "generated_at": "2026-01-15T12:00:00",
            "steps": {
                "step_1_fondement": {
                    "title": "Votre Fondement",
                    "subtitle": "Les forces et tensions qui vous definissent",
                    "signe": "Taureau",
                    "element": "Terre",
                    "modalite": "Fixe",
                    "forces": ["Stabilite", "Perseverance", "Sensualite"],
                    "tensions": ["Resistance au changement", "Possessivite", "Entêtement"],
                    "interpretation": "Test interpretation for fondement step.",
                    "reflection": "Cela resonne-t-il avec votre vecu actuel ?"
                },
                "step_2_chemin_ame": {
                    "title": "Votre Chemin d'Ame",
                    "subtitle": "Le nombre qui guide votre trajectoire",
                    "chemin_de_vie": 7,
                    "titre_chemin": "Le Sage",
                    "nombre_expression": 3,
                    "nombre_ame": 5,
                    "interpretation": "Test interpretation for chemin d'ame.",
                    "reflection": "Comment ce nombre se manifeste-t-il dans vos choix ?"
                },
                "step_3_cycle": {
                    "title": "Votre Cycle Actuel",
                    "subtitle": "Les mouvements de cette periode",
                    "annee_personnelle": 9,
                    "periode": "Mars 2026",
                    "interpretation": "Test interpretation for cycle.",
                    "reflection": "Quel element resonne le plus avec votre situation ?"
                },
                "step_4_schemas": {
                    "title": "Vos Schemas Repetitifs",
                    "subtitle": "Ce qui revient et ce que cela revele",
                    "interpretation": "Test interpretation for schemas.",
                    "reflection": "Reconnaissez-vous ces mecanismes dans votre parcours ?"
                },
                "step_5_projection": {
                    "title": "Projection 12 Mois",
                    "subtitle": "Mars 2026 - Fevrier 2027",
                    "interpretation": "Test interpretation for projection.",
                    "reflection": "Quels reperes souhaitez-vous garder en memoire ?"
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premium/pdf",
            json={"data": premium_data},
            timeout=60
        )
        
        assert response.status_code == 200, f"PDF generation failed: {response.text[:200]}"
        
        # Verify it's a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Should return PDF, got {content_type}"
        
        # Check PDF magic bytes
        pdf_bytes = response.content
        assert len(pdf_bytes) > 1000, "PDF should have content"
        assert pdf_bytes[:4] == b'%PDF', "Should be valid PDF format"
        
        # Check content-disposition header
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition, "Should be downloadable attachment"
        assert "TestUser" in disposition or "premium" in disposition, "Filename should contain user name or premium"
        
        print(f"✓ Premium PDF generated: {len(pdf_bytes)} bytes")
    
    def test_premium_pdf_missing_data(self):
        """POST /api/premium/pdf without data returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/premium/pdf",
            json={}
        )
        assert response.status_code == 400, "Should require premium data"
        print(f"✓ PDF endpoint correctly requires data")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
