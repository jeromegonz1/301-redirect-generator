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
- ✅ Scraping intelligent avec crawling jusqu'à 1000 pages
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

# 🚀 SPRINT 2 — Matching IA + Multilingue

*Documentation complète : [docs/SPRINT_2_README.md](docs/SPRINT_2_README.md)*

## 🔄 US009 – Matching IA Sémantique

**Titre** : US009 - Matching IA sémantique avec GPT-3.5-turbo

**En tant que** chef de projet digital,  
**je veux** que l'outil associe chaque ancienne URL à la nouvelle URL la plus proche sémantiquement,  
**afin de** gagner du temps en cas de structure différente.

### 🎯 Critères d'acceptation
- [ ] Utilisation de GPT-3.5-turbo pour le matching sémantique
- [ ] Score de confidence pour chaque correspondance (0.0 à 1.0)
- [ ] Chunking pour traiter 1000+ URLs (50 URLs par batch)
- [ ] Taux de matching > 80% avec confidence > 0.7

📄 **Documentation complète :** [docs/user_stories/US009.md](docs/user_stories/US009.md)

---

## 🔄 US010 – Interface de Validation Humaine

**Titre** : US010 - Interface de validation des suggestions IA

**En tant que** chef de projet digital,  
**je veux** pouvoir relire et valider les correspondances IA proposées,  
**afin d'** éviter des erreurs et garder le contrôle.

### 🎯 Critères d'acceptation
- [ ] Tableau interactif avec correspondances suggérées
- [ ] Possibilité d'éditer chaque correspondance manuellement
- [ ] Code couleur basé sur le score de confidence
- [ ] Filtres par confidence et statut de validation

📄 **Documentation complète :** [docs/user_stories/US010.md](docs/user_stories/US010.md)

---

## 🔄 US011 – Détection Automatique des Langues

**Titre** : US011 - Détection automatique des langues dans les URLs

**En tant que** responsable SEO multilingue,  
**je veux** que l'outil détecte automatiquement la langue des URLs,  
**afin que** le matching se fasse uniquement entre langues identiques.

### 🎯 Critères d'acceptation
- [ ] Reconnaissance des patterns linguistiques (`/fr/`, `/en/`, etc.)
- [ ] Support des sous-domaines multilingues
- [ ] Répartition visuelle des URLs par langue
- [ ] Langue par défaut configurable

📄 **Documentation complète :** [docs/user_stories/US011.md](docs/user_stories/US011.md)

---

## 🔄 US012 – Matching Cloisonné par Langue

**Titre** : US012 - Matching uniquement entre langues identiques

**En tant que** responsable SEO multilingue,  
**je veux** que le matching se fasse uniquement à l'intérieur d'un même groupe de langue,  
**afin d'** éviter les redirections inter-langues incorrectes.

### 🎯 Critères d'acceptation
- [ ] Cloisonnement strict : FR→FR, EN→EN uniquement
- [ ] Interface avec onglets par langue
- [ ] Statistiques séparées par groupe linguistique
- [ ] Gestion des déséquilibres numériques

📄 **Documentation complète :** [docs/user_stories/US012.md](docs/user_stories/US012.md)

---

## 🔄 US013 – Fallback 302 vers la Home FR

**Titre** : US013 - Redirections temporaires pour langues non migrées

**En tant que** responsable SEO multilingue,  
**je veux** que les URLs des langues absentes soient redirigées en 302 vers la home FR,  
**afin de** préserver l'UX en attendant la migration complète.

### 🎯 Critères d'acceptation
- [ ] Détection automatique des langues manquantes
- [ ] Génération de redirections temporaires (302)
- [ ] Cible configurable (par défaut `/fr/`)
- [ ] Une seule redirection par langue manquante

📄 **Documentation complète :** [docs/user_stories/US013.md](docs/user_stories/US013.md)

---

## 🔄 US014 – Prompt Contextuel du Chef de Projet

**Titre** : US014 - Context métier pour améliorer le matching IA

**En tant que** chef de projet digital,  
**je veux** pouvoir transmettre un prompt personnalisé à l'IA,  
**afin d'** obtenir un matching plus pertinent et métier-aware.

### 🎯 Critères d'acceptation
- [ ] Zone de texte pour instructions métier (500+ caractères)
- [ ] Injection du contexte dans le prompt GPT
- [ ] Templates pré-remplis pour cas courants
- [ ] Amélioration de +20% de la qualité du matching

