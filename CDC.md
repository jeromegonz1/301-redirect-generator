# Cahier des Charges – 301 Redirect Generator

## 1. Objectif du projet

Développer une application ultra-simple permettant à des utilisateurs non techniques (chefs de projet, intégrateurs, SEO) de générer automatiquement un fichier `.htaccess` de redirections 301, à partir de deux listes d’URLs issues d’une refonte de site (ancien site ➝ nouveau site).

🎯 **L’utilisateur ne doit rien faire d'autre que :**
- Copier-coller deux listes d’URLs (anciennes / nouvelles)
- Cliquer sur un bouton
- Télécharger les redirections au format `.htaccess` et `.csv`

💡 **Toute la valeur ajoutée de l’outil réside dans le gain de temps et la fiabilité des redirections.**

---

## 2. Fonctionnalités V1

### 2.1. Entrées supportées

L'application doit accepter 4 formats dans chacun des deux champs "Ancien site" et "Nouveau site" :
- ✅ Sitemap XML (balises `<loc>`)
- ✅ Liste brute d’URLs (1 par ligne)
- ✅ CSV copié depuis Excel/Google Sheets (2 colonnes : ancienne, nouvelle)

### 🔄 Scraping automatique (par défaut)
L'utilisateur peut simplement entrer deux URLs racines (ancien site et nouveau site) :
- L'outil explore automatiquement les liens internes (jusqu'à 200 pages)
- Le scraping se fait en profondeur, avec respect des domaines
- Ancienne URL = complète, Nouvelle URL = relative
- Le scraping est le mode d'entrée par défaut, mais peut être désactivé

### 2.2. Traitement

- Normaliser les URLs :
  - Suppression de `www.`, trailing slashes `/`, `?` ou `#`
  - Suppression du protocole dans la partie relative (`/url`)
- Matching **ligne par ligne** (index 0 = index 0, etc.)
- Générer deux fichiers :
  - `.htaccess` :
    ```
    Redirect 301 https://ancien-site.com/page /nouvelle-url
    ```
  - `.csv` :
    ```
    OLD_FULL_URL, OLD_PATH, NEW_FULL_URL, NEW_PATH
    ```

### 2.3. Export

- ✅ Téléchargement du fichier `.htaccess` prêt à être intégré au serveur
- ✅ Téléchargement du fichier `.csv` pour audit / vérification manuelle

---

## 3. Interface utilisateur

### UX 100% simplifiée (No-Brainer)

L’utilisateur ne doit **pas réfléchir** :
- Aucun réglage, filtre ou champ technique
- Un seul écran, trois zones :
  - Zone de saisie : ancienne liste
  - Zone de saisie : nouvelle liste
  - Boutons : Générer + Télécharger

### Éléments d’UI
- ✅ Deux zones de texte pour copier-coller les URLs
- ✅ Bouton "Générer redirections"
- ✅ Affichage du contenu `.htaccess` dans une zone scrollable
- ✅ Bouton "Télécharger .htaccess"
- ✅ Bouton "Télécharger CSV"
- ✅ Message en cas d’erreur ou de mismatch de lignes

---

## 4. Contraintes techniques

- ❌ **INTERDIT de hardcoder une URL** (ni domaine, ni structure)
- ✅ **Méthode TDD obligatoire** : chaque feature doit être testée avec Pytest
- ✅ Utilisation de GitHub pour le versioning
- ✅ Compatible Replit en développement
- ✅ Déploiement prévu sur Streamlit Cloud, Railway, ou autre hébergement léger

---

## 5. Stack recommandée

| Élément | Choix |
|--------|-------|
| Langage | Python 3.10+ |
| UI | Streamlit |
| Tests | Pytest |
| Parsing | `re`, `csv`, `xml.etree.ElementTree` |
| Export fichiers | `pathlib`, `csv`, `open()` |
| Déploiement | Replit (dev), Streamlit Cloud (prod)

---

## 6. Roadmap (V2+)

| Fonction | Statut |
|----------|--------|
| Matching intelligent (Levenshtein, GPT) | 🔜 |
| Interface correction manuelle des correspondances | 🔜 |
| Support multi-domaines | 🔜 |
| Détection des 404 HTTP live | 🔜 |
