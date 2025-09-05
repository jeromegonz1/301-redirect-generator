"""
Module TDD Sprint 3 - Fallback intelligent 302 pour URLs non matchées
US009 - Gestion automatique des URLs sans correspondance IA
"""

import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import csv
from io import StringIO


class Fallback302Intelligent:
    """Gestionnaire intelligent des fallbacks 302 pour URLs non matchées"""
    
    def __init__(self, enable_fallback_302: bool = True, default_fallback_lang: str = "fr"):
        """
        Initialise le gestionnaire de fallbacks 302
        
        Args:
            enable_fallback_302: Active/désactive les redirections 302 automatiques
            default_fallback_lang: Langue par défaut si aucune langue détectée
        """
        self.enable_fallback_302 = enable_fallback_302
        self.default_fallback_lang = default_fallback_lang
        
        # Pattern pour détecter les codes de langue dans les URLs
        self.language_pattern = re.compile(r'/([a-z]{2})/')
        
        # Langues supportées
        self.supported_languages = {'fr', 'en', 'de', 'es', 'it', 'nl'}
    
    def detect_unmatched_urls(self, old_urls: List[str], ai_matches: List[Dict]) -> List[str]:
        """
        Détecte les URLs de l'ancien site qui n'ont pas été matchées par l'IA
        
        Args:
            old_urls: Liste complète des URLs de l'ancien site
            ai_matches: Résultats du matching IA avec champ 'old_url'
            
        Returns:
            Liste des URLs non matchées
        """
        matched_urls = {match["old_url"] for match in ai_matches}
        unmatched = [url for url in old_urls if url not in matched_urls]
        return unmatched
    
    def extract_language_from_url(self, url: str) -> Optional[str]:
        """
        Extrait le code de langue depuis une URL
        
        Args:
            url: URL à analyser
            
        Returns:
            Code langue (ex: 'fr', 'en') ou None si non trouvé
        """
        # Nettoie l'URL pour extraire le path
        if url.startswith('http'):
            parsed = urlparse(url)
            path = parsed.path
        else:
            path = url
            
        # Recherche du pattern /xx/
        match = self.language_pattern.search(path)
        if match:
            lang = match.group(1)
            if lang in self.supported_languages:
                return lang
                
        return None
    
    def generate_302_redirect(self, old_url: str) -> Dict[str, str]:
        """
        Génère une redirection 302 vers la page d'accueil de la langue
        
        Args:
            old_url: URL de l'ancien site à rediriger
            
        Returns:
            Dictionnaire avec les données de redirection 302
        """
        # Extraction de la langue
        language = self.extract_language_from_url(old_url)
        
        if language:
            target_url = f"/{language}/"
        else:
            # Fallback vers langue par défaut
            target_url = f"/{self.default_fallback_lang}/"
        
        return {
            "type": "302",
            "old_url": old_url,
            "target_url": target_url,
            "comment": "# Fallback temporaire - à retraiter manuellement"
        }
    
    def export_to_csv(self, fallback_data: List[Dict]) -> str:
        """
        Exporte les données de fallback vers un format CSV
        
        Args:
            fallback_data: Liste des données de fallback
            
        Returns:
            Contenu CSV sous forme de string
        """
        output = StringIO()
        
        if not fallback_data:
            return ""
            
        # En-têtes CSV
        fieldnames = ["old_url", "target_url", "language", "status", "comment"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in fallback_data:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def generate_htaccess_with_fallbacks(self, redirect_data: List[Dict]) -> str:
        """
        Génère le contenu .htaccess avec redirections 301 et 302 annotées
        
        Args:
            redirect_data: Liste mixte de redirections 301 et 302
            
        Returns:
            Contenu .htaccess formaté
        """
        lines = []
        
        for redirect in redirect_data:
            redirect_type = redirect.get("type", "301")
            
            if redirect_type == "302":
                # Ajouter le commentaire avant la redirection 302
                comment = redirect.get("comment", "# Fallback temporaire")
                lines.append(comment)
                lines.append(f"Redirect 302 {redirect['old_url']} {redirect['target_url']}")
                lines.append("")  # Ligne vide pour la lisibilité
            else:
                # Redirection 301 normale
                old_url = redirect.get("old_url", "")
                new_url = redirect.get("new_url", redirect.get("target_url", ""))
                lines.append(f"Redirect 301 {old_url} {new_url}")
        
        return "\n".join(lines)
    
    def process_unmatched_urls(self, unmatched_urls: List[str]) -> List[Dict]:
        """
        Traite les URLs non matchées selon la configuration
        
        Args:
            unmatched_urls: URLs sans correspondance IA
            
        Returns:
            Liste des actions effectuées (vide si fallback désactivé)
        """
        if not self.enable_fallback_302:
            return []
        
        results = []
        for url in unmatched_urls:
            redirect_302 = self.generate_302_redirect(url)
            results.append(redirect_302)
            
        return results
    
    def process_ai_results(self, ai_session_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les résultats complets d'une session IA et génère les fallbacks
        
        Args:
            ai_session_results: Résultats avec 'matched_urls' et 'unmatched_urls'
            
        Returns:
            Dictionnaire avec fallbacks 302, CSV et lignes .htaccess
        """
        unmatched_urls = ai_session_results.get("unmatched_urls", [])
        
        if not self.enable_fallback_302 or not unmatched_urls:
            return {
                "fallback_302_redirects": [],
                "csv_export_data": [],
                "htaccess_lines": []
            }
        
        # Génération des redirections 302
        fallback_redirects = []
        csv_data = []
        
        for url in unmatched_urls:
            redirect_302 = self.generate_302_redirect(url)
            fallback_redirects.append(redirect_302)
            
            # Données pour CSV
            csv_row = {
                "old_url": url,
                "target_url": redirect_302["target_url"],
                "language": self.extract_language_from_url(url),
                "status": "fallback_302",
                "comment": "À retraiter manuellement"
            }
            csv_data.append(csv_row)
        
        # Génération des lignes .htaccess
        htaccess_lines = []
        for redirect in fallback_redirects:
            htaccess_lines.append(redirect["comment"])
            htaccess_lines.append(f"Redirect 302 {redirect['old_url']} {redirect['target_url']}")
        
        return {
            "fallback_302_redirects": fallback_redirects,
            "csv_export_data": csv_data,
            "htaccess_lines": htaccess_lines
        }