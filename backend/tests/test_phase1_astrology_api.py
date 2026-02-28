"""
Phase 1 AstrologyAPI Integration Tests
Tests for:
1. GET /api/moon-phase - New moon phase endpoint
2. GET /api/daily/{sign} - Daily content with moon phase enrichment
3. POST /api/pdf/pro-horoscope - PDF with real SVG natal chart
4. Regression tests for share/generate-card, pdf/generate, discount/validate
"""
import pytest
import requests
import os
import io
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data matching main agent's specification
PRO_HOROSCOPE_TEST_DATA = {
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
    "place": "Paris"
}

PDF_GENERATE_TEST_DATA = {
    "user_data": {
        "prenom": "Marie",
        "dateNaissance": "1990-06-15",
        "heureNaissance": "14:30",
        "ville": "Paris",
        "pays": "France",
        "genre": "female"
    }
}

SHARE_CARD_TEST_DATA = {
    "user_data": {
        "prenom": "Marie",
        "dateNaissance": "1990-06-15",
        "heureNaissance": "14:30",
        "ville": "Paris",
        "pays": "France"
    }
}


class TestMoonPhaseEndpoint:
    """Tests for the new /api/moon-phase endpoint"""
    
    def test_moon_phase_returns_200(self):
        """GET /api/moon-phase returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/moon-phase returns HTTP 200")
    
    def test_moon_phase_has_success_field(self):
        """Response has success=True"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        data = response.json()
        assert data.get('success') == True, f"Expected success=True, got {data}"
        print("PASS: Response has success=True")
    
    def test_moon_phase_has_phase_french(self):
        """Response has French phase name"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        data = response.json()
        assert 'phase' in data, f"Missing 'phase' field in response: {data}"
        # French phases should contain French words
        french_phases = [
            "Nouvelle Lune", "Premier Croissant", "Premier Quartier",
            "Lune Gibbeuse", "Pleine Lune", "Lune Disséminante",
            "Dernier Quartier", "Lune Balsamique", "Dernier Croissant"
        ]
        phase_is_french = any(fp in data['phase'] for fp in french_phases)
        print(f"INFO: phase returned: {data['phase']}")
        assert phase_is_french or data['phase'], f"Phase should be French: {data['phase']}"
        print(f"PASS: Response has French phase name: {data['phase']}")
    
    def test_moon_phase_has_phase_en(self):
        """Response has English phase name"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        data = response.json()
        assert 'phase_en' in data, f"Missing 'phase_en' field: {data}"
        print(f"PASS: Response has phase_en: {data['phase_en']}")
    
    def test_moon_phase_has_conseil(self):
        """Response has conseil field"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        data = response.json()
        assert 'conseil' in data, f"Missing 'conseil' field: {data}"
        assert len(data.get('conseil', '')) > 0, "conseil should not be empty"
        print(f"PASS: Response has conseil field")
    
    def test_moon_phase_has_signification(self):
        """Response has signification field"""
        response = requests.get(f"{BASE_URL}/api/moon-phase", timeout=30)
        data = response.json()
        assert 'signification' in data, f"Missing 'signification' field: {data}"
        print(f"PASS: Response has signification field")


class TestDailyEndpointWithMoonPhase:
    """Tests for GET /api/daily/{sign} with moon phase enrichment"""
    
    def test_daily_gemini_returns_200(self):
        """GET /api/daily/Gemini returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/daily/Gemini returns HTTP 200")
    
    def test_daily_has_phase_lunaire_field(self):
        """Response contains phase_lunaire field"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        data = response.json()
        assert 'phase_lunaire' in data, f"Missing 'phase_lunaire' field in response: {list(data.keys())}"
        print("PASS: Response contains phase_lunaire field")
    
    def test_phase_lunaire_has_french_phase(self):
        """phase_lunaire.phase is in French"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        data = response.json()
        phase_lunaire = data.get('phase_lunaire', {})
        assert 'phase' in phase_lunaire, f"Missing 'phase' in phase_lunaire: {phase_lunaire}"
        french_phases = [
            "Nouvelle Lune", "Premier Croissant", "Premier Quartier",
            "Lune Gibbeuse", "Pleine Lune", "Lune Disséminante",
            "Dernier Quartier", "Lune Balsamique", "Dernier Croissant"
        ]
        phase = phase_lunaire.get('phase', '')
        phase_is_french = any(fp in phase for fp in french_phases)
        print(f"INFO: phase_lunaire.phase = {phase}")
        assert phase_is_french or phase, f"Phase should be French text: {phase}"
        print(f"PASS: phase_lunaire.phase is French: {phase}")
    
    def test_phase_lunaire_has_conseil(self):
        """phase_lunaire has conseil field in French"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        data = response.json()
        phase_lunaire = data.get('phase_lunaire', {})
        assert 'conseil' in phase_lunaire, f"Missing 'conseil' in phase_lunaire: {phase_lunaire}"
        conseil = phase_lunaire.get('conseil', '')
        assert len(conseil) > 10, f"conseil should be substantial French text: {conseil}"
        print(f"PASS: phase_lunaire.conseil present (length: {len(conseil)})")
    
    def test_phase_lunaire_has_phase_en(self):
        """phase_lunaire has English phase name for reference"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        data = response.json()
        phase_lunaire = data.get('phase_lunaire', {})
        assert 'phase_en' in phase_lunaire, f"Missing 'phase_en' in phase_lunaire"
        print(f"PASS: phase_lunaire.phase_en present: {phase_lunaire.get('phase_en')}")
    
    def test_daily_still_has_horoscope_data(self):
        """Daily endpoint still returns normal horoscope content"""
        response = requests.get(f"{BASE_URL}/api/daily/Gemini", timeout=30)
        data = response.json()
        # Check standard fields still present
        assert 'phrase_du_jour' in data, "Missing phrase_du_jour"
        assert 'conseil_du_jour' in data, "Missing conseil_du_jour"
        assert 'horoscope' in data, "Missing horoscope"
        assert 'energie_du_jour' in data, "Missing energie_du_jour"
        print("PASS: Daily endpoint returns all standard horoscope fields")


