"""
SmartInputParser - Parser universel pour tous les formats d'URLs
US-2.1: En tant qu'utilisateur, je veux pouvoir coller n'importe quel format d'URLs
"""

import re
import json
import xml.etree.ElementTree as ET
import csv
import io
from typing import List, Dict, Any
from urllib.parse import urlparse
from smart_input_config import (
    FORMAT_DETECTION_PATTERNS, 
    EXCLUDED_EXTENSIONS, 
    PARSING_LIMITS
)


class SmartInputParser:
    """Parser intelligent qui détecte automatiquement le format d'entrée"""
    
    def __init__(self):
        self.last_statistics = {}
        self.supported_formats = ['xml', 'json', 'csv', 'text']
    
    def detect_and_parse(self, input_text: str) -> List[str]:
        """
        Détecte automatiquement le format et parse les URLs
        
        Args:
            input_text: Texte d'entrée (XML, JSON, CSV ou texte simple)
            
        Returns:
            Liste d'URLs uniques et valides
        """
        if not input_text or not input_text.strip():
            self._update_statistics([], 0, 0, 'empty')
            return []
        
        # Vérifier la taille limite
        if len(input_text) > PARSING_LIMITS['max_input_size_mb'] * 1024 * 1024:
            raise ValueError(f"Input too large (max {PARSING_LIMITS['max_input_size_mb']}MB)")
        
        # Détecter le format
        format_detected = self.detect_format(input_text)
        
        # Parser selon le format
        try:
            if format_detected == 'xml':
                urls = self.parse_xml_sitemap(input_text)
            elif format_detected == 'json':
                urls = self.parse_json(input_text)
            elif format_detected == 'csv':
                urls = self.parse_csv(input_text)
            else:  # text par défaut
                urls = self.parse_text_urls(input_text)
            
            # Filtrer et dédupliquer
            valid_urls = self._filter_and_validate_urls(urls)
            
            # Limiter le nombre d'URLs
            if len(valid_urls) > PARSING_LIMITS['max_urls_per_input']:
                valid_urls = valid_urls[:PARSING_LIMITS['max_urls_per_input']]
            
            # Mettre à jour les statistiques
            total_found = len(urls)
            valid_count = len(valid_urls)
            invalid_count = total_found - valid_count
            self._update_statistics(valid_urls, valid_count, invalid_count, format_detected)
            
            return valid_urls
            
        except Exception as e:
            # Fallback vers parsing texte en cas d'erreur
            print(f"Erreur lors du parsing {format_detected}: {e}")
            urls = self.parse_text_urls(input_text)
            valid_urls = self._filter_and_validate_urls(urls)
            self._update_statistics(valid_urls, len(valid_urls), 0, 'text_fallback')
            return valid_urls
    
    def detect_format(self, input_text: str) -> str:
        """
        Détecte le format du texte d'entrée
        
        Args:
            input_text: Texte à analyser
            
        Returns:
            Format détecté ('xml', 'json', 'csv', 'text')
        """
        input_stripped = input_text.strip()
        
        # Test XML
        for pattern in FORMAT_DETECTION_PATTERNS['xml']:
            if re.search(pattern, input_stripped, re.IGNORECASE | re.MULTILINE):
                return 'xml'
        
        # Test JSON
        for pattern in FORMAT_DETECTION_PATTERNS['json']:
            if re.search(pattern, input_stripped, re.MULTILINE):
                return 'json'
        
        # Test CSV
        for pattern in FORMAT_DETECTION_PATTERNS['csv']:
            if re.search(pattern, input_stripped, re.MULTILINE):
                return 'csv'
        
        # Par défaut : texte
        return 'text'
    
    def parse_xml_sitemap(self, xml_text: str) -> List[str]:
        """
        Parse un sitemap XML
        
        Args:
            xml_text: Contenu XML du sitemap
            
        Returns:
            Liste des URLs trouvées
        """
        urls = []
        
        try:
            # Parser le XML
            root = ET.fromstring(xml_text)
            
            # Namespace pour sitemap
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            # Chercher les URLs avec et sans namespace
            url_elements = (
                root.findall('.//sitemap:url/sitemap:loc', namespaces) or
                root.findall('.//url/loc') or
                root.findall('.//loc')
            )
            
            for url_elem in url_elements:
                if url_elem.text:
                    urls.append(url_elem.text.strip())
            
            # Si pas d'URLs trouvées, chercher dans les sitemaps index
            if not urls:
                sitemap_elements = (
                    root.findall('.//sitemap:sitemap/sitemap:loc', namespaces) or
                    root.findall('.//sitemap/loc')
                )
                for sitemap_elem in sitemap_elements:
                    if sitemap_elem.text:
                        urls.append(sitemap_elem.text.strip())
        
        except ET.ParseError as e:
            print(f"Erreur de parsing XML: {e}")
            # Fallback: extraction regex des URLs dans le XML
            urls = re.findall(r'<loc[^>]*>(https?://[^<]+)</loc>', xml_text, re.IGNORECASE)
        
        return urls
    
    def parse_json(self, json_text: str) -> List[str]:
        """
        Parse des URLs depuis JSON
        
        Args:
            json_text: Contenu JSON
            
        Returns:
            Liste des URLs trouvées
        """
        urls = []
        
        try:
            data = json.loads(json_text)
            
            if isinstance(data, list):
                # Array simple d'URLs
                urls = [str(item) for item in data if isinstance(item, str)]
            elif isinstance(data, dict):
                # Objet JSON - chercher dans toutes les valeurs
                urls = self._extract_urls_from_dict(data)
        
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON: {e}")
            # Fallback: extraction regex
            urls = re.findall(r'"(https?://[^"]+)"', json_text)
        
        return urls
    
    def parse_csv(self, csv_text: str) -> List[str]:
        """
        Parse des URLs depuis CSV
        
        Args:
            csv_text: Contenu CSV
            
        Returns:
            Liste des URLs trouvées
        """
        urls = []
        
        try:
            # Détecter le délimiteur
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(csv_text[:1024]).delimiter
            
            # Parser le CSV
            reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
            
            for row in reader:
                for cell in row:
                    if cell and self._is_valid_url(cell.strip()):
                        urls.append(cell.strip())
        
        except Exception as e:
            print(f"Erreur de parsing CSV: {e}")
            # Fallback: extraction regex
            urls = re.findall(r'https?://[^\s,;"\']+', csv_text)
        
        return urls
    
    def parse_text_urls(self, text: str) -> List[str]:
        """
        Parse des URLs depuis texte simple
        
        Args:
            text: Texte contenant des URLs
            
        Returns:
            Liste des URLs trouvées
        """
        urls = []
        
        # Séparer par lignes
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and self._is_valid_url(line):
                urls.append(line)
        
        # Si pas d'URLs trouvées ligne par ligne, extraire avec regex
        if not urls:
            urls = re.findall(r'https?://[^\s<>"\']+', text)
        
        return urls
    
    def _extract_urls_from_dict(self, data: dict) -> List[str]:
        """Extrait récursivement les URLs d'un dictionnaire"""
        urls = []
        
        for value in data.values():
            if isinstance(value, str) and self._is_valid_url(value):
                urls.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._is_valid_url(item):
                        urls.append(item)
                    elif isinstance(item, dict):
                        urls.extend(self._extract_urls_from_dict(item))
            elif isinstance(value, dict):
                urls.extend(self._extract_urls_from_dict(value))
        
        return urls
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Valide qu'une chaîne est une URL valide
        
        Args:
            url: URL à valider
            
        Returns:
            True si l'URL est valide
        """
        try:
            if not url or len(url) < 10:
                return False
            
            parsed = urlparse(url)
            
            # Doit avoir un scheme et un netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Doit être HTTP ou HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Exclure les extensions de fichiers
            if any(url.lower().endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _filter_and_validate_urls(self, urls: List[str]) -> List[str]:
        """
        Filtre et valide la liste d'URLs
        
        Args:
            urls: Liste d'URLs brutes
            
        Returns:
            Liste d'URLs valides et uniques
        """
        valid_urls = []
        seen_urls = set()
        
        for url in urls:
            if url and self._is_valid_url(url):
                # Normaliser l'URL
                url = url.strip().rstrip('/')
                
                # Dédupliquer
                if url not in seen_urls:
                    seen_urls.add(url)
                    valid_urls.append(url)
        
        return valid_urls
    
    def _update_statistics(self, valid_urls: List[str], valid_count: int, 
                          invalid_count: int, format_detected: str):
        """Met à jour les statistiques de parsing"""
        self.last_statistics = {
            'total_lines': valid_count + invalid_count,
            'valid_urls': valid_count,
            'invalid_entries': invalid_count,
            'format_detected': format_detected,
            'unique_urls': len(set(valid_urls)) if valid_urls else 0
        }
    
    def get_last_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du dernier parsing
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return self.last_statistics.copy()
    
    def get_supported_formats(self) -> List[str]:
        """
        Retourne la liste des formats supportés
        
        Returns:
            Liste des formats supportés
        """
        return self.supported_formats.copy()