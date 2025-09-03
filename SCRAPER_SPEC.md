# 📄 SCRAPER_SPEC.md – Spécification du module de scraping

## 🧭 Objectif

Ce module est conçu pour extraire automatiquement la liste des URLs internes d'un site web (ancien ou nouveau) à partir d'une **URL racine**.  
Il permet d'alimenter l'outil 301 Redirect Generator **sans intervention manuelle**.  
Il remplace le copier-coller d'un sitemap ou d'un export GA / SEO par un crawl intelligent.

---

## 🧠 Fonction attendue

- L'utilisateur saisit **l'URL d'un ancien site** et **l'URL d'un site nouveau / préprod**
- Le module effectue un **crawl automatique** jusqu'à un certain nombre de pages (par défaut : 200 max)
- Il retourne :
  - Une **liste d'URLs complètes** pour le site A (ancien)
  - Une **liste d'URLs relatives** pour le site B (nouveau / préprod)

---

## 🧱 Stack recommandée

| Élément | Choix |
|--------|-------|
| Langage | Python 3.x |
| HTTP client | `requests` |
| Parsing HTML | `BeautifulSoup` |
| Crawl queue | `deque` (`collections`) |
| Normalisation URL | `urllib.parse`, `tldextract` |
| Respect des contraintes SEO | Optionnel / désactivable (robots.txt, nofollow) |
| Alternatives futures | Interface extensible vers `Playwright`, `Scrapy` |

---

## 🔐 Accès préprod

Prévoir une capacité d'accès **aux environnements restreints** :

| Cas | Solution |
|-----|----------|
| `robots.txt` bloquant | Overridable avec `User-Agent: 301-Redirect-Bot` |
| Meta `noindex/nofollow` | Ignorés par défaut |
| Authentification | Support `Basic Auth` ou `Bearer Token` (à injecter dans headers) |
| Préprod privée (non exposée) | Fallback : copier-coller / upload manuel |

---

## 📥 Entrée attendue

```python
crawl_site(
    url_root: str,
    max_pages: int = 200,
    user_agent: str = "301-Redirect-Bot",
    auth: Optional[Tuple[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> List[str]
```

## 📤 Sortie

Une liste d'URLs propres, normalisées, sans doublon :

```python
[
    "https://vieux-site.com/contact",
    "https://vieux-site.com/hebergement/chalet",
    ...
]
```

Ou pour le nouveau site :

```python
[
    "/contact",
    "/hebergements/chalets",
    ...
]
```

## 🧪 Règles fonctionnelles

Le crawler :

- suit les liens internes (`<a href>`)
- ignore les liens externes (autres domaines)
- nettoie les URLs (sans query string, trailing slash)
- évite les doublons
- ignore les ancres (#)
- Le crawl est large mais limité : max 200 pages par domaine
- Les URLs peuvent être triées ou conservées dans l'ordre d'apparition (au choix)

## 🧩 Cas à gérer

| Cas | Comportement |
|-----|-------------|
| HTTP 403 / 404 | Ignoré avec log silencieux |
| Timeout / exception | Ignoré avec log silencieux |
| Lien vide ou ancre seule (#) | Ignoré |
| Boucle infinie | Empêchée via set() de pages visitées |

## 🔧 Exemple d'implémentation de base

```python
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
from collections import deque

def crawl_site(url_root: str, max_pages=200) -> list:
    visited = set()
    to_visit = deque([url_root])
    collected = []

    while to_visit and len(collected) < max_pages:
        url = to_visit.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            res = requests.get(url, timeout=5, headers={'User-Agent': '301-Redirect-Bot'})
            soup = BeautifulSoup(res.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link['href'])
                if href.startswith(url_root) and href not in visited:
                    to_visit.append(href)
            collected.append(url)
        except:
            continue
    return collected
```

## 🔄 Fallback si échec du crawl

Si le site ne répond pas / bloqué / inaccessible :

- Retourne None ou liste vide
- Affiche un message UX : "Le site est inaccessible, veuillez coller les URLs ou importer un fichier sitemap"

## 🧪 Tests attendus (Pytest)

- `test_crawl_site_respects_max_pages()`
- `test_crawl_removes_query_strings_and_fragments()`
- `test_crawl_ignores_external_domains()`
- `test_crawl_with_basic_auth_header()`

## 🔄 Fichiers concernés

- `src/scraper.py` → contient `crawl_site()` et helpers
- `tests/test_scraper.py` → tests unitaires du module
- `main.py` → appelle `crawl_site()` si mode scraping sélectionné

## 🧙 Bonus futur

- Mode "deep crawl" avec règles personnalisées
- Scraping asynchrone (via aiohttp)
- UI avec visualisation des liens
- Intégration dans Fire Salamander 👀