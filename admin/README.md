# Stillwater Admin

This directory currently contains two web UIs:

- `admin/frontend/` (Admin Dojo v2.0): view-only dashboard for status + Mermaid diagrams.
- `admin/static/` (legacy analytics app): older monolithic UI still served by `admin/server.py`.

## Admin Dojo v2.0 (`admin/frontend/`)

Architecture:
- Single-page app with 3 files: `index.html`, `app.css`, `app.js`
- Dark glassmorphism theme
- No build step and no framework runtime
- Service worker offline cache for Mermaid graph payloads

Token system:
- 70+ CSS tokens in `:root`
- Raw color/size values are centralized in tokens (no raw `#hex` or `px` outside `:root`)
- Includes `[data-theme="light"]` token override support

JavaScript architecture:
- Frozen `CONFIG`
- Structured `Logger`
- `APIClient` wrapper for all network calls
- Immutable `createState()` state container
- Pure DOM event wiring (no inline `onclick`)
- Modal focus trap + focus restore + offline cached diagram badge

Image inventory used by admin:
- Droplets: 15 PNG files
- Yinyang: 10 GIF files
- SVG: 2 files
- Icons: 4 files

## Run

From repo root, use the stillwater CLI server entrypoint:

```bash
python -m stillwater.cli serve
```

Then open:

- `http://localhost:18790/admin/frontend/index.html` (frontend files)
- or the root route served by your chosen admin service

## Develop

- Edit files directly in `admin/frontend/`
- Refresh browser to see changes
- No bundler/build pipeline required

## Current gaps

- `admin/static/` and `admin/frontend/` are both present
- `admin/server.py` currently serves `admin/static/` at `/`
- `admin/backend/homepage_routes.py` serves `admin/frontend/index.html` at `/`
- Browser smoke and responsive coverage now automated in `admin/tests/test_admin_frontend_e2e.py`

Keep this split explicit until one app is officially deprecated.
