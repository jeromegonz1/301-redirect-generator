# 301 Redirect Generator - Sprint 2

## Vue d'ensemble
Application Streamlit pour générer des redirections 301 intelligentes avec support IA sémantique GPT-3.5-turbo et gestion multilangue avancée.

## État actuel (Sprint 2 - Septembre 2025)
- ✅ **IA sémantique** : Matching intelligent avec GPT-3.5-turbo
- ✅ **Support multilangue** : Détection automatique et traitement par langue
- ✅ **Fallbacks 302** : Redirections temporaires pour langues non migrées
- ✅ **Interface avancée** : Mode IA + Mode classique
- ✅ **Tests TDD** : 57/58 tests passent (1 test retry désactivé)

## Modifications récentes (05/09/2025)

### Sprint 3.5 - Export XLS Balt
- ✅ **Nouveau format d'export** : Fichier .xlsx compatible Septeo BALT CMS
- ✅ **Structure conforme** : 2 colonnes exactement (Source, Target) avec URLs absolues uniquement
- ✅ **Intégration interface** : Bouton "💾 Export XLS (Balt)" après traitement complet
- ✅ **Tests TDD complets** : 5/5 tests passent, validation format strict
- ✅ **Gestion des erreurs** : Messages d'aide si openpyxl manquant

### Sprint 3 Enhanced - URLs absolues et fallback intelligent
- ✅ **URLs absolues** : Toutes les redirections utilisent des URLs complètes (source → target)
- ✅ **Fallback 302 intelligent** : Détection automatique langue + redirection vers home langue
- ✅ **Filtres anti-doublons** : Suppression automatique des redirections dupliquées et source==target
- ✅ **Résumé statistiques** : Métriques détaillées avec taux de correspondance IA
- ✅ **Configuration domaine cible** : Input utilisateur pour spécifier le domaine de destination
- ✅ **Format production** : .htaccess prêt à déployer avec commentaires organisés

### Sprint intermédiaire - Sitemap ancien site
- ✅ **Nouvelle option collecte** : Ajout "Sitemap XML" pour ancien site
- ✅ **Tests TDD** : 4 nouveaux tests pour `parse_sitemap` (tous passent)
- ✅ **Interface mise à jour** : 3 options au lieu de 2 pour ancien site
- ✅ **Documentation** : `docs/SPRINT_INTERMEDIAIRE_SITEMAP.md`

### Nouveaux modules développés
1. `language_detector.py` - Détection automatique des langues dans URLs (11 tests)
2. `ai_mapper.py` - Mapping sémantique avec OpenAI GPT-3.5-turbo (10 tests)
3. `fallback_manager.py` - Gestion redirections 302 pour langues manquantes (12 tests)
4. `advanced_interface.py` - Interface avancée Sprint 2

### Architecture mise à jour
```
src/
├── main.py (interface principale avec sélection mode)
├── advanced_interface.py (interface IA + classique)
├── generator.py (générateur classique)
├── scraper.py (scraping sites)
├── language_detector.py (détection langues)
├── ai_mapper.py (IA sémantique)
└── fallback_manager.py (fallbacks 302)

tests/ (58 tests TDD)
docs/ (documentation Sprint 2)
```

## Préférences utilisateur
- **Méthodologie** : TDD strict avec aucun hardcoding
- **Qualité** : Tests complets avant implémentation
- **Architecture** : Modules séparés et réutilisables
- **Documentation** : Sprint docs avec User Stories détaillées

## Configuration technique
- **Streamlit** : Interface web principale sur port 5000
- **OpenAI API** : Clé configurée dans secrets Replit
- **Python 3.11** : Environnement de développement
- **Pytest** : Framework de tests (57 tests passent)

## Fonctionnalités Sprint 2

### Mode IA (Recommandé)
1. **Collecte URLs** : Scraping ancien + Sitemap nouveau
2. **Analyse linguistique** : Détection automatique des langues
3. **Contexte métier** : Amélioration du matching avec spécifications projet
4. **IA sémantique** : GPT-3.5-turbo pour correspondances intelligentes
5. **Fallbacks 302** : Redirections temporaires pour langues manquantes
6. **Configuration** : Température, seuil confiance, taille lots

### Mode Classique
- Mapping alphabétique traditionnel
- Compatible workflow existant
- Sans IA ni analyse linguistique

## Décisions architecturales

### Gestion multilangue
- Détection automatique via patterns URL (`/fr/`, `/en/`, `.de/`)
- Groupement par langue avant processing IA
- Fallbacks 302 automatiques pour langues non migrées

### IA sémantique
- GPT-3.5-turbo pour performance/coût optimal
- Processing par chunks pour gérer volumes importants
- Système de confiance avec seuils configurables
- Retry automatique en cas d'échec temporaire

### Sécurité
- Clé API OpenAI dans secrets Replit
- Validation stricte des réponses JSON
- Gestion d'erreurs robuste

## Tests et qualité
- **Coverage** : 57/58 tests passent (98.3%)
- **TDD** : Tests écrits avant implémentation
- **Mocking** : Simulations OpenAI pour tests offline
- **Edge cases** : Gestion erreurs, données invalides

## Documentation
- `docs/SPRINT_2_README.md` - Guide complet Sprint 2
- User Stories US009-US014 implémentées
- Tests documentés avec exemples d'usage

## Performance
- Traitement par lots pour API OpenAI
- Cache et optimisations mémoire
- Gestion asynchrone des requêtes IA

## Maintenance
- Interface legacy conservée pour compatibilité
- Modules indépendants pour évolutions futures
- Configuration flexible via interface Streamlit