"""
Tests pour la saisie manuelle d'URLs
US-3: En tant qu'utilisateur, je veux pouvoir saisir manuellement des URLs
"""

import pytest
from src.manual_input import ManualInputParser


class TestManualInputParser:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.parser = ManualInputParser()
    
    def test_should_parse_line_separated_urls(self):
        """Test: doit parser les URLs séparées par des lignes"""
        input_text = """https://example.com/page1
https://example.com/page2
https://example.com/page3"""
        
        expected = [
            "https://example.com/page1",
            "https://example.com/page2", 
            "https://example.com/page3"
        ]
        
        result = self.parser.parse_urls(input_text)
        assert result == expected
    
    def test_should_handle_empty_lines(self):
        """Test: doit ignorer les lignes vides"""
        input_text = """https://example.com/page1

https://example.com/page2

https://example.com/page3"""
        
        expected = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        result = self.parser.parse_urls(input_text)
        assert result == expected
    
    def test_should_trim_whitespace(self):
        """Test: doit supprimer les espaces en début/fin"""
        input_text = """  https://example.com/page1  
   https://example.com/page2   
https://example.com/page3"""
        
        expected = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        result = self.parser.parse_urls(input_text)
        assert result == expected
    
    def test_should_validate_urls(self):
        """Test: doit valider les URLs et signaler les erreurs"""
        input_text = """https://example.com/valid
invalid-url
https://another-valid.com/page
not-an-url-at-all"""
        
        result = self.parser.parse_urls(input_text)
        
        # Doit retourner seulement les URLs valides
        expected_valid = [
            "https://example.com/valid",
            "https://another-valid.com/page"
        ]
        
        assert result == expected_valid
        
        # Doit avoir des erreurs pour les URLs invalides
        errors = self.parser.get_last_errors()
        assert len(errors) == 2
        assert "invalid-url" in errors[0]
        assert "not-an-url-at-all" in errors[1]
    
    def test_should_handle_different_protocols(self):
        """Test: doit accepter différents protocoles"""
        input_text = """https://example.com/secure
http://example.com/normal
ftp://files.example.com/file"""
        
        expected = [
            "https://example.com/secure",
            "http://example.com/normal",
            "ftp://files.example.com/file"
        ]
        
        result = self.parser.parse_urls(input_text)
        assert result == expected
    
    def test_should_deduplicate_urls(self):
        """Test: doit dédupliquer les URLs identiques"""
        input_text = """https://example.com/page1
https://example.com/page2
https://example.com/page1
https://example.com/page3
https://example.com/page2"""
        
        expected = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        result = self.parser.parse_urls(input_text, deduplicate=True)
        assert result == expected
    
    def test_should_handle_comma_separated_urls(self):
        """Test: doit gérer les URLs séparées par des virgules"""
        input_text = "https://example.com/page1, https://example.com/page2, https://example.com/page3"
        
        expected = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        result = self.parser.parse_urls(input_text, separator=',')
        assert result == expected
    
    def test_should_get_statistics(self):
        """Test: doit retourner des statistiques de parsing"""
        input_text = """https://example.com/page1
invalid-url
https://example.com/page2
another-invalid"""
        
        result = self.parser.parse_urls(input_text)
        stats = self.parser.get_last_statistics()
        
        assert stats['total_lines'] == 4
        assert stats['valid_urls'] == 2
        assert stats['invalid_urls'] == 2
        assert stats['empty_lines'] == 0