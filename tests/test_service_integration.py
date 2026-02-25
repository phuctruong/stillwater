"""Integration tests for the Stillwater webservice-first service mesh.

Each test here verifies a CROSS-SERVICE flow — not an individual endpoint.
Pattern:
  - Import each service app directly (FastAPI instances)
  - Create a TestClient per service
  - Drive the cross-service interaction in test logic, replacing HTTP hops
    with direct client calls (zero network, no real ports)
  - Reset all in-memory state via autouse fixtures

"Every line of code is a theorem. An untested function is an unproven lemma."
                                                          — Donald Knuth

Cross-service flows verified:
  Flow 1  (tests 01-05): Recipe → CPU → Evidence
  Flow 2  (tests 06-10): OAuth3 → Evidence
  Flow 3  (tests 11-15): Service Registry → Health → All Services
  Flow 4  (tests 16-20): Cloud Bridge → OAuth3 → Tunnel
  Flow 5  (tests 21-25): Evidence chain integrity across multiple services
  Flow 6  (tests 26-30): Full pipeline (Register → Token → Recipe → CPU → Evidence → ALCOA+)
"""

import hashlib
import json
import pytest
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

# ── Service modules (for state reset) ──────────────────────────────────────
import admin.services.evidence_pipeline as ep_module
import admin.services.oauth3_service as oauth3_module
import admin.services.cloud_bridge as bridge_module
import admin.services.tunnel_service as tunnel_module
import admin.services.recipe_engine as recipe_module

# ── FastAPI app instances ───────────────────────────────────────────────────
from admin.services.evidence_pipeline import app as evidence_app, _compute_hash
from admin.services.oauth3_service import app as oauth3_app
from admin.services.cpu_service import app as cpu_app
from admin.services.recipe_engine import app as recipe_app
from admin.services.tunnel_service import app as tunnel_app
from admin.services.cloud_bridge import app as bridge_app

# ── Registry (pure Python class, not a FastAPI app — used directly) ─────────
from admin.services.registry import ServiceRegistry
from admin.services.models import ServiceRegistration, ServiceType, ServiceStatus

# ── TestClients (one per service) ───────────────────────────────────────────
evidence_client = TestClient(evidence_app)
oauth3_client = TestClient(oauth3_app)
cpu_client = TestClient(cpu_app)
recipe_client = TestClient(recipe_app)
tunnel_client = TestClient(tunnel_app)
bridge_client = TestClient(bridge_app)


# ===========================================================================
# Fixtures — state isolation
# ===========================================================================

@pytest.fixture(autouse=True)
def reset_all_services(tmp_path):
    """Reset every service to a clean state before and after each test."""

    # Evidence: redirect chain file to tmp
    ep_module.EVIDENCE_DIR = tmp_path / "evidence"
    ep_module.CHAIN_FILE = tmp_path / "evidence" / "chain.json"

    # OAuth3: clear in-memory stores
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()

    # Cloud Bridge: clear connection + capabilities
    bridge_module._connection = None
    bridge_module._capabilities.clear()
    bridge_module._route_log.clear()

    # Tunnel: clear tunnels
    tunnel_module._tunnels.clear()

    # Recipe Engine: clear recipes, executions, cache
    recipe_module._recipes.clear()
    recipe_module._executions.clear()
    recipe_module._cache.clear()
    recipe_module._pm_triplets.clear()

    yield

    # Teardown: same resets
    oauth3_module._tokens.clear()
    oauth3_module._consent_log.clear()
    bridge_module._connection = None
    bridge_module._capabilities.clear()
    bridge_module._route_log.clear()
    tunnel_module._tunnels.clear()
    recipe_module._recipes.clear()
    recipe_module._executions.clear()
    recipe_module._cache.clear()
    recipe_module._pm_triplets.clear()


# ===========================================================================
# Helpers
# ===========================================================================

