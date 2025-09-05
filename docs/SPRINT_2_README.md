# 🚀 Sprint 2 — Matching IA + Gestion Multilingue 🌍🤖

## 📋 Contexte

Suite au succès du Sprint 1 (scraping + parsing sitemap), nous avons identifié un défi récurrent : le **déséquilibre d'URLs** et les **structures différentes** entre ancien et nouveau site. Le matching ligne-par-ligne n'est plus suffisant.

**Exemple concret :** 
- Ancien site : 800 URLs scrapées
- Nouveau site : 549 URLs dans le sitemap
- Structure différente : `/camping-presentation-gard` → `/presentation`

## 🎯 Objectifs du Sprint 2

### 🤖 Intelligence Artificielle
- **Matching sémantique** : Associer automatiquement les anciennes URLs aux nouvelles basé sur le sens
- **Prompt contextuel** : Permettre au chef de projet d'expliquer le contexte métier à l'IA
- **Validation humaine** : Interface pour relire et ajuster les suggestions IA

### 🌍 Gestion Multilingue  
- **Détection automatique** des langues (`/fr/`, `/en/`, `/de/`, etc.)
- **Matching cloisonné** : FR/FR, EN/EN uniquement
- **Fallback intelligent** : Redirection 302 vers `/fr/` pour langues non migrées

## 📦 Périmètre technique

### Nouveaux modules
- `ai_mapper.py` : Logique de matching IA avec OpenAI GPT-3.5-turbo
- `language_detector.py` : Détection et cloisonnement des langues
- Interface Streamlit enrichie avec validation humaine

### APIs externes
- **OpenAI GPT-3.5-turbo** : Matching sémantique
- Variable d'environnement : `OPENAI_API_KEY`

### Nouveaux composants UI
- ✅ Checkbox "Activer le matching IA"
- ✅ Zone de texte "Instructions du chef de projet"
- ✅ Interface de validation avec tableau éditable
- ✅ Preview des redirections avant export

## 🗂️ Documentation

| Fichier | Contenu |
|---------|---------|
| [AI_MATCHING_STRATEGY.md](AI_MATCHING_STRATEGY.md) | Stratégie technique du matching IA |
| [LANGUAGE_HANDLING.md](LANGUAGE_HANDLING.md) | Gestion multilingue et fallbacks |

## 📋 User Stories

| US | Titre | Statut |
|----|-------|--------|
| [US009](user_stories/US009.md) | Matching IA sémantique | 🔄 À développer |
| [US010](user_stories/US010.md) | Interface de validation humaine | 🔄 À développer |
| [US011](user_stories/US011.md) | Détection automatique des langues | 🔄 À développer |
| [US012](user_stories/US012.md) | Matching cloisonné par langue | 🔄 À développer |
| [US013](user_stories/US013.md) | Fallback 302 vers la home FR | 🔄 À développer |
| [US014](user_stories/US014.md) | Prompt contextuel du chef de projet | 🔄 À développer |

## 🎯 Critères de succès

- [ ] Réduction de 80% du retravail manuel sur les redirections
- [ ] Support natif des refontes multilingues
- [ ] Interface intuitive pour validation des suggestions IA
- [ ] Performance : matching de 1000 URLs en moins de 2 minutes
- [ ] Qualité : 90% de suggestions IA pertinentes

## 🔄 Prochaines étapes

1. ✅ **Phase Documentation** : Création des specs techniques
2. 🔄 **Phase Développement** : Implémentation des modules IA
3. 🔄 **Phase Test** : Validation sur cas réels multilingues
4. 🔄 **Phase Déploiement** : Intégration dans l'application principale

---

*Développé pour SEPTEO Digital Services — Fire Salamander Team* 🦎
*Sprint 2 : Intelligence Artificielle et Multilingue*