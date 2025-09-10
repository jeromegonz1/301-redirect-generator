"""
Tests TDD pour corriger les problèmes de doublons et redirections incorrectes
Fire Snake 301 - No hardcoding philosophy
"""

import pytest
from src.advanced_interface import remove_duplicate_redirects


class TestRedirectDeduplication:
    """Tests pour la déduplication et correction des redirections"""
    
    def test_remove_duplicate_redirects_basic(self):
        """Test 1: Suppression des doublons basiques"""
        redirects = [
            {'source': 'https://example.com/page1', 'target': 'https://new.com/page1'},
            {'source': 'https://example.com/page1', 'target': 'https://new.com/page1'},  # doublon
            {'source': 'https://example.com/page2', 'target': 'https://new.com/page2'},
        ]
        
        result = remove_duplicate_redirects(redirects)
        assert len(result) == 2
        assert result[0]['source'] == 'https://example.com/page1'
        assert result[1]['source'] == 'https://example.com/page2'
    
    def test_remove_self_redirects(self):
        """Test 2: Suppression des redirections vers soi-même"""
        redirects = [
            {'source': 'https://example.com/page1', 'target': 'https://example.com/page1'},  # self
            {'source': 'https://example.com/page2', 'target': 'https://new.com/page2'},
        ]
        
        result = remove_duplicate_redirects(redirects)
        assert len(result) == 1
        assert result[0]['source'] == 'https://example.com/page2'
    
    def test_fallback_only_for_unmatched_urls(self):
        """Test 3: Fallback UNIQUEMENT pour URLs non matchées par IA"""
        redirects = [
            # Correspondance IA trouvée - ne devrait PAS avoir de fallback
            {'source': 'https://example.com/fr/contact', 'target': 'https://new.com/contact', 'confidence': 0.8, 'type': '301'},
            # URL non matchée - DOIT avoir un fallback vers racine langue
            {'source': 'https://example.com/fr/page-orpheline', 'target': 'https://new.com/fr/', 'confidence': 0.0, 'type': '302'},
        ]
        
        # Les deux redirections sont valides car pour des URLs différentes
        result = remove_duplicate_redirects(redirects)
        assert len(result) == 2
    
    def test_prioritize_high_confidence_over_fallback(self):
        """Test 4: Priorité aux correspondances IA vs fallbacks"""
        redirects = [
            # Fallback 302 (confidence = 0)
            {'source': 'https://example.com/room/25-mirabeau', 'target': 'https://new.com/fr/', 'confidence': 0.0, 'type': '302'},
            # Correspondance IA (confidence > 0) 
            {'source': 'https://example.com/room/25-mirabeau', 'target': 'https://new.com/fr/chambre/chambre-25', 'confidence': 0.85, 'type': '301'},
        ]
        
        # Fonction améliorée devrait préférer la correspondance IA
        result = remove_duplicate_redirects(redirects)
        assert len(result) == 1
        assert result[0]['target'] == 'https://new.com/fr/chambre/chambre-25'
        assert result[0]['type'] == '301'