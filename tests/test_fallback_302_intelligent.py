"""
Tests TDD pour le Sprint 3 - Fallback intelligent 302 pour URLs non matchées
US009 - Fallback automatique en 302 vers page d'accueil de la langue
Aucun hardcoding - Toutes les données viennent des tests
"""

import pytest
from typing import List, Dict
import csv
import os
from unittest.mock import Mock, patch


class TestFallback302Intelligent:
    """Tests TDD pour le fallback intelligent 302 (Sprint 3)"""
    
    def test_detect_unmatched_urls_after_ai_processing(self):
        """Test détection des URLs non matchées après traitement IA"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # URLs de test - données non hardcodées
        old_urls = [
            "/fr/page1", "/fr/page2", "/fr/page-orpheline", 
            "/en/article1", "/en/article-missing",
            "/de/seite1", "/de/verlorene-seite"
        ]
        
        # Résultats simulés du matching IA (seulement certaines trouvées)
        ai_matches = [
            {"old_url": "/fr/page1", "new_url": "/fr/nouvelle1", "confidence": 0.8},
            {"old_url": "/en/article1", "new_url": "/en/new-article", "confidence": 0.9},
            {"old_url": "/de/seite1", "new_url": "/de/neue-seite", "confidence": 0.7}
        ]
        
        # Test détection des non-matchées
        unmatched = intelligent_fallback.detect_unmatched_urls(old_urls, ai_matches)
        
        expected_unmatched = ["/fr/page2", "/fr/page-orpheline", "/en/article-missing", "/de/verlorene-seite"]
        assert set(unmatched) == set(expected_unmatched)
        assert len(unmatched) == 4

    def test_generate_302_redirect_to_language_home(self):
        """Test génération redirection 302 vers page d'accueil de la langue"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # Test extraction de langue et génération redirect 302
        test_cases = [
            ("/fr/page-orpheline", "/fr/"),
            ("/en/missing-article", "/en/"),
            ("/de/verlorene-seite", "/de/"),
            ("/es/pagina-perdida", "/es/"),
            ("/it/pagina-mancante", "/it/"),
            ("/nl/ontbrekende-pagina", "/nl/")
        ]
        
        for old_url, expected_home in test_cases:
            redirect_302 = intelligent_fallback.generate_302_redirect(old_url)
            
            assert redirect_302["type"] == "302"
            assert redirect_302["old_url"] == old_url
            assert redirect_302["target_url"] == expected_home
            assert redirect_302["comment"] == "# Fallback temporaire - à retraiter manuellement"

    def test_generate_302_redirect_with_full_domain(self):
        """Test génération 302 avec URLs complètes (domaine inclus)"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # Test avec URLs complètes
        full_url = "https://ancien-site.com/fr/page-introuvable"
        redirect_302 = intelligent_fallback.generate_302_redirect(full_url)
        
        assert redirect_302["type"] == "302"
        assert redirect_302["old_url"] == "https://ancien-site.com/fr/page-introuvable"
        assert redirect_302["target_url"] == "/fr/"
        assert "Fallback temporaire" in redirect_302["comment"]

    def test_extract_language_from_url(self):
        """Test extraction de langue depuis URL"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # Test différents formats d'URLs
        test_cases = [
            ("/fr/page", "fr"),
            ("/en/article", "en"), 
            ("/de/seite", "de"),
            ("https://site.com/es/pagina", "es"),
            ("https://site.com/it/pagina/", "it"),
            ("/nl/test/sous-page", "nl"),
            ("/no-lang-here", None),  # Cas sans langue détectable
            ("/", None)  # URL racine
        ]
        
        for url, expected_lang in test_cases:
            detected_lang = intelligent_fallback.extract_language_from_url(url)
            assert detected_lang == expected_lang

    def test_export_fallback_urls_to_csv(self):
        """Test export CSV des URLs en fallback 302"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # URLs non matchées de test
        unmatched_urls = [
            "/fr/page-orpheline",
            "/en/missing-article", 
            "/de/verlorene-seite"
        ]
        
        # Génération des fallbacks 302
        fallback_data = []
        for url in unmatched_urls:
            redirect = intelligent_fallback.generate_302_redirect(url)
            fallback_data.append({
                "old_url": url,
                "target_url": redirect["target_url"],
                "language": intelligent_fallback.extract_language_from_url(url),
                "status": "fallback_302",
                "comment": "À retraiter manuellement"
            })
        
        # Test export CSV
        csv_content = intelligent_fallback.export_to_csv(fallback_data)
        
        # Vérifications CSV
        assert "old_url,target_url,language,status,comment" in csv_content
        assert "/fr/page-orpheline,/fr/,fr,fallback_302" in csv_content
        assert "/en/missing-article,/en/,en,fallback_302" in csv_content
        assert "/de/verlorene-seite,/de/,de,fallback_302" in csv_content
        assert "À retraiter manuellement" in csv_content

    def test_generate_htaccess_with_302_annotations(self):
        """Test génération .htaccess avec annotations 302"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent()
        
        # Données de test : mix de 301 normales et 302 fallback
        redirect_data = [
            # Redirections 301 normales (trouvées par IA)
            {"type": "301", "old_url": "/fr/page1", "new_url": "/fr/nouvelle1"},
            {"type": "301", "old_url": "/en/article", "new_url": "/en/new-article"},
            # Redirections 302 fallback  
            {"type": "302", "old_url": "/fr/page-orpheline", "target_url": "/fr/", 
             "comment": "# Fallback temporaire - à retraiter manuellement"},
            {"type": "302", "old_url": "/de/verlorene-seite", "target_url": "/de/",
             "comment": "# Fallback temporaire - à retraiter manuellement"}
        ]
        
        htaccess_content = intelligent_fallback.generate_htaccess_with_fallbacks(redirect_data)
        
        # Vérifications du contenu .htaccess
        assert "Redirect 301 /fr/page1 /fr/nouvelle1" in htaccess_content
        assert "Redirect 301 /en/article /en/new-article" in htaccess_content
        
        # Vérifications des 302 avec annotations
        assert "# Fallback temporaire - à retraiter manuellement" in htaccess_content
        assert "Redirect 302 /fr/page-orpheline /fr/" in htaccess_content
        assert "Redirect 302 /de/verlorene-seite /de/" in htaccess_content

    def test_fallback_302_configuration_options(self):
        """Test options de configuration pour le fallback 302"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        # Test avec fallback activé
        intelligent_fallback_on = Fallback302Intelligent(enable_fallback_302=True)
        assert intelligent_fallback_on.enable_fallback_302 is True
        
        # Test avec fallback désactivé
        intelligent_fallback_off = Fallback302Intelligent(enable_fallback_302=False)
        assert intelligent_fallback_off.enable_fallback_302 is False
        
        # Test langue de fallback par défaut
        intelligent_fallback_default = Fallback302Intelligent(default_fallback_lang="en")
        assert intelligent_fallback_default.default_fallback_lang == "en"

    def test_fallback_302_disabled_behavior(self):
        """Test comportement quand fallback 302 est désactivé"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent(enable_fallback_302=False)
        
        unmatched_urls = ["/fr/page-orpheline", "/en/missing"]
        
        # Quand désactivé, ne doit pas générer de redirections 302
        fallbacks = intelligent_fallback.process_unmatched_urls(unmatched_urls)
        
        # Doit retourner une liste vide ou des données de log uniquement
        if fallbacks:
            # Si quelque chose est retourné, ce ne doit être que du logging
            for item in fallbacks:
                assert item.get("type") != "302"
        else:
            assert fallbacks == []

    def test_integration_with_ai_mapper_results(self):
        """Test intégration avec les résultats de l'AI Mapper"""
        from src.fallback_302_intelligent import Fallback302Intelligent
        
        intelligent_fallback = Fallback302Intelligent(enable_fallback_302=True)
        
        # Simulation résultats complets d'une session IA
        ai_session_results = {
            "matched_urls": [
                {"old_url": "/fr/page1", "new_url": "/fr/nouvelle1", "confidence": 0.8},
                {"old_url": "/en/article", "new_url": "/en/new-article", "confidence": 0.9}
            ],
            "unmatched_urls": ["/fr/page-orpheline", "/en/missing-article", "/de/verlorene"]
        }
        
        # Traitement des non-matchées
        fallback_results = intelligent_fallback.process_ai_results(ai_session_results)
        
        assert "fallback_302_redirects" in fallback_results
        assert "csv_export_data" in fallback_results
        assert "htaccess_lines" in fallback_results
        
        # Vérification des redirections 302 générées
        redirects_302 = fallback_results["fallback_302_redirects"]
        assert len(redirects_302) == 3
        
        for redirect in redirects_302:
            assert redirect["type"] == "302"
            assert redirect["target_url"] in ["/fr/", "/en/", "/de/"]