#!/bin/bash
# Quick HTTPS Setup Script for AWS EC2
# This script sets up HTTPS with Let's Encrypt SSL certificate
# 
# Prerequisites:
# 1. Domain name pointing to your Elastic IP (A record)
# 2. Ports 80 and 443 open in AWS Security Group
# 3. SSH access to EC2 instance

set -e  # Exit on error

echo "🔐 HTTPS Setup Script for Django + Telegram Bot"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Get domain name from user
read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Domain name is required!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Domain: $DOMAIN"
echo "   Elastic IP: $(curl -s http://checkip.amazonaws.com/)"
echo ""
read -p "Is this correct? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 1
fi

# Update system
echo ""
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update
apt upgrade -y

# Install Nginx (if not installed)
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Nginx...${NC}"
    apt install nginx -y
fi

# Install Certbot
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Certbot...${NC}"
    apt install certbot python3-certbot-nginx -y
fi

# Install firewall (if not installed)
if ! command -v ufw &> /dev/null; then
    echo -e "${YELLOW}📦 Installing UFW firewall...${NC}"
    apt install ufw -y
fi

# Configure firewall
echo ""
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw --force enable

# Set up Nginx configuration
echo ""
echo -e "${YELLOW}📝 Setting up Nginx configuration...${NC}"

NGINX_CONFIG="/etc/nginx/sites-available/bingo"
NGINX_ENABLED="/etc/nginx/sites-enabled/bingo"

# Create Nginx config directory if it doesn't exist
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Get the backend directory path (adjust if different)
read -p "Enter full path to backend directory (default: /home/ubuntu/apps/good-bingo/arif_bingo/backend): " BACKEND_DIR
BACKEND_DIR=${BACKEND_DIR:-/home/ubuntu/apps/good-bingo/arif_bingo/backend}

