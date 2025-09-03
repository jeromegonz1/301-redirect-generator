"""
Tests pour le module de scraping
Approche TDD selon SCRAPER_SPEC.md
"""

import pytest
from unittest.mock import Mock, patch
from src.scraper import WebScraper, crawl_site, crawl_site_with_fallback


class TestWebScraper:
    """Tests pour la classe WebScraper"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.scraper = WebScraper()
    
    def test_normalize_url_removes_query_string(self):
        """Test suppression des query strings"""
        url = "https://example.com/page?param=value&other=test"
        result = self.scraper.normalize_url(url)
        assert result == "https://example.com/page"
    
    def test_normalize_url_removes_fragment(self):
        """Test suppression des fragments (#)"""
        url = "https://example.com/page#section"
        result = self.scraper.normalize_url(url)
        assert result == "https://example.com/page"
    
    def test_normalize_url_removes_trailing_slash(self):
        """Test suppression du trailing slash (sauf racine)"""
        url = "https://example.com/page/"
        result = self.scraper.normalize_url(url)
        assert result == "https://example.com/page"
        
        # La racine garde son slash
        url = "https://example.com/"
        result = self.scraper.normalize_url(url)
        assert result == "https://example.com/"
    
    def test_is_same_domain_true(self):
        """Test détection même domaine"""
        url1 = "https://example.com/page1"
        url2 = "https://example.com/page2"
        assert self.scraper.is_same_domain(url1, url2) == True
    
    def test_is_same_domain_false(self):
        """Test détection domaines différents"""
        url1 = "https://example.com/page1"
        url2 = "https://other-site.com/page2"
        assert self.scraper.is_same_domain(url1, url2) == False
    
    def test_extract_links_from_html_basic(self):
        """Test extraction de liens basique"""
        html = '''
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="https://external.com/page">External</a>
            </body>
        </html>
        '''
        base_url = "https://example.com"
        
        links = self.scraper.extract_links_from_html(html, base_url)
        
        # Doit contenir les liens internes seulement
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://external.com/page" not in links
    
    def test_extract_links_ignores_fragments(self):
        """Test que les fragments sont ignorés"""
        html = '''
        <html>
            <body>
                <a href="#section">Fragment only</a>
                <a href="/page#section">Page with fragment</a>
                <a href="">Empty href</a>
            </body>
        </html>
        '''
        base_url = "https://example.com"
        
        links = self.scraper.extract_links_from_html(html, base_url)
        
        # Ne doit contenir que le lien sans fragment
        assert len(links) == 1
        assert "https://example.com/page" in links
    
    @patch('src.scraper.requests.Session.get')
    def test_crawl_site_respects_max_pages(self, mock_get):
        """Test que le crawler respecte la limite de pages"""
        # Mock de la réponse HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html><body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body></html>
        '''
        mock_get.return_value = mock_response
        
        # Limite à 2 pages maximum
        urls = self.scraper.crawl_site("https://example.com", max_pages=2)
        
        # Ne doit pas dépasser la limite
        assert len(urls) <= 2
        assert "https://example.com" in urls
    
    @patch('src.scraper.requests.Session.get')
    def test_crawl_site_handles_http_errors(self, mock_get):
        """Test gestion des erreurs HTTP"""
        # Mock d'une erreur 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        urls = self.scraper.crawl_site("https://example.com")
        
        # Doit retourner une liste vide sans crash
        assert urls == []
    
    @patch('src.scraper.requests.Session.get')
    def test_crawl_site_with_auth(self, mock_get):
        """Test crawler avec authentification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><a href="/page">Page</a></body></html>'
        mock_get.return_value = mock_response
        
        auth = ("user", "password")
        urls = self.scraper.crawl_site("https://example.com", auth=auth)
        
        # Vérifie que l'auth a été configurée
        assert self.scraper.session.auth == auth
        assert len(urls) >= 1
    
    def test_crawl_site_relative(self):
        """Test génération d'URLs relatives"""
        with patch.object(self.scraper, 'crawl_site') as mock_crawl:
            mock_crawl.return_value = [
                "https://example.com",
                "https://example.com/page1",
                "https://example.com/section/page2"
            ]
            
            relative_urls = self.scraper.crawl_site_relative("https://example.com")
            
            expected = ["/", "/page1", "/section/page2"]
            assert relative_urls == expected


class TestHelperFunctions:
    """Tests pour les fonctions helper"""
    
    @patch('src.scraper.WebScraper.crawl_site')
    def test_crawl_site_function(self, mock_crawl):
        """Test de la fonction helper crawl_site"""
        mock_crawl.return_value = ["https://example.com/page1"]
        
        result = crawl_site("https://example.com", max_pages=100)
        
        assert result == ["https://example.com/page1"]
        mock_crawl.assert_called_once()
    
    @patch('src.scraper.WebScraper.crawl_site')
    def test_crawl_site_with_fallback_success(self, mock_crawl):
        """Test fallback en cas de succès"""
        mock_crawl.return_value = ["https://example.com"]
        
        urls, success = crawl_site_with_fallback("https://example.com")
        
        assert success == True
        assert urls == ["https://example.com"]
    
    @patch('src.scraper.WebScraper.crawl_site')
    def test_crawl_site_with_fallback_failure(self, mock_crawl):
        """Test fallback en cas d'échec"""
        mock_crawl.return_value = []  # Aucune URL trouvée
        
        urls, success = crawl_site_with_fallback("https://example.com")
        
        assert success == False
        assert urls == []
    
    @patch('src.scraper.WebScraper.crawl_site')
    def test_crawl_site_with_fallback_exception(self, mock_crawl):
        """Test fallback en cas d'exception"""
        mock_crawl.side_effect = Exception("Network error")
        
        urls, success = crawl_site_with_fallback("https://example.com")
        
        assert success == False
        assert urls == []


if __name__ == "__main__":
    pytest.main([__file__])