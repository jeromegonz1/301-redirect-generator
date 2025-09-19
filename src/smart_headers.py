"""
SmartHeaders - Gestion intelligente des headers HTTP
US-2.2: En tant qu'utilisateur, je veux un scraper qui évite les erreurs 403
"""

import random
import requests
from typing import Dict, Optional, List
from urllib.parse import urlparse
from src.smart_input_config import DEFAULT_HTTP_HEADERS


class SmartHeaders:
    """Gestionnaire intelligent des headers HTTP pour éviter les blocages"""
    
    def __init__(self):
        self.usage_stats = {
            'total_requests': 0,
            'user_agent_distribution': {},
            'success_rate_by_agent': {},
            'blocked_domains': set()
        }
        self._current_agent_index = 0
    
    def get_browser_headers(self) -> Dict[str, str]:
        """
        Retourne des headers de navigateur réalistes avec rotation
        
        Returns:
            Dictionnaire des headers HTTP
        """
        user_agents = self._get_user_agent_list()
        
        # Rotation des User-Agents
        user_agent = user_agents[self._current_agent_index % len(user_agents)]
        self._current_agent_index += 1
        
        headers = DEFAULT_HTTP_HEADERS.copy()
        headers['User-Agent'] = user_agent
        
        self._track_usage(user_agent)
        return headers
    
    def get_headers_for_url(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """
        Génère des headers personnalisés selon l'URL cible
        
        Args:
            url: URL cible
            referer: URL de référence optionnelle
            
        Returns:
            Headers personnalisés pour l'URL
        """
        headers = self.get_browser_headers()
        
        # Ajouter le referer si fourni
        if referer:
            headers['Referer'] = referer
        
        # Personnalisation selon le domaine
        domain = urlparse(url).netloc.lower()
        
        # Headers spéciaux pour Cloudflare
        if self._is_cloudflare_protected(domain):
            headers.update(self._get_cloudflare_headers())
        
        # Headers pour sites WordPress
        elif 'wordpress' in domain or 'wp-' in url:
            headers.update(self._get_wordpress_headers())
        
        return headers
    
    def get_headers_for_content_type(self, content_type: str) -> Dict[str, str]:
        """
        Adapte les headers selon le type de contenu attendu
        
        Args:
            content_type: Type de contenu ('xml', 'json', 'html')
            
        Returns:
            Headers adaptés au type de contenu
        """
        headers = self.get_browser_headers()
        
        if content_type == 'xml':
            headers['Accept'] = 'application/xml,text/xml,*/*;q=0.9'
        elif content_type == 'json':
            headers['Accept'] = 'application/json,text/plain,*/*;q=0.9'
        elif content_type == 'html':
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        
        return headers
    
    def get_mobile_headers(self) -> Dict[str, str]:
        """
        Retourne des headers d'appareil mobile
        
        Returns:
            Headers d'appareil mobile
        """
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        headers = DEFAULT_HTTP_HEADERS.copy()
        headers['User-Agent'] = random.choice(mobile_agents)
        
        return headers
    
    def get_robot_headers(self) -> Dict[str, str]:
        """
        Retourne des headers de robot respectueux
        
        Returns:
            Headers de robot identifié
        """
        headers = {
            'User-Agent': 'Fire-Snake-301-Bot/1.2.0 (+https://fire-snake-301.fr/about)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'From': 'bot@fire-snake-301.fr'
        }
        
        return headers
    
    def get_headers_with_strategy(self, retry_count: int) -> Dict[str, str]:
        """
        Adapte les headers selon la stratégie de retry
        
        Args:
            retry_count: Numéro de tentative (0, 1, 2...)
            
        Returns:
            Headers adaptés à la tentative
        """
        if retry_count == 0:
            # Premier essai : headers normaux
            return self.get_browser_headers()
        elif retry_count == 1:
            # Deuxième essai : mobile
            return self.get_mobile_headers()
        elif retry_count == 2:
            # Troisième essai : robot identifié
            return self.get_robot_headers()
        else:
            # Essais suivants : rotation aléatoire
            return random.choice([
                self.get_browser_headers(),
                self.get_mobile_headers()
            ])
    
    def create_session(self, **kwargs) -> requests.Session:
        """
        Crée une session requests avec headers intelligents
        
        Returns:
            Session configurée
        """
        session = requests.Session()
        session.headers.update(self.get_browser_headers())
        
        # Configuration de base
        session.timeout = kwargs.get('timeout', 10)
        session.max_redirects = kwargs.get('max_redirects', 5)
        
        return session
    
    def is_blocked_response(self, response) -> bool:
        """
        Détecte si une réponse indique un blocage
        
        Args:
            response: Objet response de requests
            
        Returns:
            True si la réponse indique un blocage
        """
        # Status codes de blocage
        blocked_codes = [403, 429, 503, 508]
        if response.status_code in blocked_codes:
            return True
        
        # Patterns de blocage dans le contenu
        blocked_patterns = [
            'access denied',
            'forbidden',
            'blocked',
            'cloudflare',
            'rate limit',
            'too many requests',
            'captcha required'
        ]
        
        content_lower = response.text.lower()
        return any(pattern in content_lower for pattern in blocked_patterns)
    
    def _get_user_agent_list(self) -> List[str]:
        """Retourne la liste des User-Agents disponibles"""
        return [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
    
    def _is_cloudflare_protected(self, domain: str) -> bool:
        """Détecte si un domaine utilise Cloudflare"""
        cloudflare_indicators = [
            'cloudflare',
            'cf-',
            # Ajout d'autres indicateurs si nécessaire
        ]
        return any(indicator in domain for indicator in cloudflare_indicators)
    
    def _get_cloudflare_headers(self) -> Dict[str, str]:
        """Headers spéciaux pour contourner Cloudflare"""
        return {
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def _get_wordpress_headers(self) -> Dict[str, str]:
        """Headers optimisés pour WordPress"""
        return {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache'
        }
    
    def _track_usage(self, user_agent: str):
        """Enregistre l'utilisation des User-Agents"""
        self.usage_stats['total_requests'] += 1
        
        if user_agent in self.usage_stats['user_agent_distribution']:
            self.usage_stats['user_agent_distribution'][user_agent] += 1
        else:
            self.usage_stats['user_agent_distribution'][user_agent] = 1
    
    def get_usage_statistics(self) -> Dict:
        """
        Retourne les statistiques d'utilisation
        
        Returns:
            Statistiques d'utilisation des headers
        """
        return {
            'total_requests': self.usage_stats['total_requests'],
            'user_agent_distribution': self.usage_stats['user_agent_distribution'].copy(),
            'success_rate_by_agent': self.usage_stats['success_rate_by_agent'].copy(),
            'unique_agents_used': len(self.usage_stats['user_agent_distribution']),
            'blocked_domains_count': len(self.usage_stats['blocked_domains'])
        }