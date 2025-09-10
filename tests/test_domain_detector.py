"""
Tests TDD pour la détection automatique du domaine cible
Fire Snake 301 - No hardcoding philosophy
"""

import pytest
from src.domain_detector import DomainDetector


class TestDomainDetector:
    """Tests pour la détection intelligente de domaine cible"""
    
    def test_extract_domain_from_single_url(self):
        """Test 1: Extraction de domaine depuis une seule URL"""
        detector = DomainDetector()
        
        # Test avec URL complète
        domain = detector.extract_domain_from_urls(["https://www.example.com/page"])
        assert domain == "https://www.example.com"
        
        # Test sans www
        domain = detector.extract_domain_from_urls(["https://example.com/about"])
        assert domain == "https://example.com"
    
    def test_extract_domain_from_multiple_urls(self):
        """Test 2: Extraction depuis plusieurs URLs du même domaine"""
        detector = DomainDetector()
        
        urls = [
            "https://www.lesquatredauphins.fr/page1",
            "https://www.lesquatredauphins.fr/page2",
            "https://www.lesquatredauphins.fr/about"
        ]
        
        domain = detector.extract_domain_from_urls(urls)
        assert domain == "https://www.lesquatredauphins.fr"
    
    def test_extract_domain_from_mixed_protocols(self):
        """Test 3: Gestion de protocoles mixtes (préférer HTTPS)"""
        detector = DomainDetector()
        
        urls = [
            "http://www.example.com/page1",
            "https://www.example.com/page2"
        ]
        
        domain = detector.extract_domain_from_urls(urls)
        assert domain == "https://www.example.com"  # Préfère HTTPS
    
    def test_extract_domain_from_sitemap_xml(self):
        """Test 4: Extraction depuis sitemap XML"""
        detector = DomainDetector()
        
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.lesquatredauphins.fr/</loc>
    </url>
    <url>
        <loc>https://www.lesquatredauphins.fr/about</loc>
    </url>
</urlset>'''
        
        domain = detector.extract_domain_from_sitemap(sitemap_xml)
        assert domain == "https://www.lesquatredauphins.fr"
    
    def test_extract_domain_handles_empty_input(self):
        """Test 5: Gestion des entrées vides"""
        detector = DomainDetector()
        
        assert detector.extract_domain_from_urls([]) is None
        assert detector.extract_domain_from_urls(["", "  "]) is None
        assert detector.extract_domain_from_sitemap("") is None
    
    def test_extract_domain_from_invalid_urls(self):
        """Test 6: Gestion des URLs invalides"""
        detector = DomainDetector()
        
        invalid_urls = ["not-a-url", "ftp://example.com", ""]
        domain = detector.extract_domain_from_urls(invalid_urls)
        assert domain is None
    
    def test_smart_domain_detection_from_text_input(self):
        """Test 7: Détection intelligente depuis input utilisateur"""
        detector = DomainDetector()
        
        # Test sitemap XML
        xml_input = '''<loc>https://www.lesquatredauphins.fr/page1</loc>
<loc>https://www.lesquatredauphins.fr/page2</loc>'''
        
        domain = detector.detect_from_user_input(xml_input)
        assert domain == "https://www.lesquatredauphins.fr"
        
        # Test liste d'URLs brutes
        raw_urls = '''https://www.example.com/page1
https://www.example.com/page2
https://www.example.com/about'''
        
        domain = detector.detect_from_user_input(raw_urls)
        assert domain == "https://www.example.com"
    
    def test_normalize_domain_output(self):
        """Test 8: Normalisation du domaine de sortie"""
        detector = DomainDetector()
        
        # Supprime les slashes finaux
        urls = ["https://www.example.com/page/"]
        domain = detector.extract_domain_from_urls(urls)
        assert not domain.endswith('/')
        
        # Garde la forme canonique
        assert domain.startswith('https://')