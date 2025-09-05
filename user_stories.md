User Stories – 301 Redirect Generator
# 🦎 User Stories – 301 Redirect Generator

## 🧭 EPIC – Génération automatisée de redirections 301 entre deux sites

L'objectif de l'application est de permettre à un utilisateur non technique (chef de projet, intégrateur, SEO) de copier-coller deux listes d'URLs (avant/après refonte) pour générer automatiquement :

- Un fichier `.htaccess` prêt à déployer
- Un fichier `.csv` pour audit ou relecture

Toute la valeur ajoutée repose sur le **gain de temps**, la **simplicité d'utilisation** et la **fiabilité SEO** des redirections.

---

## ✅ US001 – Coller deux listes d'URL

**Titre** : US001 - Copier deux listes d'URL

**En tant que** utilisateur,  
**je veux** coller la liste des anciennes et des nouvelles URLs dans deux champs distincts,  
**afin que** l'outil puisse les traiter sans avoir à uploader de fichiers.

### 🎯 Critères d'acceptation
- ✅ Supporte :
  - sitemap XML (balises `<loc>`)
  - liste brute (une URL par ligne)
  - CSV collé (colonnes ancienne / nouvelle)
- ✅ Détection automatique du format
- ✅ Aucune action technique requise

---

## ✅ US002 – Générer le fichier `.htaccess`

**Titre** : US002 - Générer le fichier `.htaccess`

**En tant que** utilisateur,  
**je veux** générer automatiquement un fichier `.htaccess` contenant les redirections 301,  
**afin que** je puisse le déployer directement sur mon serveur Apache.

### 🎯 Critères d'acceptation
- ✅ Ancienne URL = **complète** (ex. `https://vieux-site.com/contact`)
- ✅ Nouvelle URL = **relative** (ex. `/nous-contacter`)
- ✅ Format :
  ```apache
  Redirect 301 https://vieux-site.com/contact /nous-contacter
  ```
- ✅ Une ligne = une redirection
- ✅ Gestion des erreurs : mismatch de ligne → alerte utilisateur

---

## ✅ US003 – Générer un fichier .csv d'audit

**Titre** : US003 - Générer un fichier .csv d'audit

**En tant que** utilisateur,  
**je veux** pouvoir télécharger un fichier .csv listant toutes les redirections,  
**afin de** les vérifier, les partager ou les corriger avant intégration.

### 🎯 Critères d'acceptation
- ✅ Fichier CSV généré en parallèle du .htaccess
- ✅ Structure :
  ```
  OLD_FULL_URL, OLD_PATH, NEW_FULL_URL, NEW_PATH
  ```
- ✅ Compatible Excel / Google Sheets

---

## ✅ US004 – Interface ultra-simple (UX No-Brainer)

**Titre** : US004 - Interface ultra-simple

**En tant que** utilisateur non technique,  
**je veux** une interface claire, directe et minimaliste,  
**afin de** générer les redirections sans effort ni connaissance technique.

### 🎯 Critères d'acceptation
- ✅ Deux zones de texte (sitemap A / sitemap B)
- ✅ Un bouton "Générer"
- ✅ Deux boutons de téléchargement : .htaccess et .csv
- ✅ Aucun menu, paramètre, ou option technique
- ✅ Zéro friction cognitive

---

## ✅ US005 – TDD & Qualité de code

**Titre** : US005 - TDD & Qualité code

**En tant que** développeur,  
**je veux** que le projet respecte les bonnes pratiques (TDD, structure claire, versioning),  
**afin de** garantir sa fiabilité, maintenabilité et réutilisabilité.

### 🎯 Critères d'acceptation
- ✅ Aucune URL codée en dur (interdiction de hardcoding)
- ✅ Tests automatisés avec Pytest
- ✅ Arborescence :
  ```
  /src/
  /tests/
  /outputs/
  ```
- ✅ Utilisation d'un Git propre + commits clairs
- ✅ CI/CD possible (ex : GitHub Actions, Replit)

---

## 📦 Livrables par US

