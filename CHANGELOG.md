# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-19

### 🎉 Sprint 2.0 - Smart Crawler & Universal Input

### ✨ Ajouté
- **SmartInputParser** : Parseur universel avec auto-détection de format
  - Support XML Sitemap avec namespaces
  - Support JSON Array 
  - Support CSV avec headers
  - Support liste d'URLs simple (texte)
  - Nettoyage automatique des espaces et caractères parasites
- **SmartHeaders** : Gestion intelligente des headers HTTP
  - Rotation automatique des User-Agents (7 agents différents)
  - Headers spécialisés par type de contenu (XML, JSON, HTML)
  - Headers adaptatifs par domaine (Cloudflare, WordPress)
  - Détection automatique des réponses de blocage
- **SmartRetry** : Mécanisme de retry avec backoff exponentiel
  - Retry automatique sur erreurs réseau (TimeoutError, ConnectionError)
  - Backoff exponentiel avec jitter anti-thundering herd
  - Support du header Retry-After pour rate limiting (429)
  - Statistiques détaillées des retries
- **Interface "Input Universel"** dans l'UI
  - Option disponible pour ancien ET nouveau site
  - Section d'exemples dépliable avec code samples
  - Feedback intelligent selon le format détecté
  - Help tooltips avec détails des formats supportés

### 🔧 Amélioré
- **Scraper.py** intégré avec composants intelligents
  - WebScraper utilise maintenant SmartHeaders et SmartRetry
  - Fonction parse_sitemap renforcée avec retry automatique
  - Headers XML spécialisés pour les sitemaps
- **Interface utilisateur** 
  - Correction message d'erreur OpenAI (.env au lieu de Replit)
  - app.py comme point d'entrée unique à la racine
  - Sidebar avec vérification de clé API
  - Terminologie cohérente (plus de "Sprint 2")

### 🏗️ Technique
- Tests TDD complets pour tous les nouveaux composants
- Configuration centralisée sans hardcoding
- Imports optimisés avec préfixe src/
- Architecture modulaire et réutilisable

### 📊 Métriques
- Support de 4 formats d'input différents
- 7 User-Agents en rotation
- Retry jusqu'à 60s de délai maximum
- Performance: < 2ms pour parsing XML typique

---

## [1.1.1] - 2025-09-10

### 🐛 Corrigé
- Gestion des listes imbriquées dans current_old_urls pour éviter TypeError
- Protection contre les erreurs de type dans la détection de domaine

---

## [1.1.0] - 2025-09-10

### ✨ Ajouté
- Filtrage automatique des médias (images, PDFs, etc.)
- Nettoyage intelligent des URLs (suppression query params, normalisation)
- Affichage de la version dans l'interface
- Protection des variables d'environnement
- Interface IA sémantique avec GPT-3.5-turbo
- Support multilangue automatique

### 🔧 Amélioré
- Performance du scraping
- Interface utilisateur modernisée
- Gestion d'erreurs renforcée

---

## [1.0.0] - 2025-08-15

### ✨ Version initiale
- Générateur de redirections 301 basique
- Interface Streamlit simple
- Support scraping et sitemaps XML
- Export .htaccess et CSV