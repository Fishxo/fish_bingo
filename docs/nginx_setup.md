# Nginx setup for fish_bingo (EC2)

Gunicorn runs on `127.0.0.1:8000`. Nginx listens on port **80** and proxies HTTP/WebSocket traffic to Gunicorn.

## Prerequisites

- Gunicorn service running: `sudo systemctl status bingo-gunicorn`
- EC2 security group allows **HTTP (80)** from the internet
- Static and media directories exist on the server

```bash
mkdir -p /home/ubuntu/fish_bingo/backend/static
mkdir -p /home/ubuntu/fish_bingo/backend/media
```

Django collects admin/static assets to `staticfiles/` by default. If you use `collectstatic`, either copy/symlink into `static/` or update the `alias` path in the config:

```bash
cd /home/ubuntu/fish_bingo/backend
source venv/bin/activate
python manage.py collectstatic --noinput
ln -sfn /home/ubuntu/fish_bingo/backend/staticfiles /home/ubuntu/fish_bingo/backend/static
```

## Install site configuration

From the project root on EC2:

```bash
cd ~/fish_bingo

# Copy config into Nginx sites-available
sudo cp nginx/fish_bingo.conf /etc/nginx/sites-available/fish_bingo.conf

# Enable site
sudo ln -sf /etc/nginx/sites-available/fish_bingo.conf /etc/nginx/sites-enabled/fish_bingo.conf

# Remove default site (optional but recommended)
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload / restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Verify

```bash
sudo systemctl status nginx
curl -I http://16.16.200.57/api/health/
```

Open in browser:

- `http://16.16.200.57/`
- `http://16.16.200.57/admin-dashboard/`

## Logs

```bash
sudo tail -f /var/log/nginx/fish_bingo_access.log
sudo tail -f /var/log/nginx/fish_bingo_error.log
sudo journalctl -u nginx -f
```

## When you add a domain + HTTPS later

1. Point DNS to your EC2 Elastic IP
2. Update `server_name` in `nginx/fish_bingo.conf`
3. Run Certbot: `sudo certbot --nginx -d yourdomain.com`
4. Add your domain to Django `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

## Troubleshooting

| Problem | Check |
|---------|--------|
| 502 Bad Gateway | `sudo systemctl status bingo-gunicorn` |
| 404 on `/static/` | Run `collectstatic` and verify `static/` path |
| WebSocket fails | Confirm `/ws/` location and Redis are running |
| Connection refused on :80 | Security group + `sudo systemctl status nginx` |
| `invalid parameter "immutable"` | Use `add_header Cache-Control "public";` (not `"public, immutable"`) in site config, then `sudo nginx -t && sudo systemctl restart nginx` |
