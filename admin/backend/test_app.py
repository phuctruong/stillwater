"""Tests for admin backend FastAPI application."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import json

# Add paths
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "cli" / "src"))

from admin.backend.app import app

client = TestClient(app)


class TestHealth:
    """Test health check endpoint."""

    def test_health_check(self):
        """GET /health should return status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert "firestore_enabled" in data


class TestConfig:
    """Test config endpoint for Firebase."""

    def test_config_endpoint(self):
        """GET /config should return Firebase configuration."""
        resp = client.get("/config")
        assert resp.status_code == 200
        data = resp.json()

        assert "firebase" in data
        assert "api_url" in data

        firebase = data["firebase"]
        assert firebase["apiKey"]
        assert firebase["authDomain"]
        assert firebase["projectId"]


class TestDataEndpoints:
    """Test data CRUD endpoints."""

    def test_get_facts(self):
        """GET /api/data/facts should return facts list."""
        resp = client.get("/api/data/facts")
        assert resp.status_code == 200
        data = resp.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)
        # Verify facts have expected structure
        if data["facts"]:
            fact = data["facts"][0]
            assert "title" in fact
            assert "fact" in fact
            assert "category" in fact

    def test_get_jokes(self):
        """GET /api/data/jokes should return joke list."""
        resp = client.get("/api/data/jokes")
        assert resp.status_code == 200
        data = resp.json()
        assert "jokes" in data
        assert isinstance(data["jokes"], list)

    def test_post_joke(self):
        """POST /api/data/jokes should add a joke."""
        joke = {
            "id": "test_joke_001",
            "text": "Why did the AI go to school?",
            "category": "tech"
        }
        resp = client.post("/api/data/jokes", json=joke)
        assert resp.status_code == 200
        data = resp.json()
        assert "added" in data

    def test_get_wishes(self):
        """GET /api/data/wishes should return wishes."""
        resp = client.get("/api/data/wishes")
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data

    def test_get_settings(self):
        """GET /api/data/settings should return current settings."""
        resp = client.get("/api/data/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert "firestore_enabled" in data
        assert "api_key_configured" in data

    def test_get_learned(self):
        """GET /api/data/learned should return learned entries."""
        resp = client.get("/api/data/learned")
        assert resp.status_code == 200
        data = resp.json()
        assert "learned" in data
        assert isinstance(data["learned"], list)


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_verify_token_missing_token(self):
        """POST /api/auth/verify-token without token should fail."""
        resp = client.post("/api/auth/verify-token", json={})
        assert resp.status_code == 400

    def test_get_user_missing_auth(self):
        """GET /api/auth/user without auth header should fail."""
        resp = client.get("/api/auth/user")
        assert resp.status_code == 401

    def test_get_user_with_invalid_token(self):
        """GET /api/auth/user with invalid token should fail."""
        resp = client.get(
            "/api/auth/user",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        # Will return 503 (cloud API unavailable), 404 (not found), or auth error
        assert resp.status_code in [401, 404, 503]


class TestVerificationEndpoints:
    """Test verification endpoints."""

    def test_verify_social_no_auth(self):
        """POST /api/verify/social without auth should fail."""
        resp = client.post("/api/verify/social", json={"url": "https://twitter.com/..."})
        assert resp.status_code == 401

    def test_verify_social_with_token(self):
        """POST /api/verify/social with token (will fail at cloud)."""
        resp = client.post(
            "/api/verify/social",
            json={"url": "https://twitter.com/test/status/123"},
            headers={"Authorization": "Bearer test_token"}
        )
        # Will return 503 (cloud API unavailable) or other error codes
        # Status codes should NOT be 401 (we have auth header)
        assert resp.status_code != 401

    def test_verify_status_no_auth(self):
        """GET /api/verify/status without auth should fail."""
        resp = client.get("/api/verify/status")
        assert resp.status_code == 401


class TestApiKeyEndpoints:
    """Test API key endpoints."""

    def test_generate_key_no_auth(self):
        """POST /api/keys/generate without auth should fail."""
        resp = client.post("/api/keys/generate")
        assert resp.status_code == 401

    def test_generate_key_with_token(self):
        """POST /api/keys/generate with token (will fail at cloud)."""
        resp = client.post(
            "/api/keys/generate",
            headers={"Authorization": "Bearer test_token"}
        )
        # Will return various codes since cloud API is unavailable
        # Status codes should NOT be 401 (we have auth header)
        assert resp.status_code != 401

    def test_list_keys_no_auth(self):
        """GET /api/keys/list without auth should fail."""
        resp = client.get("/api/keys/list")
        assert resp.status_code == 401

    def test_list_keys_with_token(self):
        """GET /api/keys/list with token (will fail at cloud)."""
        resp = client.get(
            "/api/keys/list",
            headers={"Authorization": "Bearer test_token"}
        )
        # Will return various codes since cloud API is unavailable
        # Status codes should NOT be 401 (we have auth header)
        assert resp.status_code != 401


class TestMermaidEndpoints:
    """Test Mermaid-Interactive orchestration endpoints."""

    def test_get_orchestration_mermaid(self):
        """GET /api/orchestration/mermaid should return Mermaid diagram syntax."""
        resp = client.get("/api/orchestration/mermaid")
        assert resp.status_code == 200
        data = resp.json()

        # Check structure
        assert "mermaid" in data
        assert "nodes" in data
        assert "status" in data
        assert data["status"] == "ok"

        # Check Mermaid syntax
        mermaid_syntax = data["mermaid"]
        assert "graph LR" in mermaid_syntax
        assert "explorer" in mermaid_syntax.lower()
        assert "builder" in mermaid_syntax.lower()
        assert "arbiter" in mermaid_syntax.lower()

        # Check nodes list
        nodes = data["nodes"]
        assert isinstance(nodes, list)
        assert "explorer" in nodes
        assert "builder" in nodes
        assert "arbiter" in nodes

    def test_get_node_details_explorer(self):
        """GET /api/orchestration/node/explorer should return explorer node details."""
        resp = client.get("/api/orchestration/node/explorer")
        assert resp.status_code == 200
        data = resp.json()

        # Check required fields
        assert data["id"] == "explorer"
        assert data["name"] == "Explorer"
        assert data["role"] == "scout"
        assert data["model"] == "haiku"
        assert data["type"] == "CPU"
        assert data["status"] == "ok"

        # Check metadata
        assert "persona" in data
        assert "responsibility" in data
        assert "description" in data
        assert "strengths" in data
        assert isinstance(data["strengths"], list)
        assert "tools" in data
        assert isinstance(data["tools"], list)

        # Check algorithm and examples
        assert "algorithm" in data
        assert "examples" in data
        assert isinstance(data["examples"], list)
        assert len(data["examples"]) > 0

        # Check config path
        assert "config_path" in data
        assert "rung_target" in data
        assert data["rung_target"] == 641

    def test_get_node_details_builder(self):
        """GET /api/orchestration/node/builder should return builder node details."""
        resp = client.get("/api/orchestration/node/builder")
        assert resp.status_code == 200
        data = resp.json()

        # Check required fields
        assert data["id"] == "builder"
        assert data["name"] == "Builder"
        assert data["role"] == "coder"
        assert data["model"] == "sonnet"
        assert data["type"] == "Swarm"
        assert data["status"] == "ok"

        # Check examples are present
        assert len(data["examples"]) > 0
        assert any("implement" in ex.lower() for ex in data["examples"])

    def test_get_node_details_arbiter(self):
        """GET /api/orchestration/node/arbiter should return arbiter node details."""
        resp = client.get("/api/orchestration/node/arbiter")
        assert resp.status_code == 200
        data = resp.json()

        # Check required fields
        assert data["id"] == "arbiter"
        assert data["name"] == "Arbiter"
        assert data["role"] == "skeptic"
        assert data["model"] == "sonnet"
        assert data["type"] == "Swarm"
        assert data["status"] == "ok"

        # Check examples are present
        assert len(data["examples"]) > 0
        assert any("review" in ex.lower() or "verify" in ex.lower() for ex in data["examples"])

    def test_get_node_details_invalid_node(self):
        """GET /api/orchestration/node/invalid should return 404."""
        resp = client.get("/api/orchestration/node/invalid")
        assert resp.status_code == 404

    def test_mermaid_diagram_completeness(self):
        """Verify mermaid diagram has all required edges."""
        resp = client.get("/api/orchestration/mermaid")
        assert resp.status_code == 200
        data = resp.json()

        mermaid_syntax = data["mermaid"]
        # Should have edges between nodes (explorer->builder->arbiter)
        assert "-->" in mermaid_syntax
        # Count arrows - should have 2 edges
        arrow_count = mermaid_syntax.count("-->")
        assert arrow_count >= 2


class TestStaticFiles:
    """Test static file serving."""

    def test_serve_admin_root(self):
        """GET / should serve admin/static/index.html."""
        resp = client.get("/")
        assert resp.status_code == 200
        # Should contain HTML content
        assert b"html" in resp.content or b"Stillwater" in resp.content

    def test_mermaid_css_served(self):
        """GET /static/css/mermaid-interactive.css should be served."""
        resp = client.get("/static/css/mermaid-interactive.css")
        assert resp.status_code == 200
        assert b"mermaid" in resp.content.lower()

    def test_mermaid_js_served(self):
        """GET /static/js/mermaid-interactive.js should be served."""
        resp = client.get("/static/js/mermaid-interactive.js")
        assert resp.status_code == 200
        assert b"mermaid" in resp.content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