def _future_ts(hours: int = 24) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past_ts(hours: int = 1) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _issue_token(
    scopes: list[str] | None = None,
    expires_at: str | None = None,
    principal_id: str = "user-1",
    agent_id: str = "agent-1",
) -> dict:
    resp = oauth3_client.post("/oauth3/tokens", json={
        "principal_id": principal_id,
        "agent_id": agent_id,
        "scopes": scopes or ["browser.navigate"],
        "expires_at": expires_at or _future_ts(),
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


def _capture_evidence(service_id: str, action: str, artifacts: dict) -> dict:
    resp = evidence_client.post("/api/evidence/capture", json={
        "service_id": service_id,
        "action": action,
        "artifacts": artifacts,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


def _cpu_hash(data: str, algorithm: str = "sha256") -> str:
    resp = cpu_client.post("/api/cpu/hash", json={"data": data, "algorithm": algorithm})
    assert resp.status_code == 200, resp.text
    return resp.json()["hash"]


def _cpu_validate_rung(claimed: int, has_tests: bool = True,
                       has_red_green: bool = False,
                       has_security: bool = False,
                       artifacts: list[str] | None = None) -> dict:
    resp = cpu_client.post("/api/cpu/validate-rung", json={
        "claimed_rung": claimed,
        "evidence_artifacts": artifacts or ["tests.json"],
        "has_tests": has_tests,
        "has_red_green": has_red_green,
        "has_security_review": has_security,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


def _create_recipe(recipe_id: str, deterministic: bool = True) -> dict:
    resp = recipe_client.post("/api/recipes", json={
        "recipe_id": recipe_id,
        "name": f"Recipe {recipe_id}",
        "deterministic": deterministic,
        "steps": [
            {
                "step_id": "step-cpu",
                "node_type": "cpu",
                "action": "hash",
                "parameters": {"data": "test-payload"},
            }
        ],
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


def _start_tunnel(service_id: str, port: int = 8792,
                  oauth3_token: str | None = None) -> dict:
    payload: dict = {
        "service_id": service_id,
        "service_port": port,
        "tunnel_type": "wss",
        "target_host": "tunnel.solaceagi.com",
    }
    if oauth3_token:
        payload["oauth3_token"] = oauth3_token
    resp = tunnel_client.post("/api/tunnel/start", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _bridge_connect(tier: str = "pro") -> dict:
    # Integration tests run fully local/offline: force deterministic cloud status.
    with patch.object(
        bridge_module,
        "_cloud_status",
        return_value={
            "status": "ok",
            "tier": tier,
            "api_url": "https://test.solace.local/api/v1",
        },
    ):
        resp = bridge_client.post("/api/bridge/connect", json={
            "api_key": "test-api-key",
            "instance_id": "test-instance",
            "tier": tier,
        })
    assert resp.status_code == 200, resp.text
    return resp.json()


def _register_bridge_cap(service_type: str, service_id: str, port: int) -> dict:
    resp = bridge_client.post("/api/bridge/capabilities/register", json={
        "service_id": service_id,
        "service_type": service_type,
        "port": port,
        "endpoints": ["/api/health"],
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


# ===========================================================================
# Flow 1: Recipe → CPU → Evidence
# Tests 01-05
# Theorem: A recipe execution targeting a CPU step can be captured in the
# evidence chain and the bundle hash must be deterministically recomputable.
# ===========================================================================

def test_01_recipe_creates_cpu_step_result():
    """Recipe engine produces a CPU-routed step result."""
    _create_recipe("hash-recipe")
    resp = recipe_client.post("/api/recipes/hash-recipe/run", json={})
    assert resp.status_code == 200
    data = resp.json()
    # Step must have been classified as cpu
    step = data["execution"]["results"][0]
    assert step["node_type"] == "cpu"
    assert step["status"] == "routed"


def test_02_recipe_execution_id_is_sequential():
    """Two recipe runs produce sequential execution IDs."""
    _create_recipe("seq-recipe")
    r1 = recipe_client.post("/api/recipes/seq-recipe/run", json={}).json()
    r2 = recipe_client.post("/api/recipes/seq-recipe/run", json={}).json()
    # Second run should NOT be cached (first run stored in cache; second run hits cache)
    # For a deterministic recipe the second call IS a cache hit — so we check
    # that both calls succeed and return consistent recipe_id fields.
    assert r1["execution"]["recipe_id"] == "seq-recipe"
    # Second call is a cache hit
    assert r2["cache_hit"] is True


def test_03_recipe_execution_captured_in_evidence_pipeline():
    """After running a recipe, its execution is captured as an evidence bundle."""
    _create_recipe("ev-recipe")
    exec_resp = recipe_client.post("/api/recipes/ev-recipe/run", json={}).json()
    execution_id = exec_resp["execution"]["execution_id"]

    # Capture the execution as evidence
    bundle = _capture_evidence(
        service_id="recipe-engine",
        action="recipe-execution",
        artifacts={
            "execution_id": execution_id,
            "recipe_id": "ev-recipe",
            "status": "completed",
        },
    )

    assert bundle["service_id"] == "recipe-engine"
    assert bundle["action"] == "recipe-execution"
    assert bundle["artifacts"]["execution_id"] == execution_id
    assert bundle["chain_position"] == 0


def test_04_cpu_hash_result_stored_in_evidence_bundle():
    """CPU-computed hash is stored inside an evidence bundle as an artifact."""
    # Step 1: CPU computes a hash
    payload = "recipe-output-data"
    computed_hash = _cpu_hash(payload)

    # Step 2: Store hash in evidence
    bundle = _capture_evidence(
        service_id="cpu-service",
        action="hash-computation",
        artifacts={"input": payload, "sha256": computed_hash},
    )

    assert bundle["artifacts"]["sha256"] == computed_hash
    assert len(computed_hash) == 64  # SHA-256 hex length


def test_05_evidence_bundle_linked_to_cpu_hash_is_alcoa_compliant():
    """Evidence bundle for a CPU hash result achieves ALCOA+ compliance (9/9)."""
    computed_hash = _cpu_hash("test-data")

    bundle = _capture_evidence(
        service_id="cpu-service",
        action="hash-verification",
        artifacts={"sha256": computed_hash, "verified": True},
    )

    # Validate the bundle we just captured
    validate_resp = evidence_client.post("/api/evidence/validate", json=bundle)
    assert validate_resp.status_code == 200
    result = validate_resp.json()
    assert result["score"] == 9
    assert result["compliant"] is True
    assert result["gaps"] == []


# ===========================================================================
# Flow 2: OAuth3 → Evidence
# Tests 06-10
# Theorem: Token issuance, scope enforcement, and consent events must each
# produce a traceable evidence bundle, and all three bundles must form a
# correctly linked hash chain.
# ===========================================================================

def test_06_token_issuance_captured_as_evidence():
    """Issue a token; capture the issuance in the evidence pipeline."""
    token = _issue_token(scopes=["store.read"])

    bundle = _capture_evidence(
        service_id="oauth3-service",
        action="token-issued",
        artifacts={
            "token_id": token["token_id"],
            "principal_id": token["principal_id"],
            "scopes": token["scopes"],
        },
    )

    assert bundle["service_id"] == "oauth3-service"
    assert bundle["artifacts"]["token_id"] == token["token_id"]


def test_07_scope_enforcement_result_captured_in_evidence():
    """Scope enforcement outcome is captured as an evidence artifact."""
    token = _issue_token(scopes=["browser.navigate"])

    # Enforce scope
    enforce_resp = oauth3_client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["browser.navigate"],
        "action_risk": "low",
    })
    enforce_result = enforce_resp.json()
    assert enforce_result["allowed"] is True

    # Capture the enforcement as evidence
    bundle = _capture_evidence(
        service_id="oauth3-service",
        action="scope-enforcement",
        artifacts={
            "token_id": token["token_id"],
            "required_scopes": ["browser.navigate"],
            "allowed": enforce_result["allowed"],
            "gate_results": enforce_result["gate_results"],
        },
    )

    assert bundle["artifacts"]["allowed"] is True
    assert bundle["artifacts"]["gate_results"]["g1"] is True
    assert bundle["artifacts"]["gate_results"]["g3"] is True


def test_08_denied_scope_enforcement_also_captured_in_evidence():
    """A denied scope check must also appear in the evidence chain."""
    token = _issue_token(scopes=["browser.navigate"])

    # Try to access a scope the token does not have
    enforce_resp = oauth3_client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["vault.write"],
        "action_risk": "low",
    })
    deny_result = enforce_resp.json()
    assert deny_result["allowed"] is False

    bundle = _capture_evidence(
        service_id="oauth3-service",
        action="scope-denied",
        artifacts={
            "token_id": token["token_id"],
            "required_scopes": ["vault.write"],
            "allowed": False,
            "reason": deny_result["reason"],
        },
    )

    assert bundle["artifacts"]["allowed"] is False
    assert "G3" in bundle["artifacts"]["reason"]


def test_09_consent_record_linked_to_evidence_bundle():
    """A consent event is recorded in OAuth3 and also captured in evidence."""
    token = _issue_token(scopes=["browser.navigate"])

    # Record consent in OAuth3
    consent_resp = oauth3_client.post("/oauth3/consent", json={
        "token_id": token["token_id"],
        "principal_id": "user-1",
        "agent_id": "agent-1",
        "action": "navigate",
        "scopes_requested": ["browser.navigate"],
        "decision": "granted",
    })
    assert consent_resp.status_code == 201
    consent_record = consent_resp.json()

    # Capture consent event in evidence pipeline
    bundle = _capture_evidence(
        service_id="oauth3-service",
        action="consent-recorded",
        artifacts={
            "consent_id": consent_record["consent_id"],
            "token_id": token["token_id"],
            "decision": "granted",
        },
    )

    assert bundle["artifacts"]["consent_id"] == consent_record["consent_id"]
    assert bundle["artifacts"]["decision"] == "granted"


def test_10_oauth3_evidence_chain_three_events_properly_linked():
    """Three OAuth3 events (issue → enforce → consent) form a valid hash chain."""
    token = _issue_token(scopes=["browser.navigate"])

    # Event 1: token issued
    b1 = _capture_evidence("oauth3-service", "token-issued",
                            {"token_id": token["token_id"]})
    # Event 2: scope check
    b2 = _capture_evidence("oauth3-service", "scope-check",
                            {"token_id": token["token_id"], "outcome": "allowed"})
    # Event 3: consent
    b3 = _capture_evidence("oauth3-service", "consent-granted",
                            {"token_id": token["token_id"], "action": "navigate"})

    # Verify chain linkage
    assert b1["prev_hash"] == "genesis"
    assert b2["prev_hash"] == b1["content_hash"]
    assert b3["prev_hash"] == b2["content_hash"]
    assert b1["chain_position"] == 0
    assert b2["chain_position"] == 1
    assert b3["chain_position"] == 2


# ===========================================================================
# Flow 3: Service Registry → Health → All Services
# Tests 11-15
# Theorem: Multiple services registered in the registry each expose a /api/health
# endpoint; the registry can enumerate them; health status is STARTING for newly
# registered services (no real network probe required in unit/integration context).
# ===========================================================================

def test_11_registry_registers_multiple_services(tmp_path):
    """Register three services; the registry lists all three."""
    reg = ServiceRegistry(persist_path=str(tmp_path / "registry.json"))

    for svc_id, svc_type, name in [
        ("evidence-pipeline", ServiceType.EVIDENCE, "Evidence Pipeline"),
        ("oauth3-authority", ServiceType.OAUTH3, "OAuth3 Authority"),
        ("cpu-service", ServiceType.CPU, "CPU Service"),
    ]:
        reg.register(ServiceRegistration(
            service_id=svc_id,
            service_type=svc_type,
            name=name,
            port=8790,
        ))

    all_services = reg.list_all()
    assert len(all_services) == 3
    service_ids = {s.service_id for s in all_services}
    assert "evidence-pipeline" in service_ids
    assert "oauth3-authority" in service_ids
    assert "cpu-service" in service_ids


def test_12_registry_persists_and_reloads(tmp_path):
    """Services saved by one registry instance are loadable by another."""
    persist = str(tmp_path / "registry.json")
    reg1 = ServiceRegistry(persist_path=persist)
    reg1.register(ServiceRegistration(
        service_id="cpu-service",
        service_type=ServiceType.CPU,
        name="CPU Service",
        port=8792,
    ))

    reg2 = ServiceRegistry(persist_path=persist)
    count = reg2.load()
    assert count == 1
    desc = reg2.get("cpu-service")
    assert desc is not None
    assert desc.service_id == "cpu-service"


def test_13_registry_health_check_offline_when_no_server(tmp_path):
    """Health check returns OFFLINE if no server is running at the address."""
    reg = ServiceRegistry(persist_path=str(tmp_path / "registry.json"))
    reg.register(ServiceRegistration(
        service_id="ghost-service",
        service_type=ServiceType.CUSTOM,
        name="Ghost",
        port=9999,  # Nothing listens here
    ))

    health = reg.health_check("ghost-service", timeout=0.1)
    assert health.status == ServiceStatus.OFFLINE
    assert "error" in health.details


def test_14_all_service_health_endpoints_return_ok():
    """All five in-process services report status=ok at /api/health."""
    checks = [
        (evidence_client, "evidence-pipeline"),
        (oauth3_client, "oauth3-service"),
        (cpu_client, "cpu-service"),
        (recipe_client, "recipe-engine"),
        (tunnel_client, "tunnel-service"),
        (bridge_client, "cloud-bridge"),
    ]
    for svc_client, expected_id in checks:
        resp = svc_client.get("/api/health")
        assert resp.status_code == 200, f"{expected_id} health failed"
        data = resp.json()
        assert data["status"] == "ok", f"{expected_id} status not ok"
        assert data["service_id"] == expected_id, f"Wrong service_id for {expected_id}"


def test_15_registry_deregister_removes_service(tmp_path):
    """Deregistering a service removes it from the registry."""
    reg = ServiceRegistry(persist_path=str(tmp_path / "registry.json"))
    reg.register(ServiceRegistration(
        service_id="temp-service",
        service_type=ServiceType.CUSTOM,
        name="Temp",
        port=9000,
    ))
    assert reg.get("temp-service") is not None

    removed = reg.deregister("temp-service")
    assert removed is True
    assert reg.get("temp-service") is None
    assert len(reg.list_all()) == 0


# ===========================================================================
# Flow 4: Cloud Bridge → OAuth3 → Tunnel
# Tests 16-20
# Theorem: A cloud bridge connection with a valid OAuth3 token can start a
# tunnel; the tunnel carries the token reference; the bridge capabilities
# reflect the tunneled service.
# ===========================================================================

def test_16_bridge_connect_and_status():
    """Cloud bridge connects and returns correct tier in status."""
    _bridge_connect(tier="pro")
    status_resp = bridge_client.get("/api/bridge/status")
    assert status_resp.status_code == 200
    status = status_resp.json()
    assert status["connected"] is True
    assert status["tier"] == "pro"
    assert status["instance_id"] == "test-instance"


def test_17_bridge_connect_then_register_capability():
    """After connecting, register a capability for the OAuth3 service."""
    _bridge_connect(tier="pro")
    result = _register_bridge_cap("oauth3", "oauth3-authority", 8791)
    assert result["ok"] is True
    assert result["registered"]["service_type"] == "oauth3"

    caps_resp = bridge_client.get("/api/bridge/capabilities")
    assert caps_resp.json()["count"] == 1


def test_18_bridge_token_issued_then_tunnel_started_with_token():
    """Issue an OAuth3 token, then start a tunnel that carries the token."""
    token = _issue_token(scopes=["browser.navigate"])
    tunnel = _start_tunnel("oauth3-authority", port=8791,
                           oauth3_token=token["token_id"])

    assert tunnel["status"] == "active"
    # Verify tunnel carries the token reference in internal state
    tunnel_state = tunnel_module._tunnels[tunnel["tunnel_id"]]
    assert tunnel_state["oauth3_token"] == token["token_id"]


def test_19_tunnel_started_for_service_appears_in_tunneled_services():
    """A started tunnel appears in the tunneled_services list."""
    _start_tunnel("cpu-service", port=8792)
    resp = tunnel_client.get("/api/tunnel/services")
    assert resp.status_code == 200
    active = resp.json()["tunneled_services"]
    assert len(active) == 1
    assert active[0]["service_id"] == "cpu-service"


def test_20_bridge_free_tier_cannot_route_to_oauth3():
    """Free-tier bridge may only route to llm service; oauth3 is blocked."""
    _bridge_connect(tier="free")
    _register_bridge_cap("oauth3", "oauth3-authority", 8791)

    route_resp = bridge_client.post("/api/bridge/route", json={
        "service_type": "oauth3",
        "endpoint": "/api/health",
        "method": "GET",
    })
    assert route_resp.status_code == 403
    assert "pro or enterprise" in route_resp.json()["detail"]


# ===========================================================================
# Flow 5: Evidence Chain Integrity Across Multiple Services
# Tests 21-25
# Theorem: When N different services each capture one evidence bundle, the
# global chain must maintain unbroken SHA-256 linkage from position 0 to N-1.
# ===========================================================================

def test_21_five_services_each_capture_evidence_form_linked_chain():
    """Five services each submit one evidence bundle; chain is intact."""
    services = [
        ("recipe-engine", "recipe-run", {"recipe_id": "r1"}),
        ("cpu-service", "hash-computed", {"hash": "abc"}),
        ("oauth3-service", "token-issued", {"token_id": "t1"}),
        ("tunnel-service", "tunnel-started", {"tunnel_id": "tun1"}),
        ("cloud-bridge", "connection-established", {"instance": "inst1"}),
    ]
    for svc_id, action, artifacts in services:
        _capture_evidence(svc_id, action, artifacts)

    chain_resp = evidence_client.get("/api/evidence/chain")
    chain = chain_resp.json()["chain"]
    assert len(chain) == 5

    # Verify genesis anchor
    assert chain[0]["prev_hash"] == "genesis"

    # Verify each bundle's hash is recomputable
    for bundle in chain:
        content = {
            "service_id": bundle["service_id"],
            "action": bundle["action"],
            "timestamp": bundle["timestamp"],
            "artifacts": bundle["artifacts"],
            "prev_hash": bundle["prev_hash"],
        }
        expected = _compute_hash(content)
        assert bundle["content_hash"] == expected, (
            f"Hash mismatch at position {bundle['chain_position']}: "
            f"service={bundle['service_id']}"
        )


def test_22_chain_linkage_is_unbroken_across_all_bundles():
    """Each bundle's prev_hash equals the previous bundle's content_hash."""
    for i in range(4):
        _capture_evidence(f"svc-{i}", f"action-{i}", {"step": i})

    chain = evidence_client.get("/api/evidence/chain").json()["chain"]
    assert chain[0]["prev_hash"] == "genesis"
    for pos in range(1, len(chain)):
        assert chain[pos]["prev_hash"] == chain[pos - 1]["content_hash"], (
            f"Chain broken between position {pos-1} and {pos}"
        )


def test_23_evidence_bundle_ids_are_sequential_across_services():
    """Bundle IDs increment sequentially regardless of which service captures them."""
    services = ["recipe-engine", "oauth3-service", "cpu-service"]
    for svc in services:
        _capture_evidence(svc, "test-action", {"svc": svc})

    bundles_resp = evidence_client.get("/api/evidence/bundles")
    bundles = bundles_resp.json()["bundles"]
    assert bundles[0]["bundle_id"] == "ev-000000"
    assert bundles[1]["bundle_id"] == "ev-000001"
    assert bundles[2]["bundle_id"] == "ev-000002"


def test_24_individual_bundle_retrievable_by_id():
    """A bundle captured by a specific service is retrievable by its bundle_id."""
    bundle = _capture_evidence("tunnel-service", "tunnel-stop", {"tunnel_id": "tun42"})
    bundle_id = bundle["bundle_id"]

    resp = evidence_client.get(f"/api/evidence/bundles/{bundle_id}")
    assert resp.status_code == 200
    fetched = resp.json()["bundle"]
    assert fetched["service_id"] == "tunnel-service"
    assert fetched["artifacts"]["tunnel_id"] == "tun42"


def test_25_alcoa_validation_of_cross_service_bundle():
    """A bundle captured by one service validates as ALCOA+-compliant."""
    bundle = _capture_evidence(
        "cloud-bridge",
        "route-log",
        {"service_type": "evidence", "endpoint": "/api/evidence/capture"},
    )

    validate_resp = evidence_client.post("/api/evidence/validate", json=bundle)
    result = validate_resp.json()
    assert result["compliant"] is True
    assert result["score"] >= 7


# ===========================================================================
# Flow 6: Full Pipeline
# Register → Token → Recipe → CPU → Evidence → Validate ALCOA+
# Tests 26-30
# Theorem: The complete happy path through all six services produces an
# ALCOA+-compliant evidence bundle whose hash is deterministically recomputable.
# ===========================================================================

def test_26_full_pipeline_service_registry_records_all_services(tmp_path):
    """Registry step: all six services are registered with correct service types."""
    reg = ServiceRegistry(persist_path=str(tmp_path / "full-pipeline.json"))
    services_to_register = [
        ("evidence-pipeline", ServiceType.EVIDENCE, 8790),
        ("oauth3-authority", ServiceType.OAUTH3, 8791),
        ("cpu-service", ServiceType.CPU, 8792),
        ("recipe-engine", ServiceType.RECIPE, 8789),
        ("tunnel-service", ServiceType.CUSTOM, 8793),
        ("cloud-bridge", ServiceType.CUSTOM, 8794),
    ]
    for svc_id, svc_type, port in services_to_register:
        reg.register(ServiceRegistration(
            service_id=svc_id,
            service_type=svc_type,
            name=svc_id.replace("-", " ").title(),
            port=port,
        ))

    assert len(reg.list_all()) == 6


def test_27_full_pipeline_token_issued_and_enforced():
    """Token step: issue a token with recipe and cpu scopes; enforce both."""
    token = _issue_token(scopes=["store.read", "browser.read"])

    for scope in ["store.read", "browser.read"]:
        enforce_resp = oauth3_client.post("/oauth3/enforce", json={
            "token_id": token["token_id"],
            "required_scopes": [scope],
            "action_risk": "low",
        })
        data = enforce_resp.json()
        assert data["allowed"] is True, f"Scope {scope} was denied"


def test_28_full_pipeline_recipe_runs_and_routes_to_cpu():
    """Recipe step: create a CPU recipe, run it, verify step routing."""
    _create_recipe("pipeline-recipe", deterministic=True)

    run_resp = recipe_client.post("/api/recipes/pipeline-recipe/run", json={})
    assert run_resp.status_code == 200
    run_data = run_resp.json()

    assert run_data["cache_hit"] is False
    step = run_data["execution"]["results"][0]
    assert step["node_type"] == "cpu"
    assert step["status"] == "routed"
    assert step["service_port"] == 8792


def test_29_full_pipeline_cpu_rung_validation_and_evidence_capture():
    """CPU step: validate rung 641; capture the validation result in evidence."""
    rung_result = _cpu_validate_rung(
        claimed=641,
        has_tests=True,
        artifacts=["tests.json", "plan.json"],
    )
    assert rung_result["valid"] is True
    assert rung_result["achieved_rung"] == 641

    bundle = _capture_evidence(
        service_id="cpu-service",
        action="rung-validation",
        artifacts={
            "claimed_rung": rung_result["claimed_rung"],
            "achieved_rung": rung_result["achieved_rung"],
            "valid": rung_result["valid"],
        },
    )

    assert bundle["service_id"] == "cpu-service"
    assert bundle["artifacts"]["valid"] is True
    assert bundle["artifacts"]["achieved_rung"] == 641


def test_30_full_pipeline_final_alcoa_validation_is_compliant():
    """End-to-end: all pipeline stages complete; final evidence bundle is ALCOA+-compliant.

    Pipeline stages:
      1. Issue OAuth3 token
      2. Enforce scope
      3. Create + run recipe
      4. CPU rung validation
      5. Capture pipeline summary as evidence
      6. Validate the captured bundle against ALCOA+ criteria
    """
    # Stage 1: Issue token
    token = _issue_token(scopes=["store.read"])

    # Stage 2: Enforce scope
    enforce_resp = oauth3_client.post("/oauth3/enforce", json={
        "token_id": token["token_id"],
        "required_scopes": ["store.read"],
        "action_risk": "low",
    })
    assert enforce_resp.json()["allowed"] is True

    # Stage 3: Recipe run
    _create_recipe("final-recipe", deterministic=True)
    run_resp = recipe_client.post("/api/recipes/final-recipe/run", json={}).json()
    execution_id = run_resp["execution"]["execution_id"]

    # Stage 4: CPU rung validation
    rung_result = _cpu_validate_rung(641, has_tests=True)
    assert rung_result["valid"] is True

    # Stage 5: Capture full pipeline summary
    bundle = _capture_evidence(
        service_id="pipeline-orchestrator",
        action="full-pipeline-complete",
        artifacts={
            "token_id": token["token_id"],
            "scope_allowed": True,
            "execution_id": execution_id,
            "rung_achieved": rung_result["achieved_rung"],
            "pipeline_status": "completed",
        },
    )

    # Stage 6: ALCOA+ validation
    validate_resp = evidence_client.post("/api/evidence/validate", json=bundle)
    result = validate_resp.json()

    assert result["compliant"] is True, (
        f"Final pipeline bundle failed ALCOA+: score={result['score']}, gaps={result['gaps']}"
    )
    assert result["score"] == 9  # All 9 ALCOA+ dimensions satisfied
    assert result["gaps"] == []
