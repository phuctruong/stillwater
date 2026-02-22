"""Tests for Evidence Pipeline Service (admin/services/evidence_pipeline.py).

Covers:
- Health endpoint (chain_length field)
- Capture first evidence (prev_hash = "genesis")
- Capture second evidence (prev_hash = first bundle's content_hash)
- Chain integrity (recompute all hashes)
- List bundles with pagination
- Get specific bundle by ID
- Get non-existent bundle (404)
- ALCOA+ validation: fully compliant (9/9)
- ALCOA+ validation: missing service_id
- ALCOA+ validation: missing timestamp
- ALCOA+ validation: missing content_hash
- ALCOA+ validation: tampered hash (inconsistent)
- ALCOA+ validation: threshold (7/9 minimum)
- Chain grows correctly
- Service info endpoint
"""

import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from datetime import datetime

import admin.services.evidence_pipeline as ep_module
from admin.services.evidence_pipeline import app, _compute_hash

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_chain(tmp_path):
    """Redirect chain storage to a tmp dir for test isolation."""
    test_chain = tmp_path / "evidence" / "chain.json"
    original_dir = ep_module.EVIDENCE_DIR
    original_file = ep_module.CHAIN_FILE
    ep_module.EVIDENCE_DIR = tmp_path / "evidence"
    ep_module.CHAIN_FILE = test_chain
    yield test_chain
    ep_module.EVIDENCE_DIR = original_dir
    ep_module.CHAIN_FILE = original_file


# ===== Health =====

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_has_chain_length_field():
    resp = client.get("/api/health")
    assert "chain_length" in resp.json()

def test_health_chain_length_starts_at_zero():
    resp = client.get("/api/health")
    assert resp.json()["chain_length"] == 0

def test_health_chain_length_increments_after_capture():
    client.post("/api/evidence/capture", json={
        "service_id": "test",
        "action": "test-action",
        "artifacts": {"key": "value"},
    })
    resp = client.get("/api/health")
    assert resp.json()["chain_length"] == 1


# ===== Service Info =====

def test_service_info_returns_correct_port():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200
    assert resp.json()["port"] == 8790

def test_service_info_has_evidence_type():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "evidence"

def test_service_info_has_name():
    resp = client.get("/api/service-info")
    assert "Evidence Pipeline" in resp.json()["name"]


# ===== Capture: First Bundle =====

def test_capture_first_bundle_prev_hash_is_genesis():
    resp = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "deploy",
        "artifacts": {"commit": "abc123"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["prev_hash"] == "genesis"

def test_capture_first_bundle_id_is_ev_000000():
    resp = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "deploy",
        "artifacts": {"commit": "abc123"},
    })
    assert resp.json()["bundle_id"] == "ev-000000"

def test_capture_first_bundle_chain_position_is_zero():
    resp = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "deploy",
        "artifacts": {"x": 1},
    })
    assert resp.json()["chain_position"] == 0

def test_capture_bundle_has_content_hash():
    resp = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "test",
        "artifacts": {"result": "pass"},
    })
    data = resp.json()
    assert "content_hash" in data
    assert len(data["content_hash"]) == 64  # SHA-256 hex digest


# ===== Capture: Second Bundle Links to First =====

def test_capture_second_bundle_prev_hash_is_first_content_hash():
    r1 = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "build",
        "artifacts": {"build_id": "1"},
    })
    first_hash = r1.json()["content_hash"]

    r2 = client.post("/api/evidence/capture", json={
        "service_id": "svc-a",
        "action": "test",
        "artifacts": {"test_id": "1"},
    })
    assert r2.json()["prev_hash"] == first_hash

def test_capture_second_bundle_id_is_ev_000001():
    client.post("/api/evidence/capture", json={
        "service_id": "svc",
        "action": "a",
        "artifacts": {"k": "v"},
    })
    r2 = client.post("/api/evidence/capture", json={
        "service_id": "svc",
        "action": "b",
        "artifacts": {"k": "v"},
    })
    assert r2.json()["bundle_id"] == "ev-000001"


# ===== Chain Integrity =====

def test_chain_integrity_all_hashes_recomputable():
    """Recompute each bundle's content_hash and verify it matches stored value."""
    actions = ["build", "test", "deploy"]
    for action in actions:
        client.post("/api/evidence/capture", json={
            "service_id": "svc",
            "action": action,
            "artifacts": {"step": action},
        })

    resp = client.get("/api/evidence/chain")
    chain = resp.json()["chain"]
    assert len(chain) == 3

    for bundle in chain:
        content = {
            "service_id": bundle["service_id"],
            "action": bundle["action"],
            "timestamp": bundle["timestamp"],
            "artifacts": bundle["artifacts"],
            "prev_hash": bundle["prev_hash"],
        }
        expected_hash = _compute_hash(content)
        assert bundle["content_hash"] == expected_hash, (
            f"Hash mismatch at position {bundle['chain_position']}"
        )

def test_chain_prev_hashes_form_linked_list():
    """Each bundle's prev_hash must equal the previous bundle's content_hash."""
    for i in range(3):
        client.post("/api/evidence/capture", json={
            "service_id": "svc",
            "action": f"step-{i}",
            "artifacts": {"i": i},
        })

    chain = client.get("/api/evidence/chain").json()["chain"]
    assert chain[0]["prev_hash"] == "genesis"
    assert chain[1]["prev_hash"] == chain[0]["content_hash"]
    assert chain[2]["prev_hash"] == chain[1]["content_hash"]


