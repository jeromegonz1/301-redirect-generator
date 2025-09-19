# Gestion du fichier .env en production

## 🔒 Protection du fichier .env

Le fichier `.env` contient des informations sensibles (clé API OpenAI) et **NE DOIT JAMAIS** être commité dans git.

### Mesures de protection en place :

1. **`.gitignore`** : Le fichier `.env` est exclu de git
2. **Script de déploiement** : `scripts/deploy-production.sh` préserve automatiquement le `.env` lors des mises à jour
3. **Backup automatique** : Une sauvegarde horodatée est créée à chaque déploiement

## 📝 Configuration initiale sur un nouveau serveur

```bash
# 1. Cloner le projet
git clone https://github.com/votre-repo/fire-snake-301.git
cd fire-snake-301

# 2. Copier le template
cp .env.example .env

# 3. Éditer avec vos vraies valeurs
nano .env
# Ajouter votre clé OpenAI : OPENAI_API_KEY=sk-proj-xxxxx

# 4. Sécuriser le fichier
chmod 600 .env
```

## 🚀 Mise à jour en production

**TOUJOURS** utiliser le script de déploiement :

```bash
cd /home/ubuntu/fire-snake-301
./scripts/deploy-production.sh
```

Ce script :
- ✅ Sauvegarde le `.env` actuel
- ✅ Pull les dernières modifications depuis git
- ✅ Restaure le `.env` sauvegardé
- ✅ Reconstruit les conteneurs Docker
- ✅ Préserve vos configurations locales

## ⚠️ IMPORTANT

- **NE JAMAIS** faire `git add .env`
- **NE JAMAIS** écraser le `.env` en production avec celui du développement
- **TOUJOURS** utiliser le script de déploiement pour les mises à jour
- **GARDER** les backups `.env.backup.*` pendant au moins 30 jours

## 🔑 Rotation des clés API

Si vous devez changer la clé OpenAI :

```bash
# Sur le serveur de production
nano .env
# Modifier OPENAI_API_KEY=nouvelle-cle

# Redémarrer les conteneurs
docker-compose -f docker-compose.prod.yml restart
```

## 📊 Vérification

Pour vérifier que la clé est bien chargée :

```bash
docker exec fire-snake-301-app env | grep OPENAI
```

## 🆘 En cas de problème

Si le `.env` est accidentellement supprimé ou corrompu :

```bash
# Lister les backups disponibles
ls -la .env.backup.*

# Restaurer le plus récent
cp .env.backup.20240919_143022 .env

# Redémarrer
docker-compose -f docker-compose.prod.yml restart
```