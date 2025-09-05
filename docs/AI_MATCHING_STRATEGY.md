# 🤖 Stratégie de Matching IA Sémantique

## 📋 Contexte

Le matching ligne-par-ligne atteint ses limites face à :
- **Déséquilibre d'URLs** : 800 anciennes vs 549 nouvelles
- **Structures différentes** : `/camping-presentation-gard` vs `/presentation`
- **Wording différent** : `mobil-home` vs `nos-locatifs`
- **Langues multiples** : FR/EN/DE à cloisonner

## 🎯 Objectif du Matching Sémantique

Utiliser GPT-3.5-turbo pour associer automatiquement chaque ancienne URL à la nouvelle URL **la plus proche sémantiquement**, en tenant compte du contexte métier fourni par le chef de projet.

## 🔧 Architecture Technique

### API utilisée
- **Modèle** : `gpt-3.5-turbo`
- **Température** : 0.1 (précision maximale)
- **Max tokens** : 4000 par requête

### Format d'entrée
```python
{
    "anciennes_urls": [
        "https://site.com/camping-presentation-gard",
        "https://site.com/mobil-home-luxe",
        "https://site.com/restaurant-gard"
    ],
    "nouvelles_urls": [
        "/presentation",
        "/nos-locatifs",
        "/restauration"
    ],
    "contexte_metier": "mobil-home devient nos locatifs, restaurant devient restauration"
}
```

### Format de sortie
```json
{
    "correspondances": [
        {
            "ancienne": "https://site.com/camping-presentation-gard",
            "nouvelle": "/presentation",
            "confidence": 0.95,
            "raison": "Correspondance évidente : présentation du camping"
        },
        {
            "ancienne": "https://site.com/mobil-home-luxe",
            "nouvelle": "/nos-locatifs",
            "confidence": 0.90,
            "raison": "Contexte métier : mobil-home → nos-locatifs"
        }
    ],
    "non_matchees": [
        "https://site.com/page-obsolete"
    ]
}
```

## 💬 Structure du Prompt GPT

### Prompt système
```
Tu es un expert en redirections 301 pour des refontes de sites web. 
Ton rôle est d'associer chaque ancienne URL à la nouvelle URL la plus pertinente sémantiquement.

Règles :
- Analyse le sens et le contenu de chaque URL
- Une ancienne URL = une seule nouvelle URL
- Confidence entre 0.0 et 1.0
- Si confidence < 0.7, marquer comme "non_matchee"
- Priorise le contexte métier fourni par le chef de projet
```

### Prompt utilisateur dynamique
```
CONTEXTE MÉTIER :
{instructions_chef_projet}

ANCIENNES URLS :
{liste_anciennes_urls}

NOUVELLES URLS :
{liste_nouvelles_urls}

LANGUE : {langue_detectee}

Associe chaque ancienne URL à la meilleure nouvelle URL en format JSON.
```

## 🧩 Méthode de Chunking

Pour gérer de gros volumes (1000+ URLs) :

### Stratégie de découpage
- **Chunk size** : 50 URLs à la fois
- **Overlap** : 5 URLs communes entre chunks
- **Parallélisation** : 3 requêtes simultanées maximum

### Gestion des erreurs
- **Retry** : 3 tentatives avec backoff exponentiel
- **Fallback** : Matching basé sur mots-clés si IA échoue
- **Timeout** : 30 secondes par chunk

## 🔍 Prompt Contextuel Métier

### Exemples d'instructions typiques
```
Le site est en FR/EN/DE. Le contenu ES n'a pas été migré.
Les sections ont changé :
- "mobil-home" → "nos locatifs"
- "blog" → "actualités" 
- "restaurant" → "restauration"

Structure éditoriale :
- Pages principales : /presentation, /hebergement, /services
- Blog : /actualites/[slug]
- Langues : /fr/, /en/, /de/
```

### Injection dans le prompt
Le contexte métier est injecté au début du prompt utilisateur pour maximiser son impact sur les décisions de l'IA.

## 📊 Métriques de Qualité

### Indicateurs à suivre
- **Taux de matching** : % d'URLs matchées avec confidence > 0.7
- **Précision humaine** : % de suggestions validées par l'utilisateur
- **Temps de traitement** : Temps moyen par URL
- **Coût API** : Coût OpenAI par matching

### Seuils de qualité
- ✅ **Excellent** : Confidence > 0.9
- ✅ **Bon** : Confidence 0.7-0.9
- ⚠️ **À vérifier** : Confidence 0.5-0.7
- ❌ **Rejeté** : Confidence < 0.5

## 🔧 Implémentation

### Module principal : `ai_mapper.py`
```python
class AIMapper:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def match_urls(self, old_urls: List[str], new_urls: List[str], 
                   contexte: str = "", langue: str = "fr") -> MatchResult:
        # Implémentation du matching IA
```

### Intégration Streamlit
- Interface de saisie du contexte métier
- Affichage des suggestions avec scores de confidence
- Validation/édition manuelle des correspondances
- Export vers .htaccess avec correspondances validées

---

*Stratégie IA développée pour SEPTEO Digital Services*
*Optimisée pour GPT-3.5-turbo et refontes multilingues*