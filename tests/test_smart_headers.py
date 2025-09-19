"""
Tests pour les headers HTTP intelligents
US-2.2: En tant qu'utilisateur, je veux un scraper qui évite les erreurs 403
"""

import pytest
import requests
from unittest.mock import Mock, patch
from src.smart_headers import SmartHeaders


class TestSmartHeaders:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.headers_manager = SmartHeaders()
    
    def test_should_provide_realistic_browser_headers(self):
        """Test: doit fournir des headers de navigateur réalistes"""
        headers = self.headers_manager.get_browser_headers()
        
        # Vérifier la présence des headers essentiels
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert 'Accept-Encoding' in headers
        assert 'Connection' in headers
        
        # Vérifier que le User-Agent ressemble à un navigateur
        user_agent = headers['User-Agent']
        assert 'Mozilla' in user_agent
        assert any(browser in user_agent for browser in ['Chrome', 'Firefox', 'Safari'])
    
    def test_should_rotate_user_agents(self):
        """Test: doit faire tourner les User-Agents"""
        headers1 = self.headers_manager.get_browser_headers()
        headers2 = self.headers_manager.get_browser_headers()
        headers3 = self.headers_manager.get_browser_headers()
        
        # Collecter les User-Agents
        user_agents = [
            headers1['User-Agent'],
            headers2['User-Agent'], 
            headers3['User-Agent']
        ]
        
        # Doit y avoir au moins 2 User-Agents différents
        unique_agents = set(user_agents)
        assert len(unique_agents) >= 2
    
    def test_should_add_referer_when_provided(self):
        """Test: doit ajouter un Referer quand fourni"""
        url = "https://example.com/page"
        referer = "https://example.com/"
        
        headers = self.headers_manager.get_headers_for_url(url, referer=referer)
        
        assert headers['Referer'] == referer
    
    def test_should_customize_headers_for_domain(self):
        """Test: doit personnaliser les headers selon le domaine"""
        # Test pour un domaine connu problématique
        cloudflare_url = "https://site-with-cloudflare.com/page"
        headers = self.headers_manager.get_headers_for_url(cloudflare_url)
        
        # Doit avoir des headers spéciaux pour Cloudflare
        assert 'Sec-Fetch-Dest' in headers
        assert 'Sec-Fetch-Mode' in headers
        assert 'Sec-Fetch-Site' in headers
    
    def test_should_handle_different_content_types(self):
        """Test: doit adapter les headers selon le type de contenu"""
        # Headers pour XML/sitemap
        xml_headers = self.headers_manager.get_headers_for_content_type('xml')
        assert 'application/xml' in xml_headers['Accept']
        
        # Headers pour JSON
        json_headers = self.headers_manager.get_headers_for_content_type('json')
        assert 'application/json' in json_headers['Accept']
        
        # Headers pour HTML
        html_headers = self.headers_manager.get_headers_for_content_type('html')
        assert 'text/html' in html_headers['Accept']
    
    def test_should_create_session_with_headers(self):
        """Test: doit créer une session avec les bons headers"""
        session = self.headers_manager.create_session()
        
        assert isinstance(session, requests.Session)
        assert 'User-Agent' in session.headers
        assert 'Accept' in session.headers
    
    def test_should_handle_mobile_user_agent(self):
        """Test: doit pouvoir utiliser des User-Agents mobiles"""
        mobile_headers = self.headers_manager.get_mobile_headers()
        
        user_agent = mobile_headers['User-Agent']
        assert any(mobile in user_agent for mobile in ['Mobile', 'Android', 'iPhone'])
    
    def test_should_respect_robots_txt_header(self):
        """Test: doit inclure des headers respectueux pour robots.txt"""
        robot_headers = self.headers_manager.get_robot_headers()
        
        # Doit identifier clairement le bot
        user_agent = robot_headers['User-Agent']
        assert 'bot' in user_agent.lower() or 'crawler' in user_agent.lower()
    
    def test_should_get_headers_with_retry_strategy(self):
        """Test: doit adapter les headers selon la stratégie de retry"""
        # Premier essai - headers normaux
        headers1 = self.headers_manager.get_headers_with_strategy(retry_count=0)
        
        # Deuxième essai - headers différents
        headers2 = self.headers_manager.get_headers_with_strategy(retry_count=1)
        
        # Troisième essai - headers encore différents
        headers3 = self.headers_manager.get_headers_with_strategy(retry_count=2)
        
        # Les User-Agents doivent être différents
        agents = [headers1['User-Agent'], headers2['User-Agent'], headers3['User-Agent']]
        assert len(set(agents)) >= 2
    
    def test_should_detect_blocking_response(self):
        """Test: doit détecter quand une réponse indique un blocage"""
        # Mock response 403
        mock_403 = Mock()
        mock_403.status_code = 403
        mock_403.text = "Access Denied"
        
        assert self.headers_manager.is_blocked_response(mock_403) == True
        
        # Mock response 429
        mock_429 = Mock()
        mock_429.status_code = 429
        mock_429.text = "Rate Limited"
        
        assert self.headers_manager.is_blocked_response(mock_429) == True
        
        # Mock response Cloudflare
        mock_cf = Mock()
        mock_cf.status_code = 503
        mock_cf.text = "Sorry, you have been blocked by Cloudflare"
        
        assert self.headers_manager.is_blocked_response(mock_cf) == True
        
        # Mock response normale
        mock_ok = Mock()
        mock_ok.status_code = 200
        mock_ok.text = "Normal page content"
        
        assert self.headers_manager.is_blocked_response(mock_ok) == False
    
    def test_should_get_statistics(self):
        """Test: doit fournir des statistiques d'utilisation"""
        # Utiliser plusieurs types de headers
        self.headers_manager.get_browser_headers()
        self.headers_manager.get_mobile_headers()
        self.headers_manager.get_robot_headers()
        
        stats = self.headers_manager.get_usage_statistics()
        
        assert 'total_requests' in stats
        assert 'user_agent_distribution' in stats
        assert 'success_rate_by_agent' in stats
    
    def test_should_validate_headers_format(self):
        """Test: doit valider le format des headers générés"""
        headers = self.headers_manager.get_browser_headers()
        
        # Tous les headers doivent être des strings
        for key, value in headers.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) > 0
            assert len(value) > 0
        
        # Vérifier des formats spécifiques
        assert headers['Accept-Language'].count(',') >= 1  # Doit avoir plusieurs langues
        assert 'gzip' in headers['Accept-Encoding']  # Doit supporter la compression