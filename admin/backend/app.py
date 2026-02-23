from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
from pathlib import Path
import httpx
import os

# Add stillwater/cli/src to path (for DataRegistry + SettingsLoader)
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "cli" / "src"))

from stillwater.data_registry import DataRegistry
from stillwater.settings_loader import SettingsLoader

app = FastAPI(title="Stillwater Admin", version="1.0.0")

# Initialize data access
registry = DataRegistry()
settings = SettingsLoader()

# Proxy target for cloud APIs (configurable for local dev vs production)
SOLACEAGI_API_URL = os.getenv("SOLACEAGI_API_URL", "https://www.solaceagi.com")

# -- Data endpoints (no auth required) -----------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "firestore_enabled": settings.is_sync_enabled()
    }

@app.get("/config")
async def get_config():
    """Serve Firebase config to frontend."""
    return {
        "firebase": {
            "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyC_8HU6dYcPMJyVfUfVVJB-wHkFCXyZ1Zk"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "solaceagi-dev.firebaseapp.com"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID", "solaceagi-dev"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "solaceagi-dev.appspot.com"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "123456789"),
            "appId": os.getenv("FIREBASE_APP_ID", "1:123456789:web:abcdef1234567890")
        },
        "api_url": SOLACEAGI_API_URL
    }

@app.get("/api/data/jokes")
async def get_jokes():
    """Load jokes from DataRegistry."""
    import json
    data = registry.load_data_file("jokes.json")
    if not data:
        return {"jokes": []}
    try:
        parsed = json.loads(data)
        # jokes.json is a direct array, not an object
        if isinstance(parsed, list):
            return {"jokes": parsed}
        elif isinstance(parsed, dict):
            return {"jokes": parsed.get("jokes", [])}
        else:
            return {"jokes": []}
    except json.JSONDecodeError:
        return {"jokes": []}

@app.post("/api/data/jokes")
async def add_joke(joke: dict):
    """Add joke to data/custom/jokes.json."""
    import json
    data_str = registry.load_data_file("jokes.json") or "[]"
    data = json.loads(data_str)

    # jokes.json is a direct array
    if isinstance(data, list):
        data.append(joke)
    elif isinstance(data, dict) and "jokes" in data:
        data["jokes"].append(joke)
    else:
        # Fallback: create array
        data = [joke]

    registry.save_data_file("jokes.json", json.dumps(data, indent=2))
    return {"added": joke}

@app.get("/api/data/wishes")
async def get_wishes():
    """Load wishes from DataRegistry."""
    data = registry.load_data_file("wishes.md")
    return {"content": data or ""}

@app.post("/api/data/wishes")
async def add_wish(wish: dict):
    """Add wish entry (appends to data/custom/wishes.md)."""
    import json
    data_str = registry.load_data_file("wishes.md") or "{}"
    # Parse Mermaid front-matter (simplified)
    # For MVP: just append JSON line
    registry.save_data_file("wishes_added.json", json.dumps(wish))
    return {"added": wish}

@app.get("/api/data/settings")
async def get_settings():
    """Get current settings (from data/settings.md)."""
    api_key = settings.get_api_key()
    sync_enabled = settings.is_sync_enabled()
    return {
        "firestore_enabled": sync_enabled,
        "api_key_configured": api_key is not None,
        "api_key_preview": f"{api_key[:12]}...{api_key[-6:]}" if api_key else None
    }

@app.post("/api/data/settings")
async def update_setting(key: str, value: str):
    """Update a settings key."""
    if key == "firestore_enabled":
        settings.update_sync_metadata(
            timestamp=None,  # don't touch timestamp
            status=None  # don't touch status
        )
        # Parse and write back (simplified for MVP)
    return {"updated": key, "value": value}

@app.get("/api/data/learned")
async def get_learned():
    """List recent learned entries from data/custom/*.jsonl."""
    import json
    entries = []
    for jsonl_file in ["learned_wishes.jsonl", "learned_combos.jsonl", "learned_smalltalk.jsonl"]:
        content = registry.load_data_file(jsonl_file)
        if content:
            for line in content.strip().split("\n"):
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    # Sort by timestamp descending, limit 100
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"learned": entries[:100]}

# -- Auth endpoints (Firebase proxy) ------------------------------------------

@app.post("/api/auth/verify-token")
async def verify_token(body: dict):
    """Exchange Firebase ID token for user info.

    Proxies to cloud API for verification.
    """
    id_token = body.get("id_token")
    if not id_token:
        raise HTTPException(400, "Missing id_token")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{SOLACEAGI_API_URL}/api/v1/auth/verify-token",
                json={"id_token": id_token},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(resp.status_code, resp.text)
        except httpx.RequestError as e:
            raise HTTPException(503, f"Cloud API unavailable: {e}")

@app.get("/api/auth/user")
async def get_user(request: Request):
    """Get current user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing Authorization header")

    token = auth_header[7:]
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{SOLACEAGI_API_URL}/api/v1/auth/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(resp.status_code, "Invalid token")
        except httpx.RequestError:
            raise HTTPException(503, "Cloud API unavailable")

# -- Verification endpoints (proxy to cloud) ---------------------------------

@app.post("/api/verify/social")
async def verify_social(body: dict, request: Request):
    """Submit social post URL for verification."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise HTTPException(401, "Authentication required")

    token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{SOLACEAGI_API_URL}/api/v1/user/verify",
                json={"method": "social", "proof": body.get("url")},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            try:
                return resp.json()
            except Exception:
                raise HTTPException(resp.status_code, "Invalid response from cloud API")
        except httpx.RequestError:
            raise HTTPException(503, "Cloud API unavailable")

@app.get("/api/verify/status")
async def get_verification_status(request: Request):
    """Get verification status."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise HTTPException(401, "Authentication required")

    token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{SOLACEAGI_API_URL}/api/v1/user/verify/status",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(503, "Cloud API unavailable")

# -- API key endpoints (proxy to cloud) ---------------------------------------

@app.post("/api/keys/generate")
async def generate_api_key(request: Request):
    """Generate API key (requires verification)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise HTTPException(401, "Authentication required")

    token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{SOLACEAGI_API_URL}/api/v1/auth/generate-key",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(resp.status_code, resp.text)
        except httpx.RequestError:
            raise HTTPException(503, "Cloud API unavailable")

@app.get("/api/keys/list")
async def list_api_keys(request: Request):
    """List user's API keys."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        raise HTTPException(401, "Authentication required")

    token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{SOLACEAGI_API_URL}/api/v1/auth/keys",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            try:
                return resp.json()
            except Exception:
                raise HTTPException(resp.status_code, "Invalid response from cloud API")
        except httpx.RequestError:
            raise HTTPException(503, "Cloud API unavailable")

# -- Static files (admin UI) --------------------------------------------------

@app.get("/")
async def serve_admin():
    """Serve admin/static/index.html."""
    admin_static = REPO_ROOT / "admin" / "static" / "index.html"
    if admin_static.exists():
        return FileResponse(admin_static)
    else:
        return {"error": "Admin UI not found", "path": str(admin_static)}

# Mount static files (CSS, JS, etc.)
static_path = REPO_ROOT / "admin" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
