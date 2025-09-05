"""
Tests TDD pour le détecteur de langues (US011)
Aucune URL hardcodée - Toutes les URLs viennent des paramètres de test
"""

import pytest
from typing import Dict, List

class TestLanguageDetector:
    """Tests pour la détection automatique des langues"""
    
    def test_detect_french_prefix_pattern(self):
        """Test détection français avec préfixe /fr/"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        test_urls = [
            "/fr/contact",
            "/fr/services/camping", 
            "/fr/blog/article-1"
        ]
        
        for url in test_urls:
            assert detector.detect(url) == "fr"
    
    def test_detect_english_patterns(self):
        """Test détection anglais avec différents patterns"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        test_cases = [
            ("/en/about-us", "en"),          # Préfixe standard
            ("/contact/en", "en"),           # Suffixe
            ("/contact-en.html", "en"),      # Tiret + extension
            ("en.example.com/page", "en")    # Sous-domaine
        ]
        
        for url, expected_lang in test_cases:
            assert detector.detect(url) == expected_lang
    
    def test_detect_german_patterns(self):
        """Test détection allemand"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        test_cases = [
            ("/de/uber-uns", "de"),
            ("/kontakt-de", "de"),
            ("www.site.de/page", "de")
        ]
        
        for url, expected_lang in test_cases:
            assert detector.detect(url) == expected_lang
    
    def test_detect_spanish_and_italian(self):
        """Test détection espagnol et italien"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        test_cases = [
            ("/es/contacto", "es"),
            ("/it/contatto", "it"),
            ("/nl/contact", "nl")
        ]
        
        for url, expected_lang in test_cases:
            assert detector.detect(url) == expected_lang
    
    def test_default_language_fallback(self):
        """Test fallback vers langue par défaut"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector(default_language="fr")
        
        # URLs sans indication de langue
        test_urls = [
            "/contact",
            "/services", 
            "/blog/article-sans-langue"
        ]
        
        for url in test_urls:
            assert detector.detect(url) == "fr"
    
    def test_custom_default_language(self):
        """Test avec langue par défaut personnalisée"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector(default_language="en")
        
        # URL sans pattern linguistique
        assert detector.detect("/simple-page") == "en"
    
    def test_group_by_language(self):
        """Test groupement des URLs par langue"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        # URLs de test (pas de hardcoding)
        test_urls = [
            "/fr/accueil",
            "/fr/contact", 
            "/en/home",
            "/en/about",
            "/de/startseite",
            "/contact"  # Default FR
        ]
        
        grouped = detector.group_by_language(test_urls)
        
        # Vérifications
        assert "fr" in grouped
        assert "en" in grouped  
        assert "de" in grouped
        
        assert len(grouped["fr"]) == 3  # 2 /fr/ + 1 default
        assert len(grouped["en"]) == 2
        assert len(grouped["de"]) == 1
        
        # Vérifier contenu
        assert "/fr/accueil" in grouped["fr"]
        assert "/contact" in grouped["fr"]  # Fallback
        assert "/en/home" in grouped["en"]
    
    def test_get_language_stats(self):
        """Test statistiques de répartition par langue"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        # URLs de test avec répartition connue
        test_urls = [
            "/fr/page1", "/fr/page2", "/fr/page3",  # 3 FR
            "/en/page1", "/en/page2",               # 2 EN
            "/de/page1",                            # 1 DE
            "/page-sans-langue"                     # 1 FR (default)
        ]
        
        stats = detector.get_language_stats(test_urls)
        
        assert stats["fr"] == 4  # 3 explicites + 1 default
        assert stats["en"] == 2
        assert stats["de"] == 1
        assert sum(stats.values()) == len(test_urls)
    
    def test_detect_bulk_performance(self):
        """Test détection en lot pour performance"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        # Simulation d'un gros volume (pas de hardcoding)
        test_urls = []
        for i in range(100):
            test_urls.extend([
                f"/fr/page-{i}",
                f"/en/page-{i}",
                f"/de/seite-{i}"
            ])
        
        # Détection en lot
        results = detector.detect_bulk(test_urls)
        
        # Vérifications
        assert len(results) == len(test_urls)
        
        # Compter par langue
        fr_count = sum(1 for lang in results.values() if lang == "fr")
        en_count = sum(1 for lang in results.values() if lang == "en") 
        de_count = sum(1 for lang in results.values() if lang == "de")
        
        assert fr_count == 100
        assert en_count == 100
        assert de_count == 100
    
    def test_no_false_positives(self):
        """Test éviter les faux positifs"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        # URLs qui pourraient être confondues
        tricky_urls = [
            "/friend/contact",     # 'fr' dans 'friend' mais pas français
            "/content/about",      # 'en' dans 'content' mais pas anglais
            "/advanced/help"       # 'de' dans 'advanced' mais pas allemand
        ]
        
        for url in tricky_urls:
            # Doit être détecté comme langue par défaut (fr), pas la langue "cachée"
            assert detector.detect(url) == "fr"
    
    def test_case_insensitive_detection(self):
        """Test détection insensible à la casse"""
        from src.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        test_cases = [
            ("/FR/contact", "fr"),
            ("/EN/about", "en"),
            ("/DE/kontakt", "de"),
            ("/Es/contacto", "es")
        ]
        
        for url, expected_lang in test_cases:
            assert detector.detect(url) == expected_lang