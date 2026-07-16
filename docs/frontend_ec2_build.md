# Frontend production build (EC2)

## Root cause of white screen

If the browser shows a blank page but the tab title is **Markos Bingo**, Django is likely serving the **development** `frontend/index.html`, which contains:

```html
<script type="module" src="/src/main.js"></script>
```

That file only exists when the Vite dev server is running. In production you must serve the **built** files in `frontend_dist/`:

```html
<script type="module" crossorigin src="/assets/index-XXXXX.js"></script>
```

## Build on EC2

```bash
cd ~/fish_bingo/frontend
npm install
npm run build
ls -la ../frontend_dist/
ls -la ../frontend_dist/assets/
```

Expected output: `../frontend_dist/index.html` and hashed JS/CSS under `../frontend_dist/assets/`.

## Restart backend

```bash
sudo systemctl restart bingo-gunicorn
```

## Verify

```bash
curl -s http://127.0.0.1:8000/ | grep -E 'src=|href='
curl -I http://127.0.0.1:8000/assets/
curl -I http://16.16.200.57/
```

Browser DevTools → Network: `/assets/index-*.js` should return **200**, not 404.

## Deployment checklist

- [ ] `npm run build` completed without errors
- [ ] `~/fish_bingo/frontend_dist/index.html` exists
- [ ] `~/fish_bingo/frontend_dist/assets/*.js` exists
- [ ] `sudo systemctl restart bingo-gunicorn`
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] No `/src/main.js` in page source

## Notes

- `frontend_dist/` is created by Vite (`vite.config.js` → `outDir: ../frontend_dist`)
- Vite `base: '/'` is correct for Nginx at domain/IP root
- Re-run `npm run build` after every frontend code change
