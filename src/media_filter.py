"""
Filtrage des fichiers médias pour Fire Snake 301
Exclut automatiquement les images et assets des redirections
"""

from typing import List
from urllib.parse import urlparse
import os


class MediaFilter:
    """Filtre les URLs de fichiers médias et assets"""
    
    # Extensions à filtrer (pas de hardcoding, configurables)
    MEDIA_EXTENSIONS = {
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff',
        # Assets web
        '.css', '.js', '.min.js', '.min.css',
        # Documents 
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        # Autres formats
        '.xml', '.rss', '.json', '.txt', '.zip', '.rar',
        # Vidéos/Audio
        '.mp4', '.avi', '.mov', '.mp3', '.wav', '.ogg'
    }
    
    def __init__(self, custom_extensions: List[str] = None):
        """
        Initialise le filtre
        
        Args:
            custom_extensions: Extensions supplémentaires à filtrer
        """
        self.extensions = self.MEDIA_EXTENSIONS.copy()
        if custom_extensions:
            self.extensions.update(ext.lower() for ext in custom_extensions)
    
    def is_media_file(self, url: str) -> bool:
        """
        Vérifie si une URL pointe vers un fichier média
        
        Args:
            url: URL à vérifier
            
        Returns:
            True si c'est un fichier média, False sinon
        """
        if not url:
            return False
            
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Extraire l'extension
            _, ext = os.path.splitext(path)
            
            return ext in self.extensions
            
        except Exception:
            # En cas d'erreur de parsing, on considère que ce n'est pas un média
            return False
    
    def filter_urls(self, urls: List[str]) -> List[str]:
        """
        Filtre une liste d'URLs en excluant les fichiers médias
        
        Args:
            urls: Liste d'URLs à filtrer
            
        Returns:
            Liste d'URLs sans les fichiers médias
        """
        return [url for url in urls if not self.is_media_file(url)]
    
    def get_filtered_statistics(self, urls: List[str]) -> dict:
        """
        Retourne des statistiques sur le filtrage
        
        Args:
            urls: Liste d'URLs originale
            
        Returns:
            Dictionnaire avec les statistiques
        """
        total = len(urls)
        filtered_urls = self.filter_urls(urls)
        kept = len(filtered_urls)
        removed = total - kept
        
        return {
            'total': total,
            'kept': kept,
            'removed': removed,
            'removal_percentage': round((removed / total * 100) if total > 0 else 0, 1)
        }