# ===== List Bundles with Pagination =====

def test_list_bundles_returns_all():
    for i in range(5):
        client.post("/api/evidence/capture", json={
            "service_id": "svc",
            "action": f"act-{i}",
            "artifacts": {"i": i},
        })
    resp = client.get("/api/evidence/bundles")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["bundles"]) == 5

def test_list_bundles_limit():
    for i in range(5):
        client.post("/api/evidence/capture", json={
            "service_id": "svc",
            "action": f"act-{i}",
            "artifacts": {"i": i},
        })
    resp = client.get("/api/evidence/bundles?limit=3")
    assert len(resp.json()["bundles"]) == 3

def test_list_bundles_offset():
    for i in range(5):
        client.post("/api/evidence/capture", json={
            "service_id": "svc",
            "action": f"act-{i}",
            "artifacts": {"i": i},
        })
    resp = client.get("/api/evidence/bundles?offset=3")
    bundles = resp.json()["bundles"]
    assert len(bundles) == 2
    assert bundles[0]["bundle_id"] == "ev-000003"


# ===== Get Bundle by ID =====

def test_get_bundle_by_id():
    client.post("/api/evidence/capture", json={
        "service_id": "svc",
        "action": "test",
        "artifacts": {"r": "pass"},
    })
    resp = client.get("/api/evidence/bundles/ev-000000")
    assert resp.status_code == 200
    assert resp.json()["bundle"]["bundle_id"] == "ev-000000"

def test_get_nonexistent_bundle_returns_404():
    resp = client.get("/api/evidence/bundles/ev-999999")
    assert resp.status_code == 404


# ===== ALCOA+ Validation =====

def _make_compliant_bundle():
    """Return a fully compliant ALCOA+ bundle dict."""
    artifacts = {"test_result": "pass", "commit": "deadbeef"}
    content = {
        "service_id": "svc-a",
        "action": "run-tests",
        "timestamp": "2026-01-01T00:00:00",
        "artifacts": artifacts,
        "prev_hash": "genesis",
    }
    content_hash = _compute_hash(content)
    return {
        "bundle_id": "ev-000000",
        "service_id": "svc-a",
        "action": "run-tests",
        "timestamp": "2026-01-01T00:00:00",
        "artifacts": artifacts,
        "metadata": {},
        "content_hash": content_hash,
        "prev_hash": "genesis",
        "chain_position": 0,
    }

def test_alcoa_fully_compliant_bundle_scores_9():
    bundle = _make_compliant_bundle()
    resp = client.post("/api/evidence/validate", json=bundle)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 9
    assert data["compliant"] is True

def test_alcoa_missing_service_id_fails_attributable():
    bundle = _make_compliant_bundle()
    del bundle["service_id"]
    resp = client.post("/api/evidence/validate", json=bundle)
    data = resp.json()
    assert data["dimensions"]["attributable"] is False
    assert any("service_id" in g for g in data["gaps"])

def test_alcoa_missing_timestamp_fails_contemporaneous():
    bundle = _make_compliant_bundle()
    bundle["timestamp"] = ""
    resp = client.post("/api/evidence/validate", json=bundle)
    data = resp.json()
    assert data["dimensions"]["contemporaneous"] is False

def test_alcoa_missing_content_hash_fails_original():
    bundle = _make_compliant_bundle()
    del bundle["content_hash"]
    resp = client.post("/api/evidence/validate", json=bundle)
    data = resp.json()
    assert data["dimensions"]["original"] is False

def test_alcoa_tampered_hash_fails_consistent():
    bundle = _make_compliant_bundle()
    bundle["content_hash"] = "deadbeef" * 8  # Wrong hash
    resp = client.post("/api/evidence/validate", json=bundle)
    data = resp.json()
    assert data["dimensions"]["consistent"] is False
    assert any("inconsistent" in g for g in data["gaps"])

def test_alcoa_threshold_7_of_9_is_compliant():
    """A bundle with exactly 7/9 dimensions should be marked compliant.

    Remove bundle_id → loses 'available' (no bundle_id) and 'complete' (bundle_id in required set).
    Remove chain_position → loses 'enduring'.
    That is 3 lost → 6. Too few.

    Instead: remove only bundle_id → loses 'available' + 'complete' = 7/9 remaining.
    """
    bundle = _make_compliant_bundle()
    # Removing bundle_id loses: available (no bundle_id) + complete (bundle_id in required set)
    # Remaining: attributable + legible + contemporaneous + original + accurate + consistent + enduring = 7
    del bundle["bundle_id"]
    resp = client.post("/api/evidence/validate", json=bundle)
    data = resp.json()
    assert data["score"] == 7
    assert data["compliant"] is True

def test_alcoa_below_7_not_compliant():
    """A bundle with < 7 dimensions should not be compliant."""
    resp = client.post("/api/evidence/validate", json={
        "action": "something",
    })
    data = resp.json()
    assert data["compliant"] is False

def test_alcoa_compliant_returns_no_gaps_for_perfect_bundle():
    bundle = _make_compliant_bundle()
    resp = client.post("/api/evidence/validate", json=bundle)
    assert resp.json()["gaps"] == []
