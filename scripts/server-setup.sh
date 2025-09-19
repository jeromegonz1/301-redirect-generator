#!/bin/bash
# Fire Snake 301 - Server Setup Script
# Pour Ubuntu 24.04 LTS

set -euo pipefail

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="fire-snake-301.fr"
EMAIL="contact@fire-snake-301.fr"  # À remplacer par ton email
REPO_URL="https://github.com/jeromegonz1/301-redirect-generator.git"
APP_DIR="/home/ubuntu/fire-snake-301"

echo -e "${BLUE}🔥🐍 Fire Snake 301 - Installation Serveur${NC}"
echo "=================================================="
echo "Serveur: Ubuntu 24.04 LTS"
echo "Domaine: $DOMAIN"
echo "IP: 83.228.208.83"
echo ""

# Fonction pour afficher les statuts
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Mise à jour système
print_status "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# 2. Installation de docker-compose
print_status "Installation de docker-compose..."
sudo apt install -y docker-compose

# 3. Installation des outils nécessaires
print_status "Installation des outils système..."
sudo apt install -y git curl wget nginx certbot python3-certbot-nginx

# 4. Configuration du firewall
print_status "Configuration du firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 5. Création du répertoire de l'application
print_status "Création du répertoire de l'application..."
if [ -d "$APP_DIR" ]; then
    print_warning "Le répertoire $APP_DIR existe déjà"
    read -p "Voulez-vous le supprimer et recommencer ? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf $APP_DIR
    else
        print_error "Installation annulée"
        exit 1
    fi
fi

# 6. Clonage du repository
print_status "Clonage du repository..."
git clone $REPO_URL $APP_DIR
cd $APP_DIR

# 7. Configuration de l'environnement
print_status "Configuration de l'environnement..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    print_warning "⚠️  IMPORTANT: Éditez le fichier .env avec votre clé OpenAI"
    print_warning "Commande: nano $APP_DIR/.env"
    read -p "Appuyez sur Entrée une fois le fichier .env édité avec votre clé OpenAI..."
fi

# 8. Création des répertoires nécessaires
print_status "Création des répertoires..."
mkdir -p nginx/logs outputs/gpt_cache outputs/htaccess_files

# 9. Construction et lancement des conteneurs Docker
print_status "Construction des conteneurs Docker..."
cd $APP_DIR
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d --build

# 10. Configuration SSL avec Let's Encrypt
print_status "Configuration SSL avec Let's Encrypt..."

# Arrêt temporaire de nginx pour obtenir le certificat
sudo systemctl stop nginx 2>/dev/null || true
docker-compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true

# Obtention du certificat SSL
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    print_warning "Obtention du certificat SSL pour $DOMAIN..."
    sudo certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN,www.$DOMAIN
else
    print_status "Certificat SSL déjà présent"
fi

# 11. Redémarrage des services
print_status "Redémarrage des services..."
docker-compose -f docker-compose.prod.yml restart

# 12. Configuration du renouvellement automatique SSL
print_status "Configuration du renouvellement automatique SSL..."
(crontab -l 2>/dev/null || true; echo "0 3 * * * cd $APP_DIR && docker-compose -f docker-compose.prod.yml stop nginx && certbot renew && docker-compose -f docker-compose.prod.yml start nginx") | crontab -

# 13. Vérification finale
print_status "Vérification de l'installation..."
sleep 10

# Test de santé
if docker ps | grep -q fire-snake; then
    print_status "✅ Les conteneurs Fire Snake 301 sont en cours d'exécution"
else
    print_error "❌ Les conteneurs ne sont pas démarrés"
    docker-compose -f docker-compose.prod.yml logs --tail=50
fi

# Affichage des informations finales
echo ""
echo -e "${GREEN}🎉 Installation terminée !${NC}"
echo "=================================================="
echo -e "🌐 URL: ${BLUE}https://$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "📊 Logs: cd $APP_DIR && docker-compose -f docker-compose.prod.yml logs -f"
echo "🔄 Redémarrer: cd $APP_DIR && docker-compose -f docker-compose.prod.yml restart"
echo "📦 Mettre à jour: cd $APP_DIR && git pull && docker-compose -f docker-compose.prod.yml up -d --build"
echo "🔍 Statut: cd $APP_DIR && docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${YELLOW}⚠️  N'oubliez pas de:${NC}"
echo "1. Vérifier que votre clé OpenAI est bien configurée dans .env"
echo "2. Remplacer l'email dans le script par votre vraie adresse"
echo ""