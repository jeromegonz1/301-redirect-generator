"""
Tests pour le contournement Cloudflare
US-4: En tant qu'utilisateur, je veux contourner automatiquement Cloudflare
"""

import pytest
from unittest.mock import Mock, patch
from src.cloudflare_bypass import CloudflareBypass


class TestCloudflareBypass:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.bypass = CloudflareBypass()
    
    def test_should_detect_cloudflare_response(self):
        """Test: doit détecter une réponse Cloudflare"""
        cloudflare_html = '''
        <!DOCTYPE html>
        <html>
        <head>
        <title>Attention Required! | Cloudflare</title>
        </head>
        <body>
        <h1>Sorry, you have been blocked</h1>
        </body>
        </html>
        '''
        
        assert self.bypass.is_cloudflare_blocked(cloudflare_html) == True
    
    def test_should_not_detect_normal_response(self):
        """Test: ne doit pas détecter Cloudflare sur une réponse normale"""
        normal_html = '''
        <!DOCTYPE html>
        <html>
        <head><title>Normal Site</title></head>
        <body><h1>Welcome</h1></body>
        </html>
        '''
        
        assert self.bypass.is_cloudflare_blocked(normal_html) == False
    
    def test_should_generate_realistic_headers(self):
        """Test: doit générer des headers réalistes"""
        headers = self.bypass.get_realistic_headers()
        
        # Vérifier la présence des headers essentiels
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert 'Accept-Encoding' in headers
        assert 'Connection' in headers
        
        # Vérifier que le User-Agent ressemble à un navigateur réel
        user_agent = headers['User-Agent']
        assert 'Mozilla' in user_agent
        assert any(browser in user_agent for browser in ['Chrome', 'Firefox', 'Safari'])
    
    def test_should_try_multiple_strategies(self):
        """Test: doit essayer plusieurs stratégies"""
        strategies = self.bypass.get_bypass_strategies()
        
        assert len(strategies) >= 3
        assert any('Chrome' in strategy['User-Agent'] for strategy in strategies)
        assert any('Firefox' in strategy['User-Agent'] for strategy in strategies)
    
    @patch('requests.Session.get')
    def test_should_retry_with_different_strategies(self, mock_get):
        """Test: doit retenter avec différentes stratégies"""
        # Simuler une première réponse bloquée
        blocked_response = Mock()
        blocked_response.status_code = 403
        blocked_response.text = '<title>Attention Required! | Cloudflare</title>'
        
        # Puis une réponse réussie
        success_response = Mock()
        success_response.status_code = 200
        success_response.text = '<url>https://example.com/page1</url>'
        
        mock_get.side_effect = [blocked_response, success_response]
        
        result = self.bypass.fetch_with_bypass('https://example.com/sitemap.xml')
        
        # Doit avoir fait 2 tentatives
        assert mock_get.call_count == 2
        assert result.status_code == 200
    
    def test_should_handle_timeout_gracefully(self):
        """Test: doit gérer les timeouts gracieusement"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = TimeoutError("Connection timeout")
            
            result = self.bypass.fetch_with_bypass('https://example.com/sitemap.xml')
            assert result is None
    
    def test_should_respect_rate_limiting(self):
        """Test: doit respecter le rate limiting"""
        # Vérifier que le délai entre requêtes est configuré
        assert self.bypass.delay_between_requests >= 1
        assert self.bypass.delay_between_requests <= 5
    
    def test_should_randomize_request_timing(self):
        """Test: doit randomiser le timing des requêtes"""
        delays = [self.bypass.get_random_delay() for _ in range(10)]
        
        # Les délais doivent être différents
        assert len(set(delays)) > 5  # Au moins 5 délais différents sur 10
        
        # Tous dans la plage attendue
        assert all(0.5 <= delay <= 3.0 for delay in delays)