📄 **Documentation complète :** [docs/user_stories/US014.md](docs/user_stories/US014.md)

---

## 🗺️ Suivi & gestion projet

### État des User Stories

#### 🎯 Sprint 1 (Terminé)
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

#### 🚀 Sprint 2 (En cours)
| US | Titre | Statut | Documentation |
|----|-------|--------|---------------|
| US009 | Matching IA sémantique | 🔄 À développer | [Voir doc](docs/user_stories/US009.md) |
| US010 | Interface validation humaine | 🔄 À développer | [Voir doc](docs/user_stories/US010.md) |
| US011 | Détection automatique langues | 🔄 À développer | [Voir doc](docs/user_stories/US011.md) |
| US012 | Matching cloisonné par langue | 🔄 À développer | [Voir doc](docs/user_stories/US012.md) |
| US013 | Fallback 302 vers home FR | 🔄 À développer | [Voir doc](docs/user_stories/US013.md) |
| US014 | Prompt contextuel chef projet | 🔄 À développer | [Voir doc](docs/user_stories/US014.md) |

---

## 🔒 Contraintes globales

- ❌ **Aucune URL codée en dur** (tout doit venir des inputs utilisateur)
- ✅ **Développement en TDD** systématique
- ✅ **Interface utilisable** par un non-technicien
- ✅ **Output 100% exploitable** sur serveur Apache

---

### 📊 Métriques du projet

#### Sprint 1 (Terminé)
- **User Stories Sprint 1 :** 8/8 (100%)
- **Tests automatisés :** 24 tests (9 generator + 15 scraper)
- **Version actuelle :** v3.0 avec parsing sitemap

#### Sprint 2 (En cours)
- **User Stories Sprint 2 :** 0/6 (0%)
- **Objectif :** Matching IA + Gestion multilingue
- **Version cible :** v4.0 avec GPT-3.5-turbo

### 🎯 Roadmap

- ✅ **Sprint 1** : Scraping + Parsing (Terminé)
- 🔄 **Sprint 2** : IA + Multilingue (En cours)
- 🔮 **Sprint 3** : Optimisations + UI/UX avancé

### 📚 Documentation Sprint 2

- [📋 Sprint 2 README](docs/SPRINT_2_README.md)
- [🤖 Stratégie Matching IA](docs/AI_MATCHING_STRATEGY.md)
- [🌍 Gestion Multilingue](docs/LANGUAGE_HANDLING.md)

---

## ✅ US009 – Fallback intelligent en 302

**Titre** : US009 - Fallback intelligent en 302

**En tant que** chef de projet SEO,  
**je veux** que les URLs de l'ancien site qui n'ont pas de correspondance sur le nouveau  
soient redirigées temporairement (302) vers la page d'accueil de leur langue,  
**afin de** ne pas générer d'erreur 404, tout en me laissant le temps de retraiter manuellement ces cas.

### 🎯 Critères d'acceptation
- ✅ Redirection `302` générée automatiquement pour les URLs sans match IA
- ✅ La redirection cible est `/fr/`, `/en/`, `/de/` selon le prefixe de l'URL source
- ✅ Option dans l'interface : `Activer fallback automatique 302`
- ✅ Fichier `.htaccess` annoté : `# fallback temporaire à retraiter`
- ✅ Export CSV des URLs concernées pour retraitement manuel
- ✅ Détection automatique des langues dans les URLs (`/fr/`, `/en/`, `/de/`, etc.)
- ✅ Possibilité d'activer/désactiver cette fonctionnalité via interface
- ✅ Logging et audit des cas non résolus pour équipe SEO

### 📋 Exemple de fonctionnement

**Cas 1 - URL avec langue détectée :**
```
Ancienne URL : https://ancien-site.com/fr/page-introuvable
Aucune correspondance IA trouvée
→ Fallback généré : Redirect 302 https://ancien-site.com/fr/page-introuvable /fr/
```

**Cas 2 - Export CSV pour retraitement :**
```
old_url,target_url,language,status,comment
/fr/page-orpheline,/fr/,fr,fallback_302,À retraiter manuellement
/en/missing-article,/en/,en,fallback_302,À retraiter manuellement
```

### 🔧 Intégration technique
- Module : `fallback_302_intelligent.py`
- Tests TDD : `test_fallback_302_intelligent.py` (9 tests)
- Interface : Checkbox dans section configuration IA
- Documentation : `docs/fallback_mode.md`