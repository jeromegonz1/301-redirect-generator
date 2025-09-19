"""
Contournement Cloudflare pour Fire Snake 301
Techniques pour bypasser les protections anti-bot
"""

import requests
import time
import random
from typing import Dict, List, Optional
from urllib.parse import urlparse


class CloudflareBypass:
    """Contourne les protections Cloudflare avec différentes stratégies"""
    
    def __init__(self, max_retries: int = 3, delay_between_requests: float = 2.0):
        """
        Initialise le bypass Cloudflare
        
        Args:
            max_retries: Nombre maximum de tentatives
            delay_between_requests: Délai entre les requêtes (en secondes)
        """
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.session = requests.Session()
        
        # Indicateurs de détection Cloudflare
        self.cloudflare_indicators = [
            'Attention Required! | Cloudflare',
            'Sorry, you have been blocked',
            'Ray ID:',
            'cloudflare',
            'cf-error-details',
            'Please enable cookies',
            'Checking your browser'
        ]
    
    def is_cloudflare_blocked(self, response_text: str) -> bool:
        """
        Détecte si la réponse indique un blocage Cloudflare
        
        Args:
            response_text: Contenu HTML de la réponse
            
        Returns:
            True si c'est un blocage Cloudflare
        """
        if not response_text:
            return False
            
        response_lower = response_text.lower()
        return any(indicator.lower() in response_lower for indicator in self.cloudflare_indicators)
    
    def get_realistic_headers(self, browser_type: str = 'chrome') -> Dict[str, str]:
        """
        Génère des headers HTTP réalistes pour simuler un navigateur
        
        Args:
            browser_type: Type de navigateur à simuler
            
        Returns:
            Dictionnaire des headers
        """
        user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76'
        }
        
        return {
            'User-Agent': user_agents.get(browser_type, user_agents['chrome']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    def get_bypass_strategies(self) -> List[Dict[str, str]]:
        """
        Retourne différentes stratégies de contournement
        
        Returns:
            Liste des stratégies (headers)
        """
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        return [self.get_realistic_headers(browser) for browser in browsers]
    
    def get_random_delay(self) -> float:
        """
        Génère un délai aléatoire pour éviter la détection
        
        Returns:
            Délai en secondes
        """
        base_delay = self.delay_between_requests
        # Ajouter une variation aléatoire de ±50%
        variation = base_delay * 0.5
        return base_delay + random.uniform(-variation, variation)
    
    def fetch_with_bypass(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """
        Tente de récupérer une URL en contournant Cloudflare
        
        Args:
            url: URL à récupérer
            timeout: Timeout en secondes
            
        Returns:
            Réponse HTTP ou None si échec
        """
        strategies = self.get_bypass_strategies()
        
        for attempt in range(self.max_retries):
            # Utiliser une stratégie différente à chaque tentative
            strategy = strategies[attempt % len(strategies)]
            
            try:
                # Attendre avant la requête (sauf première tentative)
                if attempt > 0:
                    delay = self.get_random_delay()
                    time.sleep(delay)
                
                # Faire la requête avec la stratégie actuelle
                response = self.session.get(
                    url, 
                    headers=strategy,
                    timeout=timeout,
                    allow_redirects=True
                )
                
                # Vérifier si c'est un blocage Cloudflare
                if response.status_code == 403 or self.is_cloudflare_blocked(response.text):
                    if attempt < self.max_retries - 1:
                        continue  # Essayer la stratégie suivante
                    else:
                        return None  # Toutes les stratégies ont échoué
                
                # Succès !
                return response
                
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    continue  # Réessayer
                return None
            
            except Exception as e:
                # Autres erreurs
                return None
        
        return None
    
    def enhance_scraper_session(self, session: requests.Session) -> requests.Session:
        """
        Améliore une session requests existante avec les techniques de bypass
        
        Args:
            session: Session requests à améliorer
            
        Returns:
            Session améliorée
        """
        # Appliquer les headers les plus efficaces
        session.headers.update(self.get_realistic_headers('chrome'))
        
        # Configurer les timeouts
        session.timeout = 30
        
        # Désactiver la vérification SSL si nécessaire (pour les tests)
        # session.verify = False  # À utiliser avec précaution
        
        return session