"""
Parser pour la saisie manuelle d'URLs dans Fire Snake 301
Permet de contourner les sitemaps bloqués par Cloudflare
"""

from typing import List
from urllib.parse import urlparse
import re


class ManualInputParser:
    """Parse et valide les URLs saisies manuellement"""
    
    def __init__(self):
        """Initialise le parser"""
        self.last_errors = []
        self.last_statistics = {}
    
    def parse_urls(self, input_text: str, separator: str = '\n', 
                   deduplicate: bool = True) -> List[str]:
        """
        Parse le texte d'entrée et extrait les URLs valides
        
        Args:
            input_text: Texte contenant les URLs
            separator: Séparateur entre URLs ('\n' ou ',')
            deduplicate: Si True, supprime les doublons
            
        Returns:
            Liste d'URLs valides
        """
        if not input_text:
            self.last_errors = []
            self.last_statistics = {'total_lines': 0, 'valid_urls': 0, 'invalid_urls': 0, 'empty_lines': 0}
            return []
        
        # Séparer les URLs selon le séparateur
        if separator == ',':
            lines = [line.strip() for line in input_text.split(',')]
        else:
            lines = input_text.strip().split('\n')
        
        valid_urls = []
        errors = []
        empty_lines = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ignorer les lignes vides
            if not line:
                empty_lines += 1
                continue
            
            # Valider l'URL
            if self._is_valid_url(line):
                valid_urls.append(line)
            else:
                errors.append(f"Ligne {line_num}: '{line}' n'est pas une URL valide")
        
        # Dédupliquer si demandé
        if deduplicate:
            # Préserver l'ordre avec dict.fromkeys()
            valid_urls = list(dict.fromkeys(valid_urls))
        
        # Stocker les résultats pour récupération
        self.last_errors = errors
        self.last_statistics = {
            'total_lines': len(lines),
            'valid_urls': len(valid_urls),
            'invalid_urls': len(errors),
            'empty_lines': empty_lines
        }
        
        return valid_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Valide si une chaîne est une URL correcte
        
        Args:
            url: URL à valider
            
        Returns:
            True si l'URL est valide
        """
        try:
            result = urlparse(url)
            # Une URL valide doit avoir un scheme et un netloc
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_last_errors(self) -> List[str]:
        """
        Retourne les erreurs du dernier parsing
        
        Returns:
            Liste des messages d'erreur
        """
        return self.last_errors.copy()
    
    def get_last_statistics(self) -> dict:
        """
        Retourne les statistiques du dernier parsing
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return self.last_statistics.copy()
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extrait automatiquement les URLs d'un texte libre
        Utile pour parser du contenu copié-collé
        
        Args:
            text: Texte libre contenant potentiellement des URLs
            
        Returns:
            Liste d'URLs trouvées
        """
        # Pattern regex pour trouver les URLs
        url_pattern = r'https?://[^\s<>"\'()[\]{}|\\^`]+'
        
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Valider chaque URL trouvée
        valid_urls = [url for url in urls if self._is_valid_url(url)]
        
        return valid_urls
    
    def validate_url_accessibility(self, url: str, timeout: int = 5) -> bool:
        """
        Teste si une URL est accessible (optionnel)
        
        Args:
            url: URL à tester
            timeout: Timeout en secondes
            
        Returns:
            True si l'URL est accessible
        """
        try:
            import requests
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False