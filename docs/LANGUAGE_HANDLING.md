# 🌍 Gestion Multilingue et Détection des Langues

## 📋 Contexte

Les refontes de sites multilingues présentent des défis spécifiques :
- **Langues déséquilibrées** : FR complet, EN partiel, DE absent
- **Structures différentes** : `/fr/contact` vs `/contact-fr`
- **Contenus non migrés** : Pages ES existantes mais non reprises
- **SEO critique** : Éviter les erreurs 404 sur les langues

## 🎯 Objectifs

1. **Détection automatique** des langues dans les URLs
2. **Matching cloisonné** : FR/FR, EN/EN uniquement  
3. **Fallback intelligent** pour langues non migrées
4. **Préservation SEO** avec redirections 302 temporaires

## 🔍 Méthode de Détection des Langues

### Patterns de détection
```python
LANGUAGE_PATTERNS = {
    'fr': [r'^/fr/', r'/(fr)$', r'-fr[./]', r'\.fr/'],
    'en': [r'^/en/', r'/(en)$', r'-en[./]', r'\.en/'],
    'de': [r'^/de/', r'/(de)$', r'-de[./]', r'\.de/'],
    'es': [r'^/es/', r'/(es)$', r'-es[./]', r'\.es/'],
    'it': [r'^/it/', r'/(it)$', r'-it[./]', r'\.it/'],
    'nl': [r'^/nl/', r'/(nl)$', r'-nl[./]', r'\.nl/']
}
```

### Exemples de détection
| URL | Langue détectée | Méthode |
|-----|----------------|---------|
| `/fr/contact` | FR | Préfixe standard |
| `/contact-en` | EN | Suffixe |
| `subdomain.de/page` | DE | Sous-domaine |
| `/contact` | FR (défaut) | Langue par défaut |

### Fallback par défaut
Si aucun pattern ne correspond → **Langue = FR (défaut)**

## 🏗️ Cloisonnement Logique

### Principe de base
**Matching uniquement entre URLs de même langue**

```
Ancien site (800 URLs)    Nouveau site (549 URLs)
├── FR: 400 URLs     ←→   ├── FR: 300 URLs
├── EN: 200 URLs     ←→   ├── EN: 150 URLs  
├── DE: 100 URLs     ←→   ├── DE: 99 URLs
└── ES: 100 URLs     ←→   └── ES: 0 URLs (non migré)
```

### Algorithme de cloisonnement
```python
def group_by_language(urls: List[str]) -> Dict[str, List[str]]:
    groups = defaultdict(list)
    for url in urls:
        lang = detect_language(url)
        groups[lang].append(url)
    return groups
```

## ⚠️ Gestion des Déséquilibres

### Cas typiques
1. **Langue complètement absente** : ES sur ancien, pas sur nouveau
2. **Déséquilibre numérique** : 200 EN anciennes, 50 EN nouvelles
3. **Structure différente** : Langues en préfixe vs suffixe

### Stratégies de résolution

#### 1. Langue absente → Fallback 302
```apache
# Toutes les pages ES → Redirection temporaire vers FR
Redirect 302 /es/contact /fr/
Redirect 302 /es/services /fr/
Redirect 302 /es/blog/article /fr/
```

#### 2. Déséquilibre numérique → Matching IA
```
EN ancien : 200 URLs
EN nouveau : 50 URLs
→ IA matche les 50 plus pertinentes
→ 150 restantes → Redirection vers /en/ (home EN)
```

#### 3. Structure différente → Normalisation
```
Ancien : /contact-en, /services-en
Nouveau : /en/contact, /en/services
→ Normalisation avant matching
```

## 🔄 Types de Redirections

### 301 - Redirection permanente
Pour correspondances exactes entre langues identiques :
```apache
Redirect 301 /fr/ancien-contact /fr/contact
Redirect 301 /en/old-services /en/services
```

### 302 - Redirection temporaire  
Pour langues non migrées ou correspondances imparfaites :
```apache
# Langue non migrée
Redirect 302 /es/cualquier-pagina /fr/

# Correspondance imparfaite (EN manquant)
Redirect 302 /en/page-specifique /en/
```

## 🔧 Implémentation Technique

### Module : `language_detector.py`
```python
class LanguageDetector:
    def detect(self, url: str) -> str:
        """Détecte la langue d'une URL"""
    
    def group_by_language(self, urls: List[str]) -> Dict[str, List[str]]:
        """Groupe les URLs par langue"""
    
    def generate_fallbacks(self, missing_langs: List[str]) -> List[str]:
        """Génère les redirections 302 pour langues manquantes"""
```

### Interface Streamlit

#### Affichage des groupes de langues
```
🌍 Répartition par langue :

Ancien site :
├── FR: 400 URLs (✅ 300 nouvelles URLs disponibles)
├── EN: 200 URLs (✅ 150 nouvelles URLs disponibles) 
├── DE: 100 URLs (✅ 99 nouvelles URLs disponibles)
└── ES: 100 URLs (❌ 0 nouvelles URLs → Fallback FR)
```

#### Options de configuration
- ☑️ **Langue par défaut** : FR
- ☑️ **Fallback pour langues manquantes** : 302 vers home FR
- ☑️ **Matching strict** : Seulement entre langues identiques

## 📊 Métriques par Langue

### Tableau de bord
| Langue | Anciennes | Nouvelles | Matchées | Fallbacks | Taux |
|--------|-----------|-----------|----------|-----------|------|
| FR     | 400       | 300       | 300      | 100       | 75%  |
| EN     | 200       | 150       | 150      | 50        | 75%  |
| DE     | 100       | 99        | 99       | 1         | 99%  |
| ES     | 100       | 0         | 0        | 100       | 0%   |

### Alertes automatiques
- 🟡 **Attention** : Langue avec < 50% de matching
- 🔴 **Critique** : Langue complètement absente du nouveau site

## 🎯 Exemples Concrets

### Redirection parfaite (301)
```
/fr/camping-presentation → /fr/presentation
/en/mobile-home-luxury → /en/luxury-rentals
/de/restaurant-gard → /de/gastronomie
```

### Redirection de fallback (302)
```
/es/camping-presentacion → 302 /fr/
/es/restaurante → 302 /fr/
/it/pagina-qualsiasi → 302 /fr/
```

---

*Gestion multilingue développée pour SEPTEO Digital Services*
*Optimisée pour refontes complexes avec déséquilibres de langues*