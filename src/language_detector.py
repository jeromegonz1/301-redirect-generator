"""
Détecteur de langues pour URLs multilingues (US011)
Aucun hardcoding - Tous les patterns configurables
"""

import re
from typing import Dict, List, Set
from collections import defaultdict


class LanguageDetector:
    """Détecteur automatique de langues dans les URLs"""
    
    def __init__(self, default_language: str = "fr"):
        """
        Initialise le détecteur avec une langue par défaut
        
        Args:
            default_language: Langue utilisée quand aucun pattern ne correspond
        """
        self.default_language = default_language
        self.patterns = self._build_language_patterns()
    
    def _build_language_patterns(self) -> Dict[str, List[str]]:
        """Construit les patterns de détection par langue (configurable)"""
        return {
            'fr': [
                r'/fr/',            # anywhere: /path/fr/contact
                r'/(fr)$',          # /contact/fr
                r'-fr[./]',         # /contact-fr.html
                r'\.fr/',           # domain.fr/page
                r'fr\..*\.com'      # fr.site.com
            ],
            'en': [
                r'/en/',            # anywhere: /path/en/contact  
                r'/(en)$',          # /contact/en
                r'-en[./]',         # /contact-en.html
                r'\.co\.uk/',       # domain.co.uk/page
                r'en\..*\.com'      # en.site.com
            ],
            'de': [
                r'/de/',            # anywhere: /path/de/kontakt
                r'/(de)$',          # /kontakt/de
                r'-de[./]',         # /kontakt-de.html
                r'-de$',            # /kontakt-de
                r'\.de/',           # domain.de/page
                r'www\..*\.de/',    # www.site.de/page
                r'de\..*\.com'      # de.site.com
            ],
            'es': [
                r'/es/',            # anywhere: /path/es/contacto
                r'/(es)$',          # /contacto/es
                r'-es[./]',         # /contacto-es.html
                r'\.es/',           # domain.es/page
                r'es\..*\.com'      # es.site.com
            ],
            'it': [
                r'/it/',            # anywhere: /path/it/contatto
                r'/(it)$',          # /contatto/it
                r'-it[./]',         # /contatto-it.html
                r'\.it/',           # domain.it/page
                r'it\..*\.com'      # it.site.com
            ],
            'nl': [
                r'/nl/',            # anywhere: /path/nl/contact
                r'/(nl)$',          # /contact/nl
                r'-nl[./]',         # /contact-nl.html
                r'\.nl/',           # domain.nl/page
                r'nl\..*\.com'      # nl.site.com
            ]
        }
    
    def detect(self, url: str) -> str:
        """
        Détecte la langue d'une URL
        
        Args:
            url: URL à analyser
            
        Returns:
            Code langue détecté (ex: 'fr', 'en', 'de')
        """
        if not url or not isinstance(url, str):
            return self.default_language
        
        # Normalise l'URL pour la détection
        url = url.strip().lower()
        
        # Teste chaque langue dans l'ordre
        for language, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return language
        
        # Fallback vers la langue par défaut
        return self.default_language
    
    def detect_bulk(self, urls: List[str]) -> Dict[str, str]:
        """
        Détecte les langues pour une liste d'URLs
        
        Args:
            urls: Liste des URLs à analyser
            
        Returns:
            Dictionnaire {url: langue}
        """
        results = {}
        for url in urls:
            results[url] = self.detect(url)
        return results
    
    def group_by_language(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Groupe les URLs par langue détectée
        
        Args:
            urls: Liste des URLs à grouper
            
        Returns:
            Dictionnaire {langue: [urls]}
        """
        groups = defaultdict(list)
        
        for url in urls:
            language = self.detect(url)
            groups[language].append(url)
        
        return dict(groups)
    
    def get_language_stats(self, urls: List[str]) -> Dict[str, int]:
        """
        Calcule les statistiques de répartition par langue
        
        Args:
            urls: Liste des URLs à analyser
            
        Returns:
            Dictionnaire {langue: nombre_urls}
        """
        stats = defaultdict(int)
        
        for url in urls:
            language = self.detect(url)
            stats[language] += 1
        
        return dict(stats)
    
    def get_missing_languages(self, old_urls: List[str], new_urls: List[str]) -> List[str]:
        """
        Détecte les langues présentes dans old mais absentes de new
        
        Args:
            old_urls: URLs de l'ancien site
            new_urls: URLs du nouveau site
            
        Returns:
            Liste des langues manquantes
        """
        old_languages = set(self.group_by_language(old_urls).keys())
        new_languages = set(self.group_by_language(new_urls).keys())
        
        missing = old_languages - new_languages
        return sorted(list(missing))
    
    def add_language_pattern(self, language: str, patterns: List[str]) -> None:
        """
        Ajoute des patterns personnalisés pour une langue
        
        Args:
            language: Code de la langue (ex: 'pt', 'ru')
            patterns: Liste des regex patterns à ajouter
        """
        if language not in self.patterns:
            self.patterns[language] = []
        
        self.patterns[language].extend(patterns)
    
    def get_supported_languages(self) -> List[str]:
        """Retourne la liste des langues supportées"""
        return sorted(list(self.patterns.keys()))