"""
Module de génération des redirections 301
Gère le parsing des URLs et la génération des fichiers .htaccess et .csv
"""

import re
import csv
import xml.etree.ElementTree as ET
from typing import List, Tuple
from urllib.parse import urlparse


class RedirectGenerator:
    """Générateur de redirections 301"""
    
    def __init__(self):
        self.old_urls = []
        self.new_urls = []
    
    def parse_input(self, text_input: str) -> List[str]:
        """Parse l'input utilisateur et extrait les URLs"""
        if not text_input.strip():
            return []
        
        # Détection automatique du format
        if self._is_xml_sitemap(text_input):
            return self._parse_xml_sitemap(text_input)
        elif self._is_csv_format(text_input):
            return self._parse_csv_format(text_input)
        else:
            return self._parse_raw_urls(text_input)
    
    def _is_xml_sitemap(self, text: str) -> bool:
        """Vérifie si le texte est une sitemap XML"""
        return '<loc>' in text and '</loc>' in text
    
    def _is_csv_format(self, text: str) -> bool:
        """Vérifie si le texte est au format CSV"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False
        # Vérifie si au moins une ligne contient une virgule ou tabulation
        return any(',' in line or '\t' in line for line in lines[:3])
    
    def _parse_xml_sitemap(self, xml_text: str) -> List[str]:
        """Parse une sitemap XML et extrait les URLs"""
        urls = []
        # Utilise regex pour extraire les URLs des balises <loc>
        pattern = r'<loc>(.*?)</loc>'
        matches = re.findall(pattern, xml_text, re.IGNORECASE)
        for match in matches:
            urls.append(match.strip())
        return urls
    
    def _parse_csv_format(self, csv_text: str) -> List[str]:
        """Parse un format CSV collé"""
        urls = []
        lines = csv_text.strip().split('\n')
        for line in lines:
            # Gère virgules et tabulations
            if ',' in line:
                parts = line.split(',')
            elif '\t' in line:
                parts = line.split('\t')
            else:
                continue
            
            if len(parts) >= 1:
                urls.append(parts[0].strip())
        return urls
    
    def _parse_raw_urls(self, raw_text: str) -> List[str]:
        """Parse une liste brute d'URLs (une par ligne)"""
        urls = []
        lines = raw_text.strip().split('\n')
        for line in lines:
            url = line.strip()
            if url:
                urls.append(url)
        return urls
    
    def normalize_url(self, url: str) -> str:
        """Normalise une URL"""
        # Supprime les espaces
        url = url.strip()
        
        # Ajoute http:// si pas de protocole
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Parse l'URL
        parsed = urlparse(url)
        
        # Reconstruit l'URL normalisée
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Supprime le trailing slash sauf pour la racine
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        
        return normalized
    
    def generate_redirections(self, old_input: str, new_input: str) -> Tuple[str, List[List[str]]]:
        """Génère les redirections à partir des deux inputs"""
        # Parse les inputs
        old_urls = self.parse_input(old_input)
        new_urls = self.parse_input(new_input)
        
        # Vérifie que les listes ont la même longueur
        if len(old_urls) != len(new_urls):
            raise ValueError(f"Mismatch: {len(old_urls)} anciennes URLs vs {len(new_urls)} nouvelles URLs")
        
        # Génère les redirections
        htaccess_content = ""
        csv_data = [["OLD_FULL_URL", "OLD_PATH", "NEW_FULL_URL", "NEW_PATH"]]
        
        for old_url, new_url in zip(old_urls, new_urls):
            # Normalise les URLs
            old_normalized = self.normalize_url(old_url)
            new_normalized = self.normalize_url(new_url)
            
            # Parse pour extraire le path
            old_parsed = urlparse(old_normalized)
            new_parsed = urlparse(new_normalized)
            
            # Génère la ligne .htaccess
            new_path = new_parsed.path if new_parsed.path else '/'
            htaccess_line = f"Redirect 301 {old_normalized} {new_path}\n"
            htaccess_content += htaccess_line
            
            # Ajoute à la data CSV
            csv_row = [
                old_normalized,
                old_parsed.path if old_parsed.path else '/',
                new_normalized,
                new_path
            ]
            csv_data.append(csv_row)
        
        return htaccess_content, csv_data