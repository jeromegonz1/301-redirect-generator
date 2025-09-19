"""
Nettoyage des URLs pour Fire Snake 301
Supprime les artefacts de préproduction et normalise les URLs
"""

from typing import List
from urllib.parse import urlparse, urlunparse
import re


class URLCleaner:
    """Nettoie les URLs en supprimant les patterns indésirables"""
    
    # Patterns par défaut à supprimer (configurables, pas de hardcoding)
    DEFAULT_PATTERNS = [
        '/les-cascades/',  # Artefact de préproduction spécifique
        '/les-cascades'    # Version sans slash final
    ]
    
    def __init__(self, patterns_to_remove: List[str] = None):
        """
        Initialise le nettoyeur d'URLs
        
        Args:
            patterns_to_remove: Patterns personnalisés à supprimer
        """
        if patterns_to_remove is None:
            self.patterns = self.DEFAULT_PATTERNS.copy()
        else:
            self.patterns = patterns_to_remove.copy()
    
    def clean_url(self, url: str) -> str:
        """
        Nettoie une URL en supprimant les patterns indésirables
        
        Args:
            url: URL à nettoyer
            
        Returns:
            URL nettoyée
        """
        if not url:
            return url
            
        try:
            # Parser l'URL pour gérer correctement les composants
            parsed = urlparse(url)
            path = parsed.path
            
            # Appliquer tous les patterns de nettoyage
            for pattern in self.patterns:
                path = path.replace(pattern, '/')
            
            # Normaliser les slashes multiples
            path = re.sub(r'/+', '/', path)
            
            # Si le path devient juste '/', le laisser tel quel
            # Sinon supprimer le slash final s'il n'y en avait pas au départ
            if path != '/' and path.endswith('/') and not parsed.path.endswith('/'):
                path = path.rstrip('/')
            
            # Reconstruire l'URL avec le path nettoyé
            cleaned = urlunparse((
                parsed.scheme,
                parsed.netloc,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return cleaned
            
        except Exception:
            # En cas d'erreur de parsing, retourner l'URL originale
            return url
    
    def clean_urls(self, urls: List[str]) -> List[str]:
        """
        Nettoie une liste d'URLs
        
        Args:
            urls: Liste d'URLs à nettoyer
            
        Returns:
            Liste d'URLs nettoyées
        """
        return [self.clean_url(url) for url in urls]
    
    def get_cleaning_statistics(self, urls: List[str]) -> dict:
        """
        Retourne des statistiques sur le nettoyage
        
        Args:
            urls: Liste d'URLs originale
            
        Returns:
            Dictionnaire avec les statistiques
        """
        cleaned_urls = self.clean_urls(urls)
        
        # Compter les URLs modifiées
        modified = sum(1 for original, cleaned in zip(urls, cleaned_urls) 
                      if original != cleaned)
        
        total = len(urls)
        
        return {
            'total': total,
            'modified': modified,
            'unchanged': total - modified,
            'modification_percentage': round((modified / total * 100) if total > 0 else 0, 1)
        }
    
    def add_pattern(self, pattern: str):
        """Ajoute un pattern de nettoyage"""
        if pattern not in self.patterns:
            self.patterns.append(pattern)
    
    def remove_pattern(self, pattern: str):
        """Supprime un pattern de nettoyage"""
        if pattern in self.patterns:
            self.patterns.remove(pattern)