# 🔥🐍 Fire Snake 301 - Production Deployment Guide

## 📋 Quick Start

```bash
# On your VPS (Ubuntu)
git clone https://github.com/jeromegonz1/301-redirect-generator.git /opt/fire-snake-301
cd /opt/fire-snake-301
sudo chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Internet      │───▶│  Nginx (SSL)    │───▶│  Streamlit      │
│                 │    │  Port 80/443    │    │  Port 8501      │
│ fire-snake-     │    │  + WebSocket    │    │  Fire Snake 301 │
│ 301.fr          │    │  + Rate Limit   │    │  Container      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐳 Docker Services

### 1. Streamlit Service
- **Container**: `fire-snake-301-app`
- **Port**: 8501 (internal)
- **Health Check**: `/_stcore/health`
- **Restart**: `unless-stopped`

### 2. Nginx Service  
- **Container**: `fire-snake-301-nginx`
- **Ports**: 80, 443 (public)
- **SSL**: Let's Encrypt automated
- **Features**: WebSocket, Rate limiting, Security headers

## 🚀 Deployment Steps

### Prerequisites
- Ubuntu VPS with root access
- Domain name pointing to server IP
- Docker & Docker Compose installed

### 1. Clone & Setup
```bash
git clone https://github.com/jeromegonz1/301-redirect-generator.git /opt/fire-snake-301
cd /opt/fire-snake-301
```

### 2. Configure Environment
```bash
cp .env.production .env
nano .env
# Add your OpenAI API key
```

### 3. Run Deployment Script
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. Manual Steps (if script fails)
```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

# Setup SSL (if not automated)
sudo certbot certonly --standalone \
  --email your-email@domain.com \
  --agree-tos \
  --no-eff-email \
  -d fire-snake-301.fr \
  -d www.fire-snake-301.fr

# Restart nginx with SSL
docker-compose -f docker-compose.prod.yml restart nginx
```

## 🔧 Management Commands

### Container Management
```bash
# View status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Stop everything
docker-compose -f docker-compose.prod.yml down
```

### SSL Management
```bash
# Manual renewal
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate
openssl s509 -in /etc/letsencrypt/live/fire-snake-301.fr/cert.pem -text -noout
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl https://fire-snake-301.fr/_stcore/health

# Container health
docker-compose -f docker-compose.prod.yml ps

# Nginx status
docker exec fire-snake-301-nginx nginx -t
```

### Logs
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs streamlit

# Nginx logs  
docker-compose -f docker-compose.prod.yml logs nginx

# Follow live logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 Security Features

- **SSL/TLS**: Automatic Let's Encrypt certificates
- **HSTS**: Strict transport security headers
- **Rate Limiting**: API and general request limits
- **Security Headers**: XSS, CSRF, clickjacking protection
- **Firewall**: UFW configured for essential ports only

## 🐛 Troubleshooting

### WebSocket Issues
If you see "Please wait..." forever:
1. Check if WebSocket upgrade headers are present
2. Verify SSL certificate is valid
3. Check Nginx logs for connection errors

```bash
# Check WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  https://fire-snake-301.fr/_stcore/stream
```

### Container Won't Start
```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs streamlit

# Check if port is available
sudo netstat -tlnp | grep :8501

# Rebuild from scratch
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check Nginx SSL config
docker exec fire-snake-301-nginx nginx -t
```

## 📈 Performance Optimization

### Resource Limits
Edit `docker-compose.prod.yml` to add resource limits:
```yaml
services:
  streamlit:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Nginx Optimization
The configuration includes:
- **Gzip compression** for static assets
- **Keep-alive connections** for WebSocket
- **Rate limiting** to prevent abuse
- **Static file caching** for better performance

## 🔄 Updates

### Application Updates
```bash
cd /opt/fire-snake-301
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

### SSL Renewal (Automatic)
SSL certificates are automatically renewed via cron job:
```bash
# Check cron job
crontab -l

# Manual renewal test
./scripts/ssl-renew.sh
```

## 📞 Support

For issues with Fire Snake 301 production deployment:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify health: `curl https://fire-snake-301.fr/_stcore/health`
3. Review this guide for common solutions

---

**🔥🐍 Fire Snake 301** - Scaling the web, one redirect at a time.