# Create Nginx configuration
cat > $NGINX_CONFIG <<EOF
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};

    # Allow Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS server - main application (temporary, will be updated by Certbot)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    # SSL certificates (will be set by Certbot)
    # ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # Temporary self-signed cert (for initial setup)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/bingo_access.log;
    error_log /var/log/nginx/bingo_error.log;

    # Maximum upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias ${BACKEND_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Media files
    location /media/ {
        alias ${BACKEND_DIR}/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # WebSocket support for Django Channels
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # Main application proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        
        # WebSocket headers
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
if [ -f "$NGINX_ENABLED" ]; then
    rm $NGINX_ENABLED
fi
ln -s $NGINX_CONFIG $NGINX_ENABLED

# Remove default Nginx site
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Test Nginx configuration
echo ""
echo -e "${YELLOW}🔍 Testing Nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration has errors${NC}"
    exit 1
fi

# Start/restart Nginx
echo ""
echo -e "${YELLOW}🔄 Starting Nginx...${NC}"
systemctl restart nginx
systemctl enable nginx

# Verify domain is pointing to this server
echo ""
echo -e "${YELLOW}🔍 Verifying DNS configuration...${NC}"
CURRENT_IP=$(curl -s http://checkip.amazonaws.com/)
DOMAIN_IP=$(dig +short ${DOMAIN} | tail -n1)

if [ -z "$DOMAIN_IP" ]; then
    echo -e "${RED}❌ Warning: Cannot resolve ${DOMAIN}${NC}"
    echo -e "${YELLOW}   Make sure your domain's A record points to: ${CURRENT_IP}${NC}"
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
elif [ "$DOMAIN_IP" != "$CURRENT_IP" ]; then
    echo -e "${RED}❌ Warning: ${DOMAIN} resolves to ${DOMAIN_IP}, but this server's IP is ${CURRENT_IP}${NC}"
    echo -e "${YELLOW}   Update your domain's A record to point to: ${CURRENT_IP}${NC}"
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ DNS is correctly configured${NC}"
fi

# Get SSL certificate with Certbot
echo ""
echo -e "${YELLOW}🔐 Getting SSL certificate from Let's Encrypt...${NC}"
echo -e "${YELLOW}   This will open an interactive prompt. Please follow the instructions.${NC}"
echo ""

# Check if www subdomain is configured
read -p "Do you want to include www.${DOMAIN}? (y/n): " INCLUDE_WWW

if [ "$INCLUDE_WWW" == "y" ]; then
    certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email --redirect
else
    certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email --redirect
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL certificate obtained successfully!${NC}"
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}   Common issues:${NC}"
    echo "   1. DNS not pointing to this server (wait for DNS propagation)"
    echo "   2. Port 80 blocked by firewall"
    echo "   3. Domain not accessible from internet"
    exit 1
fi

# Set up auto-renewal
echo ""
echo -e "${YELLOW}🔄 Setting up SSL certificate auto-renewal...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

# Test renewal
echo ""
echo -e "${YELLOW}🧪 Testing certificate renewal...${NC}"
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Auto-renewal test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Auto-renewal test failed, but certificate is valid${NC}"
fi

# Restart Nginx with new configuration
echo ""
echo -e "${YELLOW}🔄 Restarting Nginx with SSL configuration...${NC}"
systemctl restart nginx

# Get environment file path
read -p "Enter path to .env file (default: /home/ubuntu/apps/good-bingo/arif_bingo/.env): " ENV_FILE
ENV_FILE=${ENV_FILE:-/home/ubuntu/apps/good-bingo/arif_bingo/.env}

# Update .env file
echo ""
echo -e "${YELLOW}📝 Updating environment variables...${NC}"

if [ -f "$ENV_FILE" ]; then
    # Update TELEGRAM_WEB_APP_URL
    if grep -q "TELEGRAM_WEB_APP_URL" "$ENV_FILE"; then
        sed -i "s|TELEGRAM_WEB_APP_URL=.*|TELEGRAM_WEB_APP_URL=https://${DOMAIN}|g" "$ENV_FILE"
    else
        echo "TELEGRAM_WEB_APP_URL=https://${DOMAIN}" >> "$ENV_FILE"
    fi

    # Update CSRF_TRUSTED_ORIGINS
    if grep -q "CSRF_TRUSTED_ORIGINS" "$ENV_FILE"; then
        sed -i "s|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}|g" "$ENV_FILE"
    else
        echo "CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}" >> "$ENV_FILE"
    fi

    # Update ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS" "$ENV_FILE"; then
        sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost|g" "$ENV_FILE"
    else
        echo "ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost" >> "$ENV_FILE"
    fi

    echo -e "${GREEN}✅ Environment variables updated${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found at ${ENV_FILE}${NC}"
    echo -e "${YELLOW}   Please update manually:${NC}"
    echo "   TELEGRAM_WEB_APP_URL=https://${DOMAIN}"
    echo "   CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}"
    echo "   ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost"
fi

# Final instructions
echo ""
echo -e "${GREEN}✅ HTTPS Setup Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "   1. Restart Gunicorn: sudo systemctl restart bingo-gunicorn.service"
echo "   2. Restart Telegram Bot: sudo systemctl restart bingo-telegram-bot.service"
echo "   3. Test HTTPS: curl -I https://${DOMAIN}"
echo "   4. Test in browser: https://${DOMAIN}"
echo "   5. Test Telegram bot - 'Start Game' button should open web app"
echo ""
echo "🔐 SSL Certificate Info:"
echo "   Domain: ${DOMAIN}"
echo "   Certificate Location: /etc/letsencrypt/live/${DOMAIN}/"
echo "   Auto-renewal: Enabled (runs daily, renews 30 days before expiry)"
echo ""
echo "📝 Logs:"
echo "   Nginx Access: sudo tail -f /var/log/nginx/bingo_access.log"
echo "   Nginx Error: sudo tail -f /var/log/nginx/bingo_error.log"
echo ""
echo "✨ Done!"

