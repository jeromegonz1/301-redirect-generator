"""
Configuration pour SmartInputParser
Évite le hardcoding et centralise les paramètres
"""

# Patterns de détection de format
FORMAT_DETECTION_PATTERNS = {
    'xml': [
        r'^\s*<\?xml',
        r'<urlset',
        r'<sitemap',
        r'xmlns.*sitemap'
    ],
    'json': [
        r'^\s*\[',
        r'^\s*\{',
        r'"https?://'
    ],
    'csv': [
        r',.*https?://',
        r'url\s*,',
        r'.*,.*\n.*,.*'
    ]
}

# Extensions de fichiers URL valides à exclure du parsing
EXCLUDED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp',
    '.pdf', '.doc', '.docx', '.zip', '.rar', '.mp4', '.mp3', '.avi',
    '.css', '.js', '.min.js', '.min.css'
}

# Headers HTTP pour éviter les 403
DEFAULT_HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

# Configuration retry
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 1.5,
    'retry_status_codes': [429, 500, 502, 503, 504],
    'timeout': 10
}

# Limites de parsing
PARSING_LIMITS = {
    'max_urls_per_input': 10000,
    'max_input_size_mb': 50,
    'url_validation_timeout': 1  # seconde pour valider chaque URL
}