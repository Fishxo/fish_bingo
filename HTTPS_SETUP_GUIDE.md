# HTTPS Setup Guide for AWS EC2 (Telegram Web App Support)

Telegram Web Apps **require HTTPS** with a valid SSL certificate. This guide shows you how to set up HTTPS on your EC2 instance.

## Prerequisites

1. ✅ AWS EC2 instance running (Ubuntu 22.04 recommended)
2. ✅ Elastic IP assigned to your instance
3. ✅ Domain name (or you can use the Elastic IP - see Option 2)
4. ✅ Ports 80 and 443 open in AWS Security Group
5. ✅ Nginx installed
6. ✅ Gunicorn running on port 8000

---

## Option 1: Using a Domain Name (Recommended - Free SSL Certificate)

This is the **best option** - you get a free SSL certificate from Let's Encrypt.

### Step 1: Get a Domain Name

1. Purchase a domain from:
   - Namecheap ($1-10/year)
   - GoDaddy
   - Cloudflare ($8/year - includes free privacy)
   - Or use a free domain from Freenom

2. Point your domain to your Elastic IP:
   - Go to your domain registrar's DNS settings
   - Add an A record:
     - **Type**: A
     - **Name**: @ (or leave blank for root domain)
     - **Value**: Your Elastic IP (e.g., `51.20.4.210`)
     - **TTL**: 3600 (or default)

3. (Optional) Add www subdomain:
   - **Type**: A
   - **Name**: www
   - **Value**: Your Elastic IP
   - **TTL**: 3600

4. Wait 5-10 minutes for DNS propagation

### Step 2: Install Certbot (Let's Encrypt SSL)

```bash
# SSH into your EC2 instance
ssh ubuntu@your-elastic-ip

# Update system
sudo apt update
sudo apt upgrade -y

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y
```

### Step 3: Install and Configure Nginx

```bash
# Install Nginx (if not already installed)
sudo apt install nginx -y

# Copy the nginx configuration file
sudo cp /path/to/your/project/nginx/nginx.conf /etc/nginx/sites-available/bingo

# Edit the configuration to use your domain
sudo nano /etc/nginx/sites-available/bingo

# Replace "yourdomain.com" with your actual domain in these lines:
# - server_name yourdomain.com www.yourdomain.com;
# - (appears twice - once for HTTP, once for HTTPS)
```

**Important**: For now, comment out the SSL certificate lines in the HTTPS server block:

```nginx
# SSL certificate paths (will be set by Certbot)
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

And temporarily remove the `ssl` keywords:

```nginx
listen 443 http2;  # Remove 'ssl' temporarily
listen [::]:443 http2;
```

### Step 4: Enable Nginx Configuration

```bash
# Create symlink to enable the site
sudo ln -s /etc/nginx/sites-available/bingo /etc/nginx/sites-enabled/

# Remove default Nginx site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 5: Get SSL Certificate with Certbot

```bash
# Run Certbot to get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts:
# - Enter your email address (for renewal notifications)
# - Agree to terms of service (Y)
# - Share email with EFF (optional, N)
# - Choose to redirect HTTP to HTTPS (2 - recommended)
```

Certbot will:
- ✅ Automatically get SSL certificate from Let's Encrypt
- ✅ Update your Nginx config with SSL paths
- ✅ Set up auto-renewal

### Step 6: Update Environment Variables

```bash
# Edit your .env file
nano /home/ubuntu/apps/good-bingo/arif_bingo/.env

# Update TELEGRAM_WEB_APP_URL to use HTTPS
TELEGRAM_WEB_APP_URL=https://yourdomain.com

# Also update CSRF_TRUSTED_ORIGINS (add to existing ones)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Update ALLOWED_HOSTS
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 7: Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart bingo-gunicorn.service

# Restart Telegram bot
sudo systemctl restart bingo-telegram-bot.service

# Restart Nginx (if needed)
sudo systemctl restart nginx
```

### Step 8: Verify HTTPS is Working

```bash
# Test HTTPS from command line
curl -I https://yourdomain.com

# Should return "HTTP/2 200" or similar

# Test in browser
# Visit: https://yourdomain.com
# Should show your app with a padlock icon ✅
```

### Step 9: Test Auto-Renewal

