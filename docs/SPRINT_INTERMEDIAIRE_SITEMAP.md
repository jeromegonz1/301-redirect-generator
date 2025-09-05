# Sprint Intermédiaire - Sitemap pour Ancien Site

## 📋 Vue d'ensemble
Ajout de la fonctionnalité de parsing sitemap XML pour la collecte des URLs de l'ancien site, en complément des options existantes (scraping et saisie manuelle).

**Date**: 05 septembre 2025  
**Type**: Sprint intermédiaire (amélioration fonctionnelle)  
**Méthodologie**: TDD (Test-Driven Development)

## 🎯 Objectif
Permettre aux utilisateurs d'utiliser le sitemap XML de l'ancien site pour collecter les URLs, offrant ainsi une alternative efficace au scraping traditionnel.

## 💡 Justification
### Pourquoi cette fonctionnalité ?
1. **Complétude des données** : Les sitemaps contiennent souvent toutes les URLs importantes d'un site
2. **Performance** : Plus rapide que le scraping page par page
3. **Fiabilité** : Évite les blocages anti-bot et les timeouts
4. **Cohérence d'interface** : Symétrie avec l'option sitemap du nouveau site
5. **Cas d'usage réels** : Nombreux anciens sites ont des sitemaps accessibles

### Cas d'usage typiques
- Ancien site WordPress avec sitemap Yoast accessible
- Sites avec robots.txt pointant vers sitemap public
- Migrations où le scraping est bloqué/lent
- Sites avec structure complexe difficile à scraper

## 🔧 Implémentation

### Approche TDD suivie
1. **Tests d'abord** : Écriture de 4 tests couvrant tous les cas d'usage
2. **Modification interface** : Ajout de l'option "Sitemap XML" pour ancien site
3. **Validation intégration** : Tests complets de bout en bout

### Tests développés
- ✅ `test_parse_sitemap_basic_xml` : Parsing sitemap standard
- ✅ `test_parse_sitemap_error_handling` : Gestion d'erreurs réseau
- ✅ `test_parse_sitemap_empty_xml` : Sitemap vide
- ✅ `test_parse_sitemap_ancien_site_workflow` : Workflow complet ancien site

### Modifications code
1. **Tests** (`tests/test_scraper.py`)
   - Ajout classe `TestParseSitemap` avec 4 tests TDD
   - Mocking complet des requêtes HTTP avec XML réaliste
   - Validation workflow spécifique ancien site

2. **Interface** (`src/advanced_interface.py`)
   - Ajout option "Sitemap XML" dans radio button ancien site
   - Interface de saisie URL sitemap avec placeholder
   - Bouton "🗺️ Parser sitemap ancien site" avec spinner
   - Messages de succès/erreur appropriés

## 📊 Nouvelle interface utilisateur

### Avant (2 options)
```
🔗 Ancien site
○ URL à scraper
○ Liste manuelle
```

### Après (3 options)
```
🔗 Ancien site  
○ URL à scraper
○ Sitemap XML          ← NOUVEAU
○ Liste manuelle
```

### Workflow utilisateur
1. Sélectionner "Sitemap XML" pour ancien site
2. Saisir URL du sitemap (ex: `https://ancien-site.com/sitemap.xml`)
3. Cliquer "🗺️ Parser sitemap ancien site"
4. URLs extraites automatiquement et stockées
5. Continuer avec analyse IA/génération redirections

## 🧪 Qualité et tests

### Couverture tests
- **4 nouveaux tests** ajoutés spécifiquement pour cette fonctionnalité
- **100% de réussite** sur tous les scénarios testés
- **Mocking complet** des dépendances externes (requests, XML)

### Scénarios testés
1. **Sitemap basique** : URLs standards avec balises `<loc>`
2. **Gestion d'erreurs** : Timeouts, erreurs réseau
3. **Sitemap vide** : Cas limite avec XML valide mais sans URLs
4. **Workflow réaliste** : Sitemap multilingue d'ancien site

