# 🦎 301 Redirect Generator

## Vue d'ensemble

Application Streamlit pour générer automatiquement des redirections 301 entre un ancien site et un nouveau site après refonte. Développée selon une approche TDD avec 100% de tests passants.

## État actuel

✅ **Fonctionnel et déployé**
- Interface Streamlit opérationnelle sur port 5000
- Tests TDD complets (9/9 passants) 
- Configuration de déploiement prête
- Workflow configuré et en fonctionnement

## Architecture

```
/301-redirect-generator
├── src/
│   ├── main.py          # Interface Streamlit
│   └── generator.py     # Logique de parsing/génération
├── tests/
│   └── test_generator.py # Tests TDD complets
├── outputs/             # Fichiers générés (vide)
├── .streamlit/
│   └── config.toml      # Config Streamlit (port 5000)
├── requirements.txt
├── user_stories.md      # User Stories complètes
├── CDC.md              # Cahier des charges
└── readme.md           # Documentation originale
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
- 9 tests automatisés passants
- Aucune URL codée en dur
- Structure de projet claire

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
# 9 passed in 0.08s
```

## Déploiement

Configuration de déploiement automatique prête pour production.

---

*Projet créé selon les User Stories et CDC fournis*