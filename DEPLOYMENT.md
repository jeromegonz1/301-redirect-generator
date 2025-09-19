# 🔥🐍 Fire Snake 301 - Guide de Déploiement Production

## Prérequis
- Serveur Ubuntu 24.04 LTS
- Domaine configuré (fire-snake-301.fr)
- Clé API OpenAI

## 📋 Installation Étape par Étape

### 1. Connexion au serveur
```bash
ssh ubuntu@83.228.208.83
```

### 2. Téléchargement du script d'installation
```bash
# Télécharger le script depuis le repo
wget https://raw.githubusercontent.com/jeromegonz1/301-redirect-generator/main/scripts/server-setup.sh
chmod +x server-setup.sh
```

### 3. Configuration préalable
Modifiez l'email dans le script :
```bash
nano server-setup.sh
# Remplacez contact@fire-snake-301.fr par votre email
```

### 4. Exécution du script d'installation
```bash
./server-setup.sh
```

Le script va :
- ✅ Installer docker-compose
- ✅ Configurer le firewall
- ✅ Cloner le repository
- ✅ Créer les conteneurs Docker
- ✅ Configurer SSL avec Let's Encrypt
- ✅ Mettre en place le renouvellement automatique

### 5. Configuration de la clé OpenAI
```bash
cd /home/ubuntu/fire-snake-301
nano .env
# Ajoutez votre clé OpenAI
```

### 6. Redémarrage des services
```bash
docker-compose -f docker-compose.prod.yml restart
```

## 🔄 Mises à jour futures

Pour déployer les nouvelles versions :
```bash
cd /home/ubuntu/fire-snake-301
./scripts/quick-deploy.sh
```

## 📊 Commandes utiles

### Voir les logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Statut des conteneurs
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Redémarrer l'application
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Arrêter l'application
```bash
docker-compose -f docker-compose.prod.yml down
```

## 🔍 Dépannage

### Problème de certificat SSL
```bash
# Renouveler manuellement
sudo certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Conteneur qui ne démarre pas
```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs streamlit
```

### Problème de mémoire
```bash
# Nettoyer Docker
docker system prune -a
```

## 🔒 Sécurité

- Le fichier `.env` contient la clé OpenAI - ne jamais le commiter
- Les certificats SSL se renouvellent automatiquement
- Le firewall n'autorise que SSH, HTTP et HTTPS

## 📧 Support

En cas de problème, vérifiez :
1. Les logs Docker
2. L'état des conteneurs
3. La configuration nginx
4. Les certificats SSL