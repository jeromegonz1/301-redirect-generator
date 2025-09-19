#!/bin/bash

# =========================================
# Fire Snake 301 - Script de déploiement production
# Ce script préserve le fichier .env lors des mises à jour
# =========================================

set -e  # Arrêter en cas d'erreur

echo "🚀 Début du déploiement Fire Snake 301..."

# Vérifier qu'on est sur le serveur de production
if [ ! -d "/home/ubuntu/fire-snake-301" ]; then
    echo "❌ Erreur: Ce script doit être exécuté sur le serveur de production"
    exit 1
fi

cd /home/ubuntu/fire-snake-301

# 1. Sauvegarder le .env actuel si il existe
if [ -f ".env" ]; then
    echo "💾 Sauvegarde du fichier .env existant..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# 2. Sauvegarder aussi le nginx/conf.d si modifié localement
if [ -f "nginx/conf.d/fire-snake-301.conf" ]; then
    echo "💾 Sauvegarde de la config nginx..."
    cp nginx/conf.d/fire-snake-301.conf nginx/conf.d/fire-snake-301.conf.backup
fi

# 3. Récupérer les dernières modifications et checkout tag v1.2.0
echo "📥 Récupération des dernières modifications..."
git fetch origin
git checkout v1.2.0

# 4. Restaurer le fichier .env
if [ -f ".env.backup."* ]; then
    echo "♻️ Restauration du fichier .env..."
    cp .env.backup.$(ls -t .env.backup.* | head -1 | cut -d. -f3-) .env
fi

# 5. Restaurer la config nginx si elle avait été sauvegardée
if [ -f "nginx/conf.d/fire-snake-301.conf.backup" ]; then
    echo "♻️ Restauration de la config nginx..."
    cp nginx/conf.d/fire-snake-301.conf.backup nginx/conf.d/fire-snake-301.conf
fi

# 6. Reconstruire et redémarrer les conteneurs
echo "🔨 Reconstruction des conteneurs Docker..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 7. Nettoyer les vieilles images Docker
echo "🧹 Nettoyage des images Docker inutilisées..."
docker system prune -f

# 8. Afficher le statut
echo ""
echo "✅ Déploiement terminé !"
echo ""
docker ps | grep fire-snake
echo ""
echo "📊 Status des conteneurs:"
docker-compose -f docker-compose.prod.yml ps

# 9. Rappel important
echo ""
echo "⚠️  RAPPEL: Le fichier .env a été préservé"
echo "    Si vous devez modifier la clé OpenAI ou d'autres variables,"
echo "    éditez directement le fichier .env sur le serveur"
echo ""
echo "🌐 Application disponible sur: https://fire-snake-301.fr"