| US | Fichier généré |
|----|----------------|
| US002 | .htaccess prêt à déployer |
| US003 | .csv pour contrôle qualité et partage |

---

## ✅ US006 – Scraping automatique (Legacy)

**Titre** : US006 - Scraping automatique des URLs

**En tant que** utilisateur,  
**je veux** pouvoir scraper automatiquement les URLs d'un site,  
**afin de** ne pas avoir à les copier manuellement.

### 🎯 Critères d'acceptation
- ✅ Scraping intelligent avec crawling jusqu'à 200 pages
- ✅ Détection automatique des liens internes
- ✅ Normalisation des URLs (suppression query strings, fragments)
- ✅ Support Basic Auth si nécessaire
- ✅ User-Agent dédié : "301-Redirect-Bot"

---

## ✅ US007 – Parsing du sitemap Yoast pour le site nouveau

**Titre** : US007 - Parser le sitemap du nouveau site en préproduction

**En tant que** utilisateur,  
**je veux** pouvoir parser le sitemap XML du nouveau site (souvent bloqué par robots.txt),  
**afin d'** extraire toutes les URLs sans scraping.

### 🎯 Critères d'acceptation
- ✅ Parsing récursif des sitemaps index Yoast
- ✅ Détection automatique des sous-sitemaps (post, page, category)
- ✅ Protection contre les boucles infinies
- ✅ Conversion en URLs relatives pour matching
- ✅ Support des sitemaps standards et Yoast SEO

📄 **Documentation complète :** [docs/user_stories/US007.md](docs/user_stories/US007.md)

---

## ✅ US008 – Campagne de test réelle

**Titre** : US008 - Test sur cas réel de refonte

**En tant que** équipe projet,  
**je veux** valider l'application sur un vrai cas de refonte,  
**afin de** m'assurer qu'elle est prête pour la production.

### 🎯 Critères d'acceptation
- ✅ Test avec ancien site : https://www.campinglescascades.com/
- ✅ Test avec nouveau site : http://72.web.thelis.es:30178/les-cascades/sitemap_index.xml
- ✅ Extraction correcte de 549 URLs du sitemap
- ✅ Génération des fichiers .htaccess et .csv fonctionnels
- ✅ Performance acceptable (< 2 min)

📄 **Documentation complète :** [docs/user_stories/US008.md](docs/user_stories/US008.md)

---

## 🗺️ Suivi & gestion projet

### État des User Stories

| US | Titre | Statut | Documentation |
|----|-------|--------|---------------|
| US001 | Coller deux listes d'URL | ✅ Terminée | - |
| US002 | Générer le fichier .htaccess | ✅ Terminée | - |
| US003 | Générer un fichier .csv | ✅ Terminée | - |
| US004 | Interface ultra-simple | ✅ Terminée | - |
| US005 | TDD & Qualité code | ✅ Terminée | - |
| US006 | Scraping automatique | ✅ Terminée | - |
| US007 | Parsing sitemap Yoast | ✅ Terminée | [Voir doc](docs/user_stories/US007.md) |
| US008 | Campagne test réelle | ✅ Terminée | [Voir doc](docs/user_stories/US008.md) |

---

## 🔒 Contraintes globales

- ❌ **Aucune URL codée en dur** (tout doit venir des inputs utilisateur)
- ✅ **Développement en TDD** systématique
- ✅ **Interface utilisable** par un non-technicien
- ✅ **Output 100% exploitable** sur serveur Apache

---

### 📊 Métriques du projet

- **Total User Stories :** 8
- **Complétées :** 8/8 (100%)
- **Tests automatisés :** 24 tests (9 generator + 15 scraper)
- **Couverture fonctionnelle :** 100%
- **Version actuelle :** v3.0 avec parsing sitemap

### 🚀 Prochaines évolutions potentielles

- Matching intelligent (fuzzy matching)
- Filtrage des URLs media
- Gestion spécifique du multilingue
- Interface de preview avant génération
- Export vers d'autres formats (nginx, etc.)