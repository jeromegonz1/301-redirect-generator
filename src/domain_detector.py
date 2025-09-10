"""
Détecteur intelligent de domaine cible pour Fire Snake 301
Philosophy: TDD, No hardcoding, Smart detection
"""

import re
from urllib.parse import urlparse
from typing import List, Optional


class DomainDetector:
    """Détecte intelligemment le domaine cible depuis les URLs de l'ancien site"""
    
    def extract_domain_from_urls(self, urls: List[str]) -> Optional[str]:
        """
        Extrait le domaine depuis une liste d'URLs
        
        Args:
            urls: Liste d'URLs de l'ancien site
            
        Returns:
            Domaine au format https://www.example.com ou None si impossible
        """
        if not urls:
            return None
        
        # Filtre les URLs valides
        valid_urls = [url.strip() for url in urls if url.strip()]
        if not valid_urls:
            return None
        
        domains = []
        
        for url in valid_urls:
            try:
                # Ajoute http:// si pas de protocole
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                parsed = urlparse(url)
                
                # Vérifie que c'est une URL HTTP/HTTPS valide avec un vrai domaine
                if (parsed.scheme in ('http', 'https') and 
                    parsed.netloc and 
                    '.' in parsed.netloc and
                    not parsed.netloc.startswith('.')):
                    # Reconstruit le domaine de base
                    domain = f"{parsed.scheme}://{parsed.netloc}"
                    domains.append(domain)
                    
            except Exception:
                # Ignore les URLs malformées
                continue
        
        if not domains:
            return None
        
        # Prend le domaine le plus fréquent
        domain_counts = {}
        for domain in domains:
            # Normalise pour compter (préfère HTTPS si les deux existent)
            netloc = urlparse(domain).netloc
            domain_counts[netloc] = domain_counts.get(netloc, [])
            domain_counts[netloc].append(domain)
        
        # Trouve le netloc le plus fréquent
        most_common_netloc = max(domain_counts.keys(), key=lambda x: len(domain_counts[x]))
        
        # Préfère HTTPS parmi les domaines de ce netloc
        candidate_domains = domain_counts[most_common_netloc]
        https_domains = [d for d in candidate_domains if d.startswith('https://')]
        
        if https_domains:
            return https_domains[0]
        else:
            return candidate_domains[0]
    
    def extract_domain_from_sitemap(self, sitemap_xml: str) -> Optional[str]:
        """
        Extrait le domaine depuis une sitemap XML
        
        Args:
            sitemap_xml: Contenu XML de la sitemap
            
        Returns:
            Domaine détecté ou None
        """
        if not sitemap_xml.strip():
            return None
        
        # Extrait les URLs des balises <loc>
        pattern = r'<loc>(.*?)</loc>'
        matches = re.findall(pattern, sitemap_xml, re.IGNORECASE)
        
        if not matches:
            return None
        
        return self.extract_domain_from_urls(matches)
    
    def detect_from_user_input(self, user_input: str) -> Optional[str]:
        """
        Détection intelligente depuis l'input utilisateur
        
        Args:
            user_input: Input brut de l'utilisateur (XML, URLs, etc.)
            
        Returns:
            Domaine détecté ou None
        """
        if not user_input.strip():
            return None
        
        # Détecte si c'est une sitemap XML
        if '<loc>' in user_input and '</loc>' in user_input:
            return self.extract_domain_from_sitemap(user_input)
        
        # Sinon, traite comme une liste d'URLs
        lines = [line.strip() for line in user_input.split('\n') if line.strip()]
        return self.extract_domain_from_urls(lines)
    
    def suggest_target_domain(self, old_site_input: str, current_target: str = "") -> str:
        """
        Suggère intelligemment le domaine cible basé sur l'ancien site
        
        Args:
            old_site_input: Input de l'ancien site
            current_target: Domaine cible actuel (peut être vide)
            
        Returns:
            Suggestion de domaine cible
        """
        # Si un domaine cible est déjà renseigné et valide, le garde
        if current_target and current_target.startswith(('http://', 'https://')):
            return current_target
        
        # Sinon, détecte depuis l'ancien site
        detected_domain = self.detect_from_user_input(old_site_input)
        
        if detected_domain:
            # Peut être personnalisé avec des règles métier ici
            # Par exemple: remplacer certains domaines connus
            return self._apply_domain_mapping_rules(detected_domain)
        
        # Fallback: domaine vide pour que l'utilisateur renseigne
        return ""
    
    def _apply_domain_mapping_rules(self, detected_domain: str) -> str:
        """
        Applique des règles de mapping de domaines si nécessaire
        Peut être étendu sans hardcoding
        
        Args:
            detected_domain: Domaine détecté de l'ancien site
            
        Returns:
            Domaine suggéré pour le nouveau site
        """
        # Par défaut, suggère le même domaine
        # L'utilisateur peut le modifier dans l'interface
        return detected_domain