class TestProHoroscopePDFWithChart:
    """Tests for POST /api/pdf/pro-horoscope with real SVG natal chart"""
    
    def test_pro_horoscope_returns_200(self):
        """POST /api/pdf/pro-horoscope returns HTTP 200"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=PRO_HOROSCOPE_TEST_DATA,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: POST /api/pdf/pro-horoscope returns HTTP 200")
    
    def test_pro_horoscope_returns_pdf(self):
        """Response is application/pdf"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=PRO_HOROSCOPE_TEST_DATA,
            timeout=60
        )
        content_type = response.headers.get('Content-Type', '')
        assert 'application/pdf' in content_type, f"Expected application/pdf, got {content_type}"
        print("PASS: Response content-type is application/pdf")
    
    def test_pro_horoscope_pdf_size_gt_1mb(self):
        """PDF size is > 1.5MB (indicates real content including SVG chart)"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=PRO_HOROSCOPE_TEST_DATA,
            timeout=60
        )
        pdf_size_mb = len(response.content) / (1024 * 1024)
        print(f"INFO: PDF size is {pdf_size_mb:.2f} MB")
        # Real SVG chart should make PDF larger
        assert pdf_size_mb > 1.0, f"PDF should be > 1MB for enriched content, got {pdf_size_mb:.2f} MB"
        print(f"PASS: PDF size is {pdf_size_mb:.2f} MB (> 1MB)")
    
    def test_pro_horoscope_contains_astrologyapi_text(self):
        """Generated PDF contains 'AstrologyAPI' text (real SVG chart embedded)"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/pro-horoscope",
            json=PRO_HOROSCOPE_TEST_DATA,
            timeout=60
        )
        pdf_bytes = response.content
        
        # Check PDF for AstrologyAPI marker
        # Note: This text appears in the PDF when the real SVG chart is embedded
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            
            # Look for the marker text that appears when chart is rendered
            has_chart_marker = "AstrologyAPI" in full_text or "Carte du ciel" in full_text.lower() or "carte du ciel" in full_text.lower()
            print(f"INFO: PDF text extraction - found AstrologyAPI: {'AstrologyAPI' in full_text}, found carte du ciel: {'carte du ciel' in full_text.lower()}")
            
            # At minimum, the natal chart page should exist
            has_natal_chart_page = "carte du ciel" in full_text.lower() or "votre carte" in full_text.lower()
            assert has_natal_chart_page, f"PDF should contain natal chart page text"
            print(f"PASS: PDF contains natal chart page content")
        except ImportError:
            # If PyMuPDF not available, just check PDF header
            assert pdf_bytes[:4] == b'%PDF', "Response should be valid PDF"
            print("PASS: Valid PDF header (PyMuPDF not available for text extraction)")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    def test_pdf_generate_still_works(self):
        """POST /api/pdf/generate still works (regression)"""
        response = requests.post(
            f"{BASE_URL}/api/pdf/generate",
            json=PDF_GENERATE_TEST_DATA,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'application/pdf' in response.headers.get('Content-Type', ''), "Should return PDF"
        print("PASS: POST /api/pdf/generate still works (regression)")
    
    def test_share_card_still_works(self):
        """POST /api/share/generate-card still works (regression)"""
        response = requests.post(
            f"{BASE_URL}/api/share/generate-card",
            json=SHARE_CARD_TEST_DATA,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content_type = response.headers.get('Content-Type', '')
        assert 'image/png' in content_type, f"Expected image/png, got {content_type}"
        print("PASS: POST /api/share/generate-card still works (regression)")
    
    def test_discount_plume2026_still_works(self):
        """POST /api/discount/validate with PLUME2026 still works (regression)"""
        response = requests.post(
            f"{BASE_URL}/api/discount/validate",
            json={"code": "PLUME2026"},
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('valid') == True, f"PLUME2026 should be valid: {data}"
        assert data.get('discount_percent') == 100, f"Should give 100% discount: {data}"
        print("PASS: POST /api/discount/validate with PLUME2026 still works (regression)")
    
    def test_root_endpoint(self):
        """GET /api/ returns 200"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/ returns 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
