# 🔥 Fire Snake 301 - Stratégie de Versioning

## Version actuelle : v1.0.0

## 📋 Stratégie Git Flow

### Branches principales
- **`main`** : Version stable en production (fire-snake-301.fr)
- **`develop`** : Intégration des nouvelles fonctionnalités

### Branches de travail
- **`feature/*`** : Nouvelles fonctionnalités (ex: `feature/export-pdf`)
- **`fix/*`** : Corrections de bugs (ex: `fix/duplicate-redirects`)
- **`hotfix/*`** : Corrections urgentes en production

## 🚀 Workflow de développement

### Pour une nouvelle fonctionnalité :
```bash
# 1. Partir de develop
git checkout develop
git pull origin develop

# 2. Créer une branche feature
git checkout -b feature/ma-fonctionnalite

# 3. Développer et commiter
git add .
git commit -m "Add: description de la fonctionnalité"

# 4. Pousser et créer une PR vers develop
git push origin feature/ma-fonctionnalite
```

### Pour un déploiement en production :
```bash
# 1. Merger develop dans main
git checkout main
git merge develop

# 2. Créer un nouveau tag
git tag -a v1.1.0 -m "Version 1.1.0: Description"
git push origin main --tags

# 3. Sur le serveur
cd /home/ubuntu/fire-snake-301
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📊 Semantic Versioning

Format : **vMAJOR.MINOR.PATCH**

- **MAJOR** : Changements incompatibles avec les versions précédentes
- **MINOR** : Nouvelles fonctionnalités compatibles
- **PATCH** : Corrections de bugs

### Exemples :
- v1.0.0 → v1.1.0 : Ajout export PDF
- v1.1.0 → v1.1.1 : Fix bug doublons
- v1.1.1 → v2.0.0 : Refonte complète de l'interface

## 🔄 Commandes utiles

```bash
# Voir les tags
git tag -l

# Voir les branches
git branch -a

# Retourner à une version spécifique
git checkout v1.0.0

# Voir l'historique
git log --oneline --graph --all
```