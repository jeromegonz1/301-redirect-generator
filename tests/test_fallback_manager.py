"""
Tests TDD pour le gestionnaire de fallbacks 302 (US013)
Aucun hardcoding d'URLs - Toutes les données viennent des tests
"""

import pytest
from typing import List, Dict

class TestFallbackManager:
    """Tests pour la gestion des fallbacks 302"""
    
    def test_fallback_manager_initialization(self):
        """Test initialisation du gestionnaire de fallbacks"""
        from src.fallback_manager import FallbackManager
        
        # Test avec langue par défaut
        manager = FallbackManager()
        assert manager.default_fallback_lang == "fr"
        
        # Test avec langue personnalisée
        manager_en = FallbackManager(default_fallback_lang="en")
        assert manager_en.default_fallback_lang == "en"
    
    def test_detect_missing_languages(self):
        """Test détection des langues manquantes"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        # URLs de test (pas de hardcoding)
        old_urls = [
            "/fr/page1", "/fr/page2",  # FR présent partout
            "/en/page1", "/en/page2",  # EN présent partout  
            "/es/page1", "/es/page2",  # ES seulement dans ancien
            "/de/page1"                # DE seulement dans ancien
        ]
        
        new_urls = [
            "/fr/nouvelle1", "/fr/nouvelle2",  # FR migré
            "/en/new1", "/en/new2"             # EN migré  
            # ES et DE absents du nouveau site
        ]
        
        missing = manager.detect_missing_languages(old_urls, new_urls)
        
        # Vérifications
        assert "es" in missing
        assert "de" in missing
        assert "fr" not in missing  # Présent dans nouveau
        assert "en" not in missing  # Présent dans nouveau
        assert len(missing) == 2
    
    def test_generate_302_redirects(self):
        """Test génération des redirections 302"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager(default_fallback_lang="fr")
        
        # Simulation d'URLs groupées par langue
        old_urls_grouped = {
            "es": ["/es/contacto", "/es/servicios"],
            "it": ["/it/contatto"]
        }
        
        missing_langs = ["es", "it"]
        
        redirects = manager.generate_302_redirects(missing_langs, old_urls_grouped)
        
        # Vérifications
        assert len(redirects) == 3  # 2 ES + 1 IT
        
        # Toutes les redirections pointent vers /fr/
        for source, target in redirects:
            assert target == "/fr/"
        
        # URLs sources correctes
        sources = [r[0] for r in redirects]
        assert "/es/contacto" in sources
        assert "/es/servicios" in sources
        assert "/it/contatto" in sources
    
    def test_generate_302_redirects_custom_fallback(self):
        """Test génération avec langue fallback personnalisée"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        old_urls_grouped = {
            "es": ["/es/test1", "/es/test2"]
        }
        
        # Fallback vers anglais au lieu de français
        redirects = manager.generate_302_redirects(["es"], old_urls_grouped, fallback_lang="en")
        
        for source, target in redirects:
            assert target == "/en/"
    
    def test_format_htaccess_302(self):
        """Test formatage des redirections en .htaccess"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        # Redirections de test
        redirects = [
            ("/es/contacto", "/fr/"),
            ("/es/servicios", "/fr/"), 
            ("/it/contatto", "/fr/")
        ]
        
        htaccess = manager.format_htaccess_302(redirects)
        
        # Vérifications du format
        assert "Redirect 302" in htaccess
        assert "/es/contacto" in htaccess
        assert "/fr/" in htaccess
        assert "temporaires" in htaccess  # Commentaire
        assert "Générées automatiquement" in htaccess
    
    def test_format_htaccess_302_empty(self):
        """Test formatage avec liste vide"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        htaccess = manager.format_htaccess_302([])
        assert htaccess == ""
    
    def test_get_fallback_stats(self):
        """Test génération des statistiques de fallback"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        # URLs de test avec répartition connue
        old_urls = [
            "/fr/p1", "/fr/p2", "/fr/p3",  # 3 FR
            "/en/p1", "/en/p2",            # 2 EN
            "/es/p1", "/es/p2", "/es/p3"   # 3 ES (sera manquant)
        ]
        
        new_urls = [
            "/fr/n1", "/fr/n2",  # FR migré
            "/en/n1"             # EN migré (partiellement)
            # ES absent = fallback nécessaire
        ]
        
        stats = manager.get_fallback_stats(old_urls, new_urls)
        
        # Vérifications
        assert stats["total_old_urls"] == 8
        assert stats["total_new_urls"] == 3
        assert stats["languages_old"] == 3  # FR, EN, ES
        assert stats["languages_new"] == 2  # FR, EN seulement
        assert "es" in stats["missing_languages"]
        assert stats["fallback_count"] == 3  # 3 URLs ES
        
        # Détails par langue
        assert stats["language_details"]["es"]["missing"] == True
        assert stats["language_details"]["es"]["fallback_needed"] == 3
        assert stats["language_details"]["fr"]["missing"] == False
    
    def test_generate_fallback_report(self):
        """Test génération du rapport textuel"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        old_urls = ["/fr/test", "/es/test", "/it/test"]
        new_urls = ["/fr/nouveau"]  # Seul FR migré
        
        report = manager.generate_fallback_report(old_urls, new_urls)
        
        # Vérifications du contenu
        assert "Rapport des redirections temporaires" in report
        assert "Espagnol" in report or "🇪🇸" in report
        assert "Italien" in report or "🇮🇹" in report
        assert "2 redirections 302" in report  # ES + IT
        assert "/fr/" in report  # Langue de fallback
    
    def test_set_default_fallback(self):
        """Test modification de la langue de fallback par défaut"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager(default_fallback_lang="fr")
        
        # Modification vers anglais
        manager.set_default_fallback("en")
        assert manager.default_fallback_lang == "en"
    
    def test_get_supported_fallback_languages(self):
        """Test liste des langues supportées pour fallback"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        languages = manager.get_supported_fallback_languages()
        
        # Vérifications
        assert isinstance(languages, list)
        assert "fr" in languages
        assert "en" in languages
        assert "de" in languages
        assert len(languages) >= 6  # Au moins les 6 principales
    
    def test_integration_with_language_detector(self):
        """Test intégration avec le détecteur de langues"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        # URLs avec patterns complexes
        complex_old_urls = [
            "/fr/contact-entreprise",
            "/contact-en.html", 
            "www.site.de/services",
            "/es/contacto-empresa"
        ]
        
        complex_new_urls = [
            "/fr/contact",  # Seul FR disponible
        ]
        
        missing = manager.detect_missing_languages(complex_old_urls, complex_new_urls)
        
        # Doit détecter EN, DE, ES comme manquants
        assert "en" in missing
        assert "de" in missing  
        assert "es" in missing
        assert "fr" not in missing
    
    def test_no_fallback_needed(self):
        """Test cas où aucun fallback n'est nécessaire"""
        from src.fallback_manager import FallbackManager
        
        manager = FallbackManager()
        
        # Toutes les langues présentes dans les deux sites
        old_urls = ["/fr/page1", "/en/page1"]
        new_urls = ["/fr/nouvelle", "/en/new"]
        
        missing = manager.detect_missing_languages(old_urls, new_urls)
        assert len(missing) == 0
        
        stats = manager.get_fallback_stats(old_urls, new_urls)
        assert stats["fallback_count"] == 0
        assert stats["fallback_percentage"] == 0.0