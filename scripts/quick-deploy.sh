#!/bin/bash
# Fire Snake 301 - Script de déploiement rapide
# À exécuter après server-setup.sh pour les mises à jour

set -euo pipefail

APP_DIR="/home/ubuntu/fire-snake-301"
DOMAIN="fire-snake-301.fr"

echo "🔥🐍 Fire Snake 301 - Déploiement rapide"
echo "========================================="

cd $APP_DIR

# 1. Pull des dernières modifications et checkout tag v1.2.0
echo "📥 Récupération des dernières modifications..."
git fetch origin
git checkout v1.2.0

# 2. Arrêt propre des conteneurs
echo "⏹️ Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml down -v --remove-orphans

# 3. Nettoyage préventif Docker (évite les erreurs ContainerConfig)
echo "🧹 Nettoyage Docker complet..."
docker container prune -f
docker image prune -af
docker volume prune -f
docker builder prune -af

# 4. Rebuild et restart des conteneurs
echo "🔨 Reconstruction des conteneurs..."
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

# 5. Vérification
echo "✅ Vérification du déploiement..."
sleep 5
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🎉 Déploiement terminé !"
echo "🌐 https://$DOMAIN"
echo "📊 Logs: docker-compose -f docker-compose.prod.yml logs -f"