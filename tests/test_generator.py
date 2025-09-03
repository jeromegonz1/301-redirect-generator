"""
Tests pour le générateur de redirections 301
Approche TDD selon les user stories
"""

import pytest
from src.generator import RedirectGenerator


class TestRedirectGenerator:
    """Tests pour la classe RedirectGenerator"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.generator = RedirectGenerator()
    
    def test_parse_raw_urls(self):
        """US001: Test parsing d'une liste brute d'URLs"""
        raw_input = """https://ancien-site.com/page1
https://ancien-site.com/page2
https://ancien-site.com/contact"""
        
        result = self.generator.parse_input(raw_input)
        
        assert len(result) == 3
        assert result[0] == "https://ancien-site.com/page1"
        assert result[1] == "https://ancien-site.com/page2"
        assert result[2] == "https://ancien-site.com/contact"
    
    def test_parse_xml_sitemap(self):
        """US001: Test parsing d'une sitemap XML"""
        xml_input = """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://ancien-site.com/page1</loc>
  </url>
  <url>
    <loc>https://ancien-site.com/page2</loc>
  </url>
</urlset>"""
        
        result = self.generator.parse_input(xml_input)
        
        assert len(result) == 2
        assert result[0] == "https://ancien-site.com/page1"
        assert result[1] == "https://ancien-site.com/page2"
    
    def test_parse_csv_format(self):
        """US001: Test parsing d'un format CSV"""
        csv_input = """https://ancien-site.com/page1,https://nouveau-site.com/page1
https://ancien-site.com/page2,https://nouveau-site.com/page2"""
        
        result = self.generator.parse_input(csv_input)
        
        assert len(result) == 2
        assert result[0] == "https://ancien-site.com/page1"
        assert result[1] == "https://ancien-site.com/page2"
    
    def test_normalize_url(self):
        """Test de normalisation des URLs"""
        # Test avec trailing slash
        assert self.generator.normalize_url("https://site.com/page/") == "https://site.com/page"
        
        # Test sans protocole
        assert self.generator.normalize_url("site.com/page") == "http://site.com/page"
        
        # Test racine
        assert self.generator.normalize_url("https://site.com/") == "https://site.com/"
    
    def test_generate_htaccess_format(self):
        """US002: Test génération du format .htaccess correct"""
        old_input = "https://ancien-site.com/contact"
        new_input = "https://nouveau-site.com/nous-contacter"
        
        htaccess_content, csv_data = self.generator.generate_redirections(old_input, new_input)
        
        # Vérifie le format .htaccess
        expected_line = "Redirect 301 https://ancien-site.com/contact /nous-contacter\n"
        assert htaccess_content == expected_line
    
    def test_generate_csv_format(self):
        """US003: Test génération du format CSV d'audit"""
        old_input = "https://ancien-site.com/contact"
        new_input = "https://nouveau-site.com/nous-contacter"
        
        htaccess_content, csv_data = self.generator.generate_redirections(old_input, new_input)
        
        # Vérifie la structure CSV
        assert len(csv_data) == 2  # Header + 1 ligne
        assert csv_data[0] == ["OLD_FULL_URL", "OLD_PATH", "NEW_FULL_URL", "NEW_PATH"]
        assert csv_data[1] == [
            "https://ancien-site.com/contact",
            "/contact",
            "https://nouveau-site.com/nous-contacter", 
            "/nous-contacter"
        ]
    
    def test_mismatch_error(self):
        """US002: Test gestion d'erreur en cas de mismatch"""
        old_input = """https://ancien-site.com/page1
https://ancien-site.com/page2"""
        new_input = "https://nouveau-site.com/page1"
        
        with pytest.raises(ValueError, match="Mismatch"):
            self.generator.generate_redirections(old_input, new_input)
    
    def test_multiple_redirections(self):
        """Test génération de plusieurs redirections"""
        old_input = """https://ancien-site.com/page1
https://ancien-site.com/page2"""
        new_input = """https://nouveau-site.com/nouvelle-page1
https://nouveau-site.com/nouvelle-page2"""
        
        htaccess_content, csv_data = self.generator.generate_redirections(old_input, new_input)
        
        # Vérifie qu'on a bien 2 redirections
        lines = htaccess_content.strip().split('\n')
        assert len(lines) == 2
        assert "Redirect 301 https://ancien-site.com/page1 /nouvelle-page1" in lines[0]
        assert "Redirect 301 https://ancien-site.com/page2 /nouvelle-page2" in lines[1]
        
        # Vérifie le CSV (header + 2 lignes)
        assert len(csv_data) == 3
    
    def test_empty_input(self):
        """Test avec input vide"""
        result = self.generator.parse_input("")
        assert result == []
        
        result = self.generator.parse_input("   ")
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__])