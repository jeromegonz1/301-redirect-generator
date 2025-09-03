# SCRAPING_STRATEGY.md

## 🎯 Objectif

Proposer une option par défaut permettant de **scraper automatiquement** les URLs internes de deux sites (ancien et nouveau), sans intervention technique.

## ✅ Ce que fait le scraping

- Explore tous les liens internes `<a href="...">`
- Nettoie et normalise les URLs
- Ne suit pas les liens externes ou assets
- Ignore les doublons
- Limite le crawl à un maximum de 200 pages par site
- Utilise un `User-Agent` dédié : `301-Redirect-Bot`

## 🔐 Accès préprod / privé

- Le scraping doit pouvoir fonctionner même sur des préproductions privées
- Solutions acceptées :
  - Header `User-Agent: 301-Redirect-Bot`
  - Authentification Basic HTTP
  - Token ou clé d'accès
  - Tunnel (ngrok, Cloudflare Tunnel)

## 🧠 Résumé

- Le scraping est le mode par défaut
- L'utilisateur peut le désactiver si besoin
- Le système doit automatiquement détecter et récupérer les URLs internes
- Si le site est inaccessible, fallback vers input manuel