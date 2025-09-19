"""
Tests pour le filtrage des fichiers médias
US-1: En tant qu'utilisateur, je veux que les images et fichiers médias soient exclus
"""

import pytest
from src.media_filter import MediaFilter


class TestMediaFilter:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.filter = MediaFilter()
    
    def test_should_filter_common_image_extensions(self):
        """Test: doit filtrer les extensions d'images communes"""
        media_urls = [
            "https://example.com/photo.jpg",
            "https://example.com/image.jpeg", 
            "https://example.com/logo.png",
            "https://example.com/icon.gif",
            "https://example.com/vector.svg",
            "https://example.com/photo.webp",
            "https://example.com/favicon.ico"
        ]
        
        for url in media_urls:
            assert self.filter.is_media_file(url) == True, f"{url} should be filtered"
    
    def test_should_not_filter_html_pages(self):
        """Test: ne doit pas filtrer les pages HTML"""
        html_urls = [
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/contact.html", 
            "https://example.com/page.php",
            "https://example.com/article.aspx"
        ]
        
        for url in html_urls:
            assert self.filter.is_media_file(url) == False, f"{url} should NOT be filtered"
    
    def test_should_filter_other_asset_types(self):
        """Test: doit filtrer les autres types d'assets"""
        asset_urls = [
            "https://example.com/style.css",
            "https://example.com/script.js",
            "https://example.com/document.pdf",
            "https://example.com/data.xml",
            "https://example.com/feed.rss"
        ]
        
        for url in asset_urls:
            assert self.filter.is_media_file(url) == True, f"{url} should be filtered"
    
    def test_filter_urls_list(self):
        """Test: filtrage d'une liste d'URLs mixte"""
        mixed_urls = [
            "https://example.com/",
            "https://example.com/photo.jpg",
            "https://example.com/about", 
            "https://example.com/logo.png",
            "https://example.com/contact",
            "https://example.com/style.css"
        ]
        
        expected_filtered = [
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/contact"
        ]
        
        result = self.filter.filter_urls(mixed_urls)
        assert result == expected_filtered
    
    def test_case_insensitive_filtering(self):
        """Test: filtrage insensible à la casse"""
        urls_mixed_case = [
            "https://example.com/PHOTO.JPG",
            "https://example.com/Image.PNG", 
            "https://example.com/style.CSS"
        ]
        
        for url in urls_mixed_case:
            assert self.filter.is_media_file(url) == True