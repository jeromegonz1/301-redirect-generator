"""
Module de scraping automatique pour le 301 Redirect Generator
Extrait automatiquement les URLs internes d'un site web
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from typing import List, Optional, Tuple, Dict
import tldextract
import time
import logging
import xml.etree.ElementTree as ET

# Configuration du logging silencieux
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class WebScraper:
    """Scraper intelligent pour extraire les URLs internes d'un site"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': '301-Redirect-Bot'
        })
    
    def normalize_url(self, url: str) -> str:
        """Normalise une URL en supprimant query strings, fragments, trailing slash"""
        parsed = urlparse(url)
        
        # Reconstruit l'URL sans query string ni fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        
        # Supprime le trailing slash sauf pour la racine
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        
        return normalized
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """Vérifie si deux URLs appartiennent au même domaine"""
        domain1 = tldextract.extract(url1)
        domain2 = tldextract.extract(url2)
        
        return (domain1.domain == domain2.domain and 
                domain1.suffix == domain2.suffix)
    
    def extract_links_from_html(self, html: str, base_url: str) -> List[str]:
        """Extrait tous les liens internes d'une page HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                
                # Ignore les ancres vides ou juste des fragments
                if not href or href.startswith('#'):
                    continue
                
                # Construit l'URL absolue
                absolute_url = urljoin(base_url, href)
                
                # Vérifie que c'est un lien interne
                if self.is_same_domain(absolute_url, base_url):
                    normalized = self.normalize_url(absolute_url)
                    links.append(normalized)
            
            return links
        except Exception:
            return []
    
    def crawl_site(self, 
                   url_root: str, 
                   max_pages: int = 200,
                   auth: Optional[Tuple[str, str]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   timeout: int = 5) -> List[str]:
        """
        Crawl un site web et retourne la liste des URLs internes trouvées
        
        Args:
            url_root: URL racine du site à crawler
            max_pages: Nombre maximum de pages à crawler
            auth: Tuple (username, password) pour Basic Auth
            headers: Headers HTTP supplémentaires
            timeout: Timeout en secondes pour chaque requête
            
        Returns:
            Liste des URLs internes trouvées
        """
        
        # Normalise l'URL racine
        url_root = self.normalize_url(url_root)
        
        # Configure l'authentification si fournie
        if auth:
            self.session.auth = auth
        
        # Ajoute les headers supplémentaires
        if headers:
            self.session.headers.update(headers)
        
        visited = set()
        to_visit = deque([url_root])
        collected_urls = []
        
        while to_visit and len(collected_urls) < max_pages:
            current_url = to_visit.popleft()
            
            # Évite les doublons
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            try:
                # Fait la requête HTTP
                response = self.session.get(current_url, timeout=timeout)
                
                # Ignore les erreurs HTTP (403, 404, etc.)
                if response.status_code >= 400:
                    continue
                
                # Ajoute l'URL à la collection
                collected_urls.append(current_url)
                
                # Extrait les liens de la page
                new_links = self.extract_links_from_html(response.text, current_url)
                
                # Ajoute les nouveaux liens à la queue
                for link in new_links:
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)
                
                # Délai poli entre les requêtes
                time.sleep(0.1)
                
            except Exception:
                # Ignore silencieusement toutes les erreurs (timeout, connection, etc.)
                continue
        
        return collected_urls
    
    def crawl_site_relative(self, url_root: str, **kwargs) -> List[str]:
        """
        Crawl un site et retourne les URLs sous forme relative
        Utile pour le nouveau site dans les redirections
        """
        absolute_urls = self.crawl_site(url_root, **kwargs)
        relative_urls = []
        
        parsed_root = urlparse(url_root)
        base_domain = f"{parsed_root.scheme}://{parsed_root.netloc}"
        
        for url in absolute_urls:
            if url.startswith(base_domain):
                relative_path = url[len(base_domain):]
                if not relative_path:
                    relative_path = '/'
                relative_urls.append(relative_path)
            
        return relative_urls


# Fonction helper pour compatibilité avec l'ancienne API
def crawl_site(url_root: str, 
               max_pages: int = 200,
               user_agent: str = "301-Redirect-Bot",
               auth: Optional[Tuple[str, str]] = None,
               headers: Optional[Dict[str, str]] = None) -> List[str]:
    """
    Fonction helper pour crawler un site web
    Compatible avec l'exemple de la spécification
    """
    scraper = WebScraper()
    
    # Met à jour le User-Agent si fourni
    if user_agent != "301-Redirect-Bot":
        custom_headers = headers or {}
        custom_headers['User-Agent'] = user_agent
        headers = custom_headers
    
    return scraper.crawl_site(
        url_root=url_root,
        max_pages=max_pages,
        auth=auth,
        headers=headers
    )


def crawl_site_with_fallback(url_root: str, max_pages: int = 200) -> Tuple[List[str], bool]:
    """
    Crawl un site avec gestion de fallback
    
    Returns:
        Tuple (urls_list, success_flag)
        Si success_flag est False, le scraping a échoué
    """
    try:
        scraper = WebScraper()
        urls = scraper.crawl_site(url_root, max_pages)
        
        # Considère le scraping comme réussi s'il y a au moins une URL
        if urls:
            return urls, True
        else:
            return [], False
            
    except Exception:
        return [], False


def parse_sitemap(sitemap_url: str, recursive: bool = True, _visited: set = None) -> List[str]:
    """
    Parse un sitemap XML (incluant les sitemaps Yoast) et extrait toutes les URLs.
    
    Args:
        sitemap_url: URL du sitemap à parser
        recursive: Si True, parse récursivement les sitemaps index
        _visited: Set des sitemaps déjà visités (pour éviter les boucles infinies)
    
    Returns:
        Liste des URLs trouvées dans le sitemap
    """
    if _visited is None:
        _visited = set()
    
    if sitemap_url in _visited:
        return []
    
    _visited.add(sitemap_url)
    urls = []
    
    try:
        # Configuration du user-agent pour éviter les blocages
        headers = {
            'User-Agent': '301-Redirect-Bot (Sitemap Parser)',
            'Accept': 'application/xml,text/xml,application/xhtml+xml'
        }
        
        response = requests.get(sitemap_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse le XML avec BeautifulSoup (plus robuste)
        soup = BeautifulSoup(response.content, 'xml')
        
        # Extraire toutes les balises <loc>
        loc_tags = soup.find_all('loc')
        for loc in loc_tags:
            url = loc.text.strip()
            if url:
                # Vérifier si c'est un sitemap ou une URL normale
                # Détecte les patterns courants de sitemaps: sitemap*.xml, *-sitemap.xml, etc.
                is_sitemap = any([
                    'sitemap' in url.lower(),
                    url.endswith('.xml'),
                    'page-sitemap' in url.lower(),
                    'post-sitemap' in url.lower(),
                    'category-sitemap' in url.lower(),
                    'product-sitemap' in url.lower()
                ])
                
                if recursive and is_sitemap:
                    # C'est un sous-sitemap (pages, articles, etc.), le parser récursivement
                    print(f"  → Parsing sub-sitemap: {url}")
                    sub_urls = parse_sitemap(url, recursive=True, _visited=_visited)
                    urls.extend(sub_urls)
                else:
                    # C'est une URL de contenu normale
                    urls.append(url)
        
        # Dédoublonner les URLs
        urls = list(dict.fromkeys(urls))
        
        print(f"Parsed {len(urls)} URLs from sitemap: {sitemap_url}")
        return urls
        
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du sitemap {sitemap_url}: {e}")
        return []
    except Exception as e:
        print(f"Erreur lors du parsing du sitemap {sitemap_url}: {e}")
        return []