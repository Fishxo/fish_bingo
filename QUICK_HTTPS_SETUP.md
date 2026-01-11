# Quick HTTPS Setup for goodbingo.shop

Since you've already:
- ✅ Bought domain `goodbingo.shop` from Namecheap
- ✅ Pointed domain to your Elastic IP
- ✅ Updated nginx.conf with your domain

Follow these steps to complete HTTPS setup:

## Step 1: Copy Nginx Config to EC2

**Important**: Before copying, we need to temporarily remove/comment out the SSL certificate lines because Certbot will add them automatically.

First, SSH into your EC2 instance:

```bash
ssh ubuntu@your-elastic-ip
```

Then copy your nginx config. You can either:

**Option A: Use SCP from your local machine** (recommended):
```bash
# From your local machine (Windows PowerShell)
scp nginx/nginx.conf ubuntu@your-elastic-ip:/tmp/nginx-bingo.conf
```

**Option B: Create it directly on EC2**:
```bash
# On EC2, create the file
sudo nano /etc/nginx/sites-available/bingo
```

**IMPORTANT**: Before Certbot, temporarily comment out or remove these lines (Certbot will add them automatically):

```nginx
# Comment out these lines temporarily:
# ssl_certificate /etc/letsencrypt/live/goodbingo.shop/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/goodbingo.shop/privkey.pem;

# And change these lines:
listen 443 ssl http2;  # Temporarily change to: listen 443 http2;
```

**OR** use this temporary config (without SSL lines) and let Certbot add them:

```bash
# Copy the config without SSL certificate lines first
sudo nano /etc/nginx/sites-available/bingo
# Paste your config but remove lines 30-31 (SSL certificate paths)
# And remove 'ssl' from line 25: listen 443 http2;
```

## Step 2: Verify DNS is Working

```bash
# Check if domain points to your Elastic IP
dig goodbingo.shop
# Should show your Elastic IP in the ANSWER section

# Or use nslookup
nslookup goodbingo.shop
```

Wait 5-10 minutes after setting up DNS if it's not working yet.

## Step 3: Install Nginx and Certbot

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Nginx (if not already installed)
sudo apt install nginx -y

# Install Certbot for Nginx
sudo apt install certbot python3-certbot-nginx -y
```

## Step 4: Set Up Nginx Configuration

```bash
# Copy config file to Nginx sites-available
sudo cp /tmp/nginx-bingo.conf /etc/nginx/sites-available/bingo
# OR if you created it directly:
# It should already be at /etc/nginx/sites-available/bingo

# Edit the file to temporarily remove SSL certificate lines
sudo nano /etc/nginx/sites-available/bingo
```

**In the editor**, find these lines and comment them out (add # at the beginning):

```nginx
# Comment out these lines (lines 30-31):
# ssl_certificate /etc/letsencrypt/live/goodbingo.shop/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/goodbingo.shop/privkey.pem;

# Change line 25 from:
listen 443 ssl http2;
# To (temporarily remove 'ssl'):
listen 443 http2;
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 5: Enable Nginx Site

```bash
# Create symlink to enable the site
sudo ln -s /etc/nginx/sites-available/bingo /etc/nginx/sites-enabled/bingo

# Remove default Nginx site (if it exists)
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes (says "syntax is ok"), restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 6: Configure Firewall

```bash
# Install UFW if not installed
sudo apt install ufw -y

# Allow necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (for Let's Encrypt)
sudo ufw allow 443/tcp  # HTTPS

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

## Step 7: Get SSL Certificate with Certbot

```bash
# Run Certbot to get SSL certificate
# This will automatically update your Nginx config with SSL certificate paths
sudo certbot --nginx -d goodbingo.shop -d www.goodbingo.shop

# Follow the prompts:
# 1. Enter your email address (for renewal notifications)
# 2. Agree to terms (Y)
# 3. Share email with EFF (optional, N is fine)
# 4. Redirect HTTP to HTTPS? (2 - Yes, redirect all)
```

