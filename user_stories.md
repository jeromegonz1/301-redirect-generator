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

## 🗺️ Suivi & gestion projet

Les User Stories sont suivies dans le Kanban GitHub Project :  
👉 **Roadmap 301 Generator**

---

## 🔒 Contraintes globales

- ❌ **Aucune URL codée en dur** (tout doit venir des inputs utilisateur)
- ✅ **Développement en TDD** systématique
- ✅ **Interface utilisable** par un non-technicien
- ✅ **Output 100% exploitable** sur serveur Apache

---

### ✅ Et maintenant :

1. Crée un fichier dans ton repo : `user_stories.md`
2. Colle ce contenu
3. Commit :
   ```bash
   git add user_stories.md
   git commit -m "docs: ajout des User Stories complètes du projet"
   git push origin main
   ```