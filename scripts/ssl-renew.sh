#!/bin/bash
# Fire Snake 301 - SSL Certificate Renewal Script

set -euo pipefail

APP_DIR="/opt/fire-snake-301"
DOMAIN="fire-snake-301.fr"

echo "🔐 Renewing SSL certificates for Fire Snake 301..."

# Navigate to app directory
cd $APP_DIR

# Stop nginx container
docker-compose -f docker-compose.prod.yml stop nginx

# Renew certificates
certbot renew --standalone --quiet

# Start nginx container
docker-compose -f docker-compose.prod.yml start nginx

# Verify renewal
if curl -f -s https://$DOMAIN/_stcore/health > /dev/null; then
    echo "✅ SSL renewal successful - Fire Snake 301 is accessible"
else
    echo "❌ SSL renewal failed - checking logs"
    docker-compose -f docker-compose.prod.yml logs nginx --tail=20
    exit 1
fi