#!/bin/bash
# Fire Snake 301 - Script de déploiement rapide
# À exécuter après server-setup.sh pour les mises à jour

set -euo pipefail

APP_DIR="/home/ubuntu/fire-snake-301"
DOMAIN="fire-snake-301.fr"

echo "🔥🐍 Fire Snake 301 - Déploiement rapide"
echo "========================================="

cd $APP_DIR

# 1. Pull des dernières modifications
echo "📥 Récupération des dernières modifications..."
git pull origin main

# 2. Rebuild et restart des conteneurs
echo "🔨 Reconstruction des conteneurs..."
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Nettoyage des images inutilisées
echo "🧹 Nettoyage des anciennes images..."
docker image prune -f

# 4. Vérification
echo "✅ Vérification du déploiement..."
sleep 5
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🎉 Déploiement terminé !"
echo "🌐 https://$DOMAIN"
echo "📊 Logs: docker-compose -f docker-compose.prod.yml logs -f"