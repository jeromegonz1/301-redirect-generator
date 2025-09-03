# 🦎 301 Redirect Generator

## Vue d'ensemble

Application Streamlit pour générer automatiquement des redirections 301 entre un ancien site et un nouveau site après refonte. Développée selon une approche TDD avec 100% de tests passants.

## État actuel

✅ **Fonctionnel et déployé avec module de scraping**
- Interface Streamlit opérationnelle sur port 5000
- Tests TDD complets (24/24 passants : 9 générateur + 15 scraper)
- Module de scraping automatique implémenté selon SCRAPER_SPEC.md
- Configuration de déploiement prête
- Workflow configuré et en fonctionnement

## Architecture

```
/301-redirect-generator
├── src/
│   ├── main.py          # Interface Streamlit
│   ├── generator.py     # Logique de parsing/génération
│   └── scraper.py       # Module de scraping automatique
├── tests/
│   ├── test_generator.py # Tests TDD générateur (9 tests)
│   └── test_scraper.py   # Tests TDD scraper (15 tests) 
├── outputs/             # Fichiers générés (vide)
├── .streamlit/
│   └── config.toml      # Config Streamlit (port 5000)
├── requirements.txt     # Dépendances avec scraping
├── user_stories.md      # User Stories complètes
├── CDC.md              # Cahier des charges mis à jour
├── SCRAPER_SPEC.md     # Spécification technique scraping
├── SCRAPING_STRATEGY.md # Stratégie de scraping
├── UX_ENHANCEMENTS.md  # Améliorations UX
├── US006.md           # Issue scraping automatique
├── AGENT_BRIEF.md     # Brief technique détaillé
└── readme.md          # Documentation originale
```

## Fonctionnalités implémentées

### US001 - Parsing multi-format ✅
- Sitemap XML (balises `<loc>`)
- Liste brute d'URLs (une par ligne)
- CSV collé (colonnes séparées)
- Détection automatique du format

### US002 - Génération .htaccess ✅
- Format: `Redirect 301 [URL_COMPLETE] [CHEMIN_RELATIF]`
- Normalisation automatique des URLs
- Gestion des erreurs de correspondance

### US003 - Export CSV d'audit ✅
- Structure: `OLD_FULL_URL, OLD_PATH, NEW_FULL_URL, NEW_PATH`
- Compatible Excel/Google Sheets

### US004 - Interface ultra-simple ✅
- Deux zones de texte pour coller les URLs
- Bouton "Générer" unique
- Téléchargements .htaccess et .csv
- Aucun paramètre technique

### US005 - Qualité TDD ✅
- 24 tests automatisés passants (9 générateur + 15 scraper)
- Aucune URL codée en dur
- Structure de projet claire

### US006 - Scraping automatique ✅ **NOUVEAU**
- Module de scraping intelligent (src/scraper.py)
- Crawling automatique jusqu'à 200 pages par site
- Normalisation des URLs et gestion des domaines
- Support authentification Basic Auth
- User-Agent dédié : "301-Redirect-Bot"
- Gestion des erreurs avec fallback
- 15 tests automatisés couvrant tous les cas

## Configuration

- **Port**: 5000 (obligatoire Replit)
- **Host**: 0.0.0.0 (permet proxy iframe)
- **Déploiement**: Autoscale configuré

## Utilisation

1. Coller anciennes URLs dans le premier champ
2. Coller nouvelles URLs dans le second champ
3. Cliquer "Générer les redirections"
4. Télécharger fichiers .htaccess et .csv

## Tests

```bash
python -m pytest tests/ -v
# 24 passed in 1.06s (9 générateur + 15 scraper)
```

### Tests par module
- **Generator** : 9 tests (parsing, génération, validation)
- **Scraper** : 15 tests (crawling, normalisation, authentification)

## Déploiement

Configuration de déploiement automatique prête pour production.

---

*Projet créé selon les User Stories et CDC fournis*