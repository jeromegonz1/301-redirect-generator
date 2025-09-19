"""
Tests pour le SmartInputParser
US-2.1: En tant qu'utilisateur, je veux pouvoir coller n'importe quel format d'URLs
et que l'app détecte automatiquement le format
"""

import pytest
from src.smart_input_parser import SmartInputParser


class TestSmartInputParser:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.parser = SmartInputParser()
    
    def test_should_detect_and_parse_simple_text_urls(self):
        """Test: doit détecter et parser des URLs texte simple"""
        input_text = """https://example.com/page1
https://example.com/page2
https://example.com/page3"""
        
        result = self.parser.detect_and_parse(input_text)
        
        assert len(result) == 3
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result
        assert "https://example.com/page3" in result
    
    def test_should_detect_and_parse_xml_sitemap(self):
        """Test: doit détecter et parser un sitemap XML"""
        xml_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/about</loc>
    <lastmod>2024-01-02</lastmod>
  </url>
</urlset>"""
        
        result = self.parser.detect_and_parse(xml_sitemap)
        
        assert len(result) == 2
        assert "https://example.com/" in result
        assert "https://example.com/about" in result
    
    def test_should_detect_and_parse_json_urls(self):
        """Test: doit détecter et parser des URLs au format JSON"""
        json_input = """[
  "https://example.com/api/page1",
  "https://example.com/api/page2",
  "https://example.com/api/page3"
]"""
        
        result = self.parser.detect_and_parse(json_input)
        
        assert len(result) == 3
        assert "https://example.com/api/page1" in result
        assert "https://example.com/api/page2" in result
        assert "https://example.com/api/page3" in result
    
    def test_should_detect_and_parse_csv_urls(self):
        """Test: doit détecter et parser des URLs au format CSV"""
        csv_input = """url,status,description
https://example.com/page1,active,Homepage
https://example.com/page2,active,About page
https://example.com/page3,inactive,Contact"""
        
        result = self.parser.detect_and_parse(csv_input)
        
        assert len(result) == 3
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result
        assert "https://example.com/page3" in result
    
    def test_should_handle_empty_input(self):
        """Test: doit gérer les entrées vides"""
        result = self.parser.detect_and_parse("")
        assert result == []
        
        result = self.parser.detect_and_parse("   ")
        assert result == []
    
    def test_should_handle_malformed_xml(self):
        """Test: doit gérer les XML malformés"""
        malformed_xml = """<urlset>
  <url>
    <loc>https://example.com/</loc>
  </url>
  <!-- XML non fermé -->"""
        
        # Ne doit pas planter, retourner une liste vide ou fallback
        result = self.parser.detect_and_parse(malformed_xml)
        assert isinstance(result, list)
    
    def test_should_handle_malformed_json(self):
        """Test: doit gérer les JSON malformés"""
        malformed_json = """[
  "https://example.com/page1",
  "https://example.com/page2"
  // JSON non fermé"""
        
        # Ne doit pas planter, retourner une liste vide ou fallback
        result = self.parser.detect_and_parse(malformed_json)
        assert isinstance(result, list)
    
    def test_should_filter_invalid_urls(self):
        """Test: doit filtrer les URLs invalides"""
        input_text = """https://example.com/valid1
not-a-url
https://example.com/valid2
just some text
https://example.com/valid3"""
        
        result = self.parser.detect_and_parse(input_text)
        
        # Doit contenir seulement les URLs valides
        assert len(result) == 3
        assert "https://example.com/valid1" in result
        assert "https://example.com/valid2" in result
        assert "https://example.com/valid3" in result
        assert "not-a-url" not in result
        assert "just some text" not in result
    
    def test_should_deduplicate_urls(self):
        """Test: doit dédupliquer les URLs"""
        input_text = """https://example.com/page1
https://example.com/page2
https://example.com/page1
https://example.com/page3
https://example.com/page2"""
        
        result = self.parser.detect_and_parse(input_text)
        
        assert len(result) == 3
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result
        assert "https://example.com/page3" in result
    
    def test_should_detect_format_correctly(self):
        """Test: doit détecter le format correctement"""
        # Test détection XML
        xml_input = "<?xml version='1.0'?><urlset></urlset>"
        assert self.parser.detect_format(xml_input) == "xml"
        
        # Test détection JSON
        json_input = '["https://example.com"]'
        assert self.parser.detect_format(json_input) == "json"
        
        # Test détection CSV
        csv_input = "url,status\nhttps://example.com,active"
        assert self.parser.detect_format(csv_input) == "csv"
        
        # Test détection texte
        text_input = "https://example.com/page1\nhttps://example.com/page2"
        assert self.parser.detect_format(text_input) == "text"
    
    def test_should_get_parsing_statistics(self):
        """Test: doit retourner des statistiques de parsing"""
        input_text = """https://example.com/page1
not-a-url
https://example.com/page2
invalid
https://example.com/page3"""
        
        result = self.parser.detect_and_parse(input_text)
        stats = self.parser.get_last_statistics()
        
        assert stats['total_lines'] == 5
        assert stats['valid_urls'] == 3
        assert stats['invalid_entries'] == 2
        assert stats['format_detected'] == 'text'