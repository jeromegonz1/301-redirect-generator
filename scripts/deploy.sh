#!/bin/bash
# Fire Snake 301 - Production Deployment Script
# Philosophy: TDD, No hardcoding, Scalable

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="fire-snake-301.fr"
EMAIL="your-email@example.com"  # Change this to your email
REPO_URL="https://github.com/jeromegonz1/301-redirect-generator.git"
APP_DIR="/opt/fire-snake-301"

echo -e "${BLUE}🔥🐍 Fire Snake 301 - Production Deployment${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y curl wget git nginx certbot python3-certbot-nginx

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    print_status "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    print_status "Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Copy production environment file
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    print_warning "Please edit .env file with your OpenAI API key:"
    print_warning "nano .env"
    read -p "Press Enter after editing .env file..."
fi

# Create required directories
print_status "Creating required directories..."
mkdir -p nginx/logs outputs/gpt_cache outputs/htaccess_files

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build and start containers
print_status "Building and starting Fire Snake 301..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 30

# Check container status
print_status "Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Setup SSL with Certbot
setup_ssl() {
    print_status "Setting up SSL certificate with Let's Encrypt..."
    
    # Stop nginx container temporarily
    docker-compose -f docker-compose.prod.yml stop nginx
    
    # Get SSL certificate
    sudo certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    # Start nginx container
    docker-compose -f docker-compose.prod.yml start nginx
}

# Check if SSL certificate exists
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    print_warning "SSL certificate not found. Setting up Let's Encrypt..."
    read -p "Enter your email for Let's Encrypt: " EMAIL
    sed -i "s/your-email@example.com/$EMAIL/g" scripts/deploy.sh
    setup_ssl
else
    print_status "SSL certificate already exists"
fi

# Setup automatic SSL renewal
print_status "Setting up automatic SSL renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f $APP_DIR/docker-compose.prod.yml restart nginx") | crontab -

# Firewall configuration
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

# Final health check
print_status "Performing final health check..."
sleep 10

if curl -f -s https://$DOMAIN/_stcore/health > /dev/null; then
    print_status "✅ Fire Snake 301 is running successfully!"
    print_status "🌐 Visit: https://$DOMAIN"
else
    print_warning "Health check failed. Checking logs..."
    docker-compose -f docker-compose.prod.yml logs --tail=50
fi

echo ""
echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo "=================================================="
echo -e "🌐 Fire Snake 301: ${BLUE}https://$DOMAIN${NC}"
echo -e "📊 Logs: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "🔄 Restart: ${YELLOW}docker-compose -f docker-compose.prod.yml restart${NC}"
echo -e "⬇️  Update: ${YELLOW}git pull && docker-compose -f docker-compose.prod.yml up -d --build${NC}"
echo ""