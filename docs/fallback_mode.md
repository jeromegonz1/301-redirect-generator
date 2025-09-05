# Fallback 302 pour les URLs non matchées

Ce mode permet de gérer intelligemment les cas où une URL de l'ancien site n'a pas d'équivalent sémantique sur le nouveau site (matching IA non concluant ou URL manquante).

## Fonctionnement

- Une redirection **302 temporaire** est générée vers la **page d'accueil de la langue correspondante**
- Le code **302** évite d'indexer une mauvaise URL, contrairement à un 301
- Toutes les redirections fallback sont **loggées et exportables**

## Exemple

Ancienne URL : `https://www.monsite.com/de/angebot-alt/`  
Aucune correspondance trouvée par IA  
➡️ Fallback : `Redirect 302 https://www.monsite.com/de/angebot-alt/ /de/`

## UI

- Case à cocher dans l'interface : `✅ Activer fallback 302 automatique`
- Export CSV des fallback générés

## Retraitement

L'équipe SEO peut retraiter les URLs à partir du CSV, puis regénérer un `.htaccess` propre en supprimant les 302 manuels.

## Détection automatique des langues

Le système détecte automatiquement la langue dans l'URL grâce aux patterns :
- `/fr/` → Redirection vers `/fr/`
- `/en/` → Redirection vers `/en/`
- `/de/` → Redirection vers `/de/`
- `/es/` → Redirection vers `/es/`
- `/it/` → Redirection vers `/it/`
- `/nl/` → Redirection vers `/nl/`

## Format .htaccess généré

```apache
# Redirections 301 normales (trouvées par IA)
Redirect 301 /fr/page-trouvee /fr/nouvelle-page

# Fallback temporaire - à retraiter manuellement
Redirect 302 /fr/page-orpheline /fr/

# Fallback temporaire - à retraiter manuellement  
Redirect 302 /en/missing-article /en/
```

## Export CSV pour retraitement

Le CSV généré contient :
- `old_url` : URL d'origine
- `target_url` : URL de redirection (/langue/)
- `language` : Code langue détecté
- `status` : "fallback_302"
- `comment` : "À retraiter manuellement"

## Avantages

1. **Aucune erreur 404** : Toutes les URLs redirigent quelque part
2. **SEO préservé** : Les 302 n'impactent pas l'indexation définitive
3. **Retraitement facilité** : CSV avec toutes les URLs à revoir
4. **Flexibilité** : Peut être activé/désactivé selon les besoins