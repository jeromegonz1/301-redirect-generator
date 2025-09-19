"""
Tests pour le nettoyage des URLs de destination
US-2: En tant qu'utilisateur, je veux des URLs sans artefacts de préproduction
"""

import pytest
from src.url_cleaner import URLCleaner


class TestURLCleaner:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.cleaner = URLCleaner()
    
    def test_should_remove_les_cascades_path(self):
        """Test: doit supprimer /les-cascades/ des URLs"""
        urls_with_cascades = [
            "https://www.campinglescascades.com/les-cascades/de/",
            "https://www.campinglescascades.com/les-cascades/en/about/",
            "https://www.campinglescascades.com/les-cascades/fr/contact/"
        ]
        
        expected = [
            "https://www.campinglescascades.com/de/",
            "https://www.campinglescascades.com/en/about/",
            "https://www.campinglescascades.com/fr/contact/"
        ]
        
        for i, url in enumerate(urls_with_cascades):
            result = self.cleaner.clean_url(url)
            assert result == expected[i], f"Expected {expected[i]}, got {result}"
    
    def test_should_not_modify_clean_urls(self):
        """Test: ne doit pas modifier les URLs déjà propres"""
        clean_urls = [
            "https://www.campinglescascades.com/de/",
            "https://example.com/about/",
            "https://site.com/contact.html"
        ]
        
        for url in clean_urls:
            result = self.cleaner.clean_url(url)
            assert result == url, f"URL should not be modified: {url}"
    
    def test_should_handle_custom_patterns(self):
        """Test: doit gérer des patterns personnalisés"""
        custom_cleaner = URLCleaner(patterns_to_remove=['/staging/', '/preprod/'])
        
        test_cases = [
            ("https://site.com/staging/page/", "https://site.com/page/"),
            ("https://site.com/preprod/about/", "https://site.com/about/"),
            ("https://site.com/normal/", "https://site.com/normal/")
        ]
        
        for original, expected in test_cases:
            result = custom_cleaner.clean_url(original)
            assert result == expected
    
    def test_clean_urls_list(self):
        """Test: nettoyage d'une liste d'URLs"""
        urls = [
            "https://www.campinglescascades.com/les-cascades/de/",
            "https://www.site.com/about/",
            "https://www.campinglescascades.com/les-cascades/en/contact/"
        ]
        
        expected = [
            "https://www.campinglescascades.com/de/",
            "https://www.site.com/about/",
            "https://www.campinglescascades.com/en/contact/"
        ]
        
        result = self.cleaner.clean_urls(urls)
        assert result == expected
    
    def test_should_handle_edge_cases(self):
        """Test: gestion des cas limites"""
        edge_cases = [
            ("", ""),  # URL vide
            ("https://site.com/les-cascades/", "https://site.com/"),  # Juste le pattern
            ("https://site.com/les-cascades", "https://site.com/"),  # Sans slash final
            ("invalid-url", "invalid-url")  # URL invalide
        ]
        
        for original, expected in edge_cases:
            result = self.cleaner.clean_url(original)
            assert result == expected
    
    def test_should_preserve_query_params_and_fragments(self):
        """Test: doit préserver les paramètres et fragments"""
        test_cases = [
            (
                "https://site.com/les-cascades/page/?param=value#section",
                "https://site.com/page/?param=value#section"
            ),
            (
                "https://site.com/les-cascades/search?q=test&lang=fr",
                "https://site.com/search?q=test&lang=fr"
            )
        ]
        
        for original, expected in test_cases:
            result = self.cleaner.clean_url(original)
            assert result == expected