SSL certificates expire every 90 days. Certbot sets up auto-renewal, but test it:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# If successful, certificates will auto-renew
```

---

## Option 2: Using Elastic IP Directly (Self-Signed Certificate)

⚠️ **WARNING**: Self-signed certificates will **NOT work** with Telegram Web Apps! Telegram requires a valid, trusted SSL certificate.

However, you can use this for testing or development.

### Alternative: Use Cloudflare Tunnel (No Domain Needed)

If you don't want to buy a domain, you can use Cloudflare Tunnel (free):

1. Sign up for free Cloudflare account
2. Install Cloudflare Tunnel on your EC2:
   ```bash
   # Install Cloudflare Tunnel
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   
   # Login to Cloudflare
   cloudflared tunnel login
   
   # Create tunnel
   cloudflared tunnel create bingo-app
   
   # Configure tunnel
   cloudflared tunnel route dns bingo-app your-subdomain.cloudflare.com
   
   # Run tunnel
   cloudflared tunnel run bingo-app
   ```

3. Your app will be available at `https://your-subdomain.cloudflare.com` with valid SSL

---

## Option 3: Use AWS Certificate Manager (ACM) with Load Balancer

If you want to use AWS services:

1. Create an Application Load Balancer (ALB) in AWS
2. Request SSL certificate from AWS Certificate Manager (ACM)
3. Attach certificate to ALB
4. Point your domain to ALB
5. ALB forwards traffic to EC2 on port 8000

This is more complex but integrates with AWS services.

---

## Troubleshooting

### Issue: Certbot fails with "Failed to obtain certificate"

**Solution**:
- Verify DNS is pointing to your Elastic IP: `dig yourdomain.com`
- Ensure port 80 is open: `sudo ufw allow 80`
- Check domain is accessible: `curl http://yourdomain.com`
- Wait longer for DNS propagation (can take up to 48 hours)

### Issue: Nginx fails to start

**Solution**:
- Check configuration: `sudo nginx -t`
- Check error logs: `sudo tail -f /var/log/nginx/error.log`
- Ensure port 443 is open: `sudo ufw allow 443`

### Issue: HTTPS works but Telegram still shows link

**Solution**:
- Verify `TELEGRAM_WEB_APP_URL` uses `https://` (not `http://`)
- Restart Telegram bot: `sudo systemctl restart bingo-telegram-bot.service`
- Check SSL certificate is valid: `openssl s_client -connect yourdomain.com:443`

### Issue: Certificate renewal fails

**Solution**:
- Certbot auto-renewal runs via systemd timer
- Check timer: `sudo systemctl status certbot.timer`
- Enable timer: `sudo systemctl enable certbot.timer`
- Test renewal: `sudo certbot renew --dry-run`

---

## Security Checklist

- ✅ Port 443 (HTTPS) open in AWS Security Group
- ✅ Port 80 (HTTP) open (for redirect and Let's Encrypt)
- ✅ Firewall configured: `sudo ufw allow 80 && sudo ufw allow 443`
- ✅ SSL certificate valid and auto-renewing
- ✅ Nginx configured with security headers
- ✅ Django `SECURE_SSL_REDIRECT = True` (if using Django redirect)
- ✅ `SESSION_COOKIE_SECURE = True` in settings.py (already set)
- ✅ `CSRF_COOKIE_SECURE = True` in settings.py (already set)

---

## Quick Reference Commands

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Reload Nginx (without downtime)
sudo nginx -s reload

# Check SSL certificate expiry
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check if Certbot auto-renewal is enabled
sudo systemctl status certbot.timer

# View Nginx access logs
sudo tail -f /var/log/nginx/bingo_access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/bingo_error.log
```

---

## After Setup

1. ✅ Update `.env` file with `TELEGRAM_WEB_APP_URL=https://yourdomain.com`
2. ✅ Restart all services
3. ✅ Test HTTPS in browser
4. ✅ Test Telegram bot - "Start Game" button should open web app (not show link)
5. ✅ Verify SSL certificate auto-renewal is set up

---

## Need Help?

If you encounter issues:
1. Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
2. Check Gunicorn logs: `sudo journalctl -u bingo-gunicorn.service -f`
3. Check bot logs: `sudo journalctl -u bingo-telegram-bot.service -f`
4. Verify DNS: `dig yourdomain.com` or `nslookup yourdomain.com`
5. Test SSL: `openssl s_client -connect yourdomain.com:443`