Certbot will:
- ✅ Get SSL certificate from Let's Encrypt
- ✅ Automatically update your Nginx config with SSL paths
- ✅ Set up HTTPS redirect

## Step 8: Verify SSL Certificate

```bash
# Check certificate was installed
sudo certbot certificates

# Test HTTPS from command line
curl -I https://goodbingo.shop
# Should return "HTTP/2 200" or similar

# Test auto-renewal (dry run)
sudo certbot renew --dry-run
```

## Step 9: Enable Auto-Renewal

```bash
# Certbot should have set this up automatically, but verify:
sudo systemctl status certbot.timer

# If not enabled, enable it:
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Step 10: Update Environment Variables

```bash
# Edit your .env file
nano /home/ubuntu/apps/good-bingo/arif_bingo/.env

# Update or add these lines:
TELEGRAM_WEB_APP_URL=https://goodbingo.shop
CSRF_TRUSTED_ORIGINS=https://goodbingo.shop,https://www.goodbingo.shop
ALLOWED_HOSTS=goodbingo.shop,www.goodbingo.shop,localhost

# Save and exit (Ctrl+X, Y, Enter)
```

## Step 11: Restart Services

```bash
# Restart Gunicorn (to pick up new environment variables)
sudo systemctl restart bingo-gunicorn.service

# Restart Telegram Bot (to pick up new TELEGRAM_WEB_APP_URL)
sudo systemctl restart bingo-telegram-bot.service

# Restart Nginx (if needed)
sudo systemctl restart nginx
```

## Step 12: Test Everything

```bash
# Test HTTPS in browser
# Visit: https://goodbingo.shop
# Should show your app with padlock icon ✅

# Test Telegram bot
# Send /play command to your bot
# "Start Game" button should open web app (not show link) ✅
```

## Troubleshooting

### If Certbot fails with "Failed to obtain certificate":

1. **Check DNS**: 
   ```bash
   dig goodbingo.shop
   # Should show your Elastic IP
   ```

2. **Check port 80 is open**:
   ```bash
   sudo ufw allow 80/tcp
   sudo systemctl restart nginx
   ```

3. **Wait for DNS propagation** (can take 5-48 hours, usually 10 minutes)

4. **Verify domain is accessible**:
   ```bash
   curl http://goodbingo.shop
   # Should return something (even if it's an error)
   ```

### If Nginx fails to start:

```bash
# Check configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### If HTTPS works but Telegram still shows link:

1. Verify `.env` file has correct URL:
   ```bash
   cat /home/ubuntu/apps/good-bingo/arif_bingo/.env | grep TELEGRAM_WEB_APP_URL
   # Should show: TELEGRAM_WEB_APP_URL=https://goodbingo.shop
   ```

2. Restart Telegram bot:
   ```bash
   sudo systemctl restart bingo-telegram-bot.service
   sudo journalctl -u bingo-telegram-bot.service -f
   # Check logs for any errors
   ```

3. Test SSL certificate is valid:
   ```bash
   openssl s_client -connect goodbingo.shop:443 -servername goodbingo.shop
   # Should show "Verify return code: 0 (ok)"
   ```

## Quick Commands Reference

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Reload Nginx (without downtime)
sudo nginx -s reload

# Check SSL certificate
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# View Nginx logs
sudo tail -f /var/log/nginx/bingo_access.log
sudo tail -f /var/log/nginx/bingo_error.log

# Check services
sudo systemctl status bingo-gunicorn.service
sudo systemctl status bingo-telegram-bot.service
```

## Done! ✅

After completing these steps:
- ✅ HTTPS will be working at https://goodbingo.shop
- ✅ SSL certificate will auto-renew every 90 days
- ✅ Telegram bot will open web app instead of showing link
- ✅ All HTTP traffic will redirect to HTTPS