### Validation intégration
- ✅ Fonction `parse_sitemap` réutilise code existant (DRY)
- ✅ Interface cohérente avec options nouveau site
- ✅ Pas de régression sur fonctionnalités existantes
- ✅ Tests passent dans l'environnement complet

## 📈 Avantages apportés

### Pour l'utilisateur
1. **Plus d'options de collecte** : 3 méthodes au lieu de 2
2. **Rapidité** : Parsing sitemap plus rapide que scraping
3. **Complétude** : Sitemaps souvent plus exhaustifs
4. **Cohérence** : Même workflow que nouveau site

### Pour le développement
1. **Réutilisation code** : Fonction `parse_sitemap` existante
2. **Tests robustes** : 4 nouveaux tests TDD
3. **Maintenabilité** : Interface modulaire et extensible
4. **Documentation** : Sprint documenté selon process

## 🔧 Détails techniques

### Fonction réutilisée
- `parse_sitemap()` de `src/scraper.py`
- Support sitemaps index récursifs
- Gestion robuste des erreurs
- Déduplication automatique des URLs

### Interface mise à jour
```python
# Nouveau choix dans radio button
old_input_mode = st.radio("Mode", [
    "URL à scraper", 
    "Sitemap XML",        # ← AJOUTÉ
    "Liste manuelle"
], key="old")

# Nouvelle condition elif
elif old_input_mode == "Sitemap XML":
    old_sitemap_url = st.text_input("URL du sitemap ancien site", 
                                   placeholder="https://ancien-site.com/sitemap.xml")
    if st.button("🗺️ Parser sitemap ancien site"):
        # Logique de parsing...
```

## 📝 Instructions d'utilisation

### Pour l'utilisateur final
1. **Accéder au Mode IA** : Sélectionner "🚀 Mode IA (Sprint 2)"
2. **Choisir Sitemap** : Dans "🔗 Ancien site", sélectionner "Sitemap XML"
3. **Saisir URL** : Entrer l'URL du sitemap (format: `https://site.com/sitemap.xml`)
4. **Parser** : Cliquer "🗺️ Parser sitemap ancien site"
5. **Validation** : Vérifier le nombre d'URLs extraites
6. **Continuer** : Procéder avec nouveau site et génération IA

### URLs sitemap courantes
- `/sitemap.xml` (standard)
- `/sitemap_index.xml` (WordPress Yoast)
- `/wp-sitemap.xml` (WordPress natif)
- Consulter `/robots.txt` pour localiser le sitemap

## 🔍 Points d'attention

### Prérequis
- Sitemap XML accessible publiquement
- Format XML valide selon standards sitemaps.org
- URLs complètes (pas relatives) dans les balises `<loc>`

### Limitations connues
- Nécessite sitemap public (pas de authentification)
- Format XML uniquement (pas de support TXT)
- Timeout de 30 secondes par requête

### Cas d'échec possibles
- Sitemap protégé par authentification
- XML malformé ou format non-standard
- URLs relatives dans les balises `<loc>`
- Timeouts sur sites lents

## 🚀 Impact et mesures

### Métriques de succès
- ✅ **4/4 tests passent** : Implémentation robuste
- ✅ **Interface cohérente** : UX uniforme avec nouveau site
- ✅ **Zéro régression** : Fonctionnalités existantes préservées
- ✅ **Documentation complète** : Process TDD respecté

### Prochaines étapes possibles
1. Support authentification basique pour sitemaps protégés
2. Format sitemap TXT en plus du XML
3. Prévisualisation des URLs avant import
4. Cache des sitemaps pour réutilisation

## 📚 Références

### Standards utilisés
- **Sitemaps.org** : Format XML standard
- **TDD** : Tests écrits avant implémentation
- **DRY** : Réutilisation fonction existante

### Ressources
- Documentation sitemaps : https://sitemaps.org/
- BeautifulSoup XML parsing (utilisé dans `parse_sitemap`)
- Tests pytest avec mocking requests

---

**Développé selon méthodologie TDD - Sprint intermédiaire v1.0**  
*Fire Salamander Team - SEPTEO Digital Services* 🦎