"""Tests for Recipe Engine Service (admin/services/recipe_engine.py).

Covers:
- Health endpoint fields (recipe_count, cache_size, cache_hit_rate)
- Service info endpoint
- Create recipe (POST 201)
- List recipes (empty, then with one)
- Get recipe by ID
- Get non-existent recipe (404)
- Run recipe — routes steps correctly by node_type
- Run recipe — LLM step routes to port 8788
- Run recipe — CPU step routes to port 8792
- Run recipe — BROWSER step routes to port 9222
- Run recipe — non-existent recipe (404)
- Deterministic recipe: first run -> cache miss
- Deterministic recipe: second run -> cache hit
- Deterministic recipe: cache hit_count increments
- Non-deterministic recipe: never cached
- Check cache endpoint (cache miss)
- Check cache endpoint (cache hit after run)
- Cache key determinism (same inputs -> same key)
- Cache key differs with different params
- Create PM triplet
- List PM triplets (all)
- List PM triplets (filtered by recipe_id)
- Recipe models validation (NodeType enum, RecipeStep, PMTriplet)
- Multi-step recipe with mixed node types
"""

import hashlib
import json
import pytest
from fastapi.testclient import TestClient

import admin.services.recipe_engine as engine_module
from admin.services.recipe_engine import app
from admin.services.recipe_models import NodeType, RecipeStep, PMTriplet

client = TestClient(app)


# ===== Fixtures =====

@pytest.fixture(autouse=True)
def clear_state():
    """Clear all in-memory state between tests."""
    engine_module._recipes.clear()
    engine_module._executions.clear()
    engine_module._cache.clear()
    engine_module._pm_triplets.clear()
    yield
    engine_module._recipes.clear()
    engine_module._executions.clear()
    engine_module._cache.clear()
    engine_module._pm_triplets.clear()


# ===== Helpers =====

def _make_recipe(recipe_id="recipe-001", deterministic=False, steps=None):
    return {
        "recipe_id": recipe_id,
        "name": f"Test Recipe {recipe_id}",
        "version": "0.1.0",
        "description": "A test recipe",
        "steps": steps or [],
        "preconditions": [],
        "postconditions": [],
        "required_scopes": [],
        "deterministic": deterministic,
        "metadata": {},
    }

def _create_recipe(recipe_id="recipe-001", deterministic=False, steps=None):
    payload = _make_recipe(recipe_id, deterministic, steps)
    resp = client.post("/api/recipes", json=payload)
    assert resp.status_code == 201
    return resp


def _llm_step(step_id="step-llm"):
    return {
        "step_id": step_id,
        "node_type": "llm",
        "action": "generate",
        "parameters": {"prompt": "hello"},
        "timeout_ms": 5000,
    }

def _cpu_step(step_id="step-cpu"):
    return {
        "step_id": step_id,
        "node_type": "cpu",
        "action": "hash",
        "parameters": {"data": "abc"},
        "timeout_ms": 5000,
    }

def _browser_step(step_id="step-browser"):
    return {
        "step_id": step_id,
        "node_type": "browser",
        "action": "navigate",
        "parameters": {"url": "https://example.com"},
        "timeout_ms": 5000,
    }

def _human_step(step_id="step-human"):
    return {
        "step_id": step_id,
        "node_type": "human",
        "action": "approve",
        "parameters": {},
        "timeout_ms": 60000,
    }


# ===== Health Endpoint =====

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health_has_service_id():
    resp = client.get("/api/health")
    assert resp.json()["service_id"] == "recipe-engine"

def test_health_has_service_type():
    resp = client.get("/api/health")
    assert resp.json()["service_type"] == "recipe"

def test_health_has_version():
    resp = client.get("/api/health")
    assert "version" in resp.json()

def test_health_has_recipe_count():
    resp = client.get("/api/health")
    assert "recipe_count" in resp.json()
    assert resp.json()["recipe_count"] == 0

def test_health_recipe_count_increments_after_create():
    _create_recipe("r-001")
    resp = client.get("/api/health")
    assert resp.json()["recipe_count"] == 1

def test_health_has_cache_size():
    resp = client.get("/api/health")
    assert "cache_size" in resp.json()
    assert resp.json()["cache_size"] == 0

def test_health_has_cache_hit_rate():
    resp = client.get("/api/health")
    assert "cache_hit_rate" in resp.json()
    assert resp.json()["cache_hit_rate"] == 0.0


# ===== Service Info Endpoint =====

def test_service_info_returns_port():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200
    assert resp.json()["port"] == 8789

def test_service_info_has_service_id():
    resp = client.get("/api/service-info")
    assert resp.json()["service_id"] == "recipe-engine"

def test_service_info_has_service_type():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "recipe"

def test_service_info_has_name():
    resp = client.get("/api/service-info")
    assert "Recipe Engine" in resp.json()["name"]

def test_service_info_has_version():
    resp = client.get("/api/service-info")
    assert "version" in resp.json()


# ===== Create Recipe =====

def test_create_recipe_returns_201():
    resp = _create_recipe()
    assert resp.status_code == 201

def test_create_recipe_returns_ok_true():
    resp = _create_recipe()
    assert resp.json()["ok"] is True

def test_create_recipe_contains_recipe():
    resp = _create_recipe("r-100")
    data = resp.json()
    assert "recipe" in data
    assert data["recipe"]["recipe_id"] == "r-100"

def test_create_recipe_preserves_fields():
    payload = _make_recipe("r-200", deterministic=True)
    payload["description"] = "My desc"
    payload["required_scopes"] = ["read:profile"]
    resp = client.post("/api/recipes", json=payload)
    data = resp.json()["recipe"]
    assert data["description"] == "My desc"
    assert data["required_scopes"] == ["read:profile"]
    assert data["deterministic"] is True


# ===== List Recipes =====

def test_list_recipes_empty():
    resp = client.get("/api/recipes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["recipes"] == []

def test_list_recipes_returns_one_after_create():
    _create_recipe("r-001")
    resp = client.get("/api/recipes")
    data = resp.json()
    assert len(data["recipes"]) == 1
    assert data["recipes"][0]["recipe_id"] == "r-001"

def test_list_recipes_returns_multiple():
    _create_recipe("r-001")
    _create_recipe("r-002")
    resp = client.get("/api/recipes")
    ids = {r["recipe_id"] for r in resp.json()["recipes"]}
    assert ids == {"r-001", "r-002"}


# ===== Get Recipe by ID =====

def test_get_recipe_returns_recipe():
    _create_recipe("r-get-01")
    resp = client.get("/api/recipes/r-get-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["recipe"]["recipe_id"] == "r-get-01"

def test_get_recipe_not_found_returns_404():
    resp = client.get("/api/recipes/nonexistent-id")
    assert resp.status_code == 404

def test_get_recipe_returns_all_fields():
    payload = _make_recipe("r-fields")
    payload["steps"] = [_llm_step()]
    client.post("/api/recipes", json=payload)
    resp = client.get("/api/recipes/r-fields")
    recipe = resp.json()["recipe"]
    assert "recipe_id" in recipe
    assert "name" in recipe
    assert "version" in recipe
    assert "steps" in recipe
    assert "deterministic" in recipe


# ===== Run Recipe =====

def test_run_recipe_not_found_returns_404():
    resp = client.post("/api/recipes/ghost-recipe/run", json={})
    assert resp.status_code == 404

def test_run_recipe_returns_ok_true():
    _create_recipe("r-run-01")
    resp = client.post("/api/recipes/r-run-01/run", json={})
    assert resp.json()["ok"] is True

def test_run_recipe_returns_cache_hit_false_first_time():
    _create_recipe("r-run-02")
    resp = client.post("/api/recipes/r-run-02/run", json={})
    assert resp.json()["cache_hit"] is False

def test_run_recipe_contains_execution():
    _create_recipe("r-run-03")
    resp = client.post("/api/recipes/r-run-03/run", json={})
    data = resp.json()
    assert "execution" in data
    assert data["execution"]["recipe_id"] == "r-run-03"
    assert data["execution"]["status"] == "completed"

def test_run_recipe_llm_step_routes_to_port_8788():
    _create_recipe("r-llm", steps=[_llm_step("step-1")])
    resp = client.post("/api/recipes/r-llm/run", json={})
    results = resp.json()["execution"]["results"]
    assert len(results) == 1
    assert results[0]["service_port"] == 8788

def test_run_recipe_cpu_step_routes_to_port_8792():
    _create_recipe("r-cpu", steps=[_cpu_step("step-1")])
    resp = client.post("/api/recipes/r-cpu/run", json={})
    results = resp.json()["execution"]["results"]
    assert len(results) == 1
    assert results[0]["service_port"] == 8792

def test_run_recipe_browser_step_routes_to_port_9222():
    _create_recipe("r-browser", steps=[_browser_step("step-1")])
    resp = client.post("/api/recipes/r-browser/run", json={})
    results = resp.json()["execution"]["results"]
    assert len(results) == 1
    assert results[0]["service_port"] == 9222

def test_run_recipe_human_step_skipped_no_port():
    _create_recipe("r-human", steps=[_human_step("step-1")])
    resp = client.post("/api/recipes/r-human/run", json={})
    results = resp.json()["execution"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "skipped"

def test_run_recipe_step_result_contains_node_type():
    _create_recipe("r-nt", steps=[_llm_step("step-x")])
    resp = client.post("/api/recipes/r-nt/run", json={})
    result = resp.json()["execution"]["results"][0]
    assert result["node_type"] == "llm"

def test_run_recipe_step_result_contains_step_id():
    _create_recipe("r-sid", steps=[_cpu_step("my-step-id")])
    resp = client.post("/api/recipes/r-sid/run", json={})
    result = resp.json()["execution"]["results"][0]
    assert result["step_id"] == "my-step-id"

def test_run_recipe_step_result_contains_action():
    _create_recipe("r-action", steps=[_llm_step("s1")])
    resp = client.post("/api/recipes/r-action/run", json={})
    result = resp.json()["execution"]["results"][0]
    assert result["action"] == "generate"


# ===== Deterministic Recipe — Cache Miss / Hit =====

def test_deterministic_recipe_first_run_is_cache_miss():
    _create_recipe("r-det", deterministic=True)
    resp = client.post("/api/recipes/r-det/run", json={})
    assert resp.json()["cache_hit"] is False

def test_deterministic_recipe_second_run_is_cache_hit():
    _create_recipe("r-det2", deterministic=True)
    client.post("/api/recipes/r-det2/run", json={})
    resp = client.post("/api/recipes/r-det2/run", json={})
    assert resp.json()["cache_hit"] is True

def test_deterministic_recipe_cache_hit_returns_result():
    _create_recipe("r-det3", deterministic=True)
    client.post("/api/recipes/r-det3/run", json={})
    resp = client.post("/api/recipes/r-det3/run", json={})
    data = resp.json()
    assert "result" in data
    assert data["result"]["recipe_id"] == "r-det3"

def test_deterministic_recipe_hit_count_increments():
    _create_recipe("r-det4", deterministic=True)
    # First run — populates cache (hit_count=0)
    client.post("/api/recipes/r-det4/run", json={})
    # Second run — first cache hit → hit_count becomes 1
    resp2 = client.post("/api/recipes/r-det4/run", json={})
    assert resp2.json()["hit_count"] == 1
    # Third run — second cache hit → hit_count becomes 2
    resp3 = client.post("/api/recipes/r-det4/run", json={})
    assert resp3.json()["hit_count"] == 2

def test_non_deterministic_recipe_never_cached():
    _create_recipe("r-nondet", deterministic=False)
    client.post("/api/recipes/r-nondet/run", json={})
    resp = client.post("/api/recipes/r-nondet/run", json={})
    # Should NOT be a cache hit
    assert resp.json()["cache_hit"] is False

def test_non_deterministic_recipe_cache_size_stays_zero():
    _create_recipe("r-nondet2", deterministic=False)
    client.post("/api/recipes/r-nondet2/run", json={})
    health = client.get("/api/health").json()
    assert health["cache_size"] == 0

def test_deterministic_recipe_increments_cache_size():
    _create_recipe("r-det5", deterministic=True)
    client.post("/api/recipes/r-det5/run", json={})
    health = client.get("/api/health").json()
    assert health["cache_size"] == 1


# ===== Check Cache Endpoint =====

def test_check_cache_miss_before_run():
    _create_recipe("r-chk", deterministic=True)
    resp = client.get("/api/recipes/r-chk/cache")
    data = resp.json()
    assert data["ok"] is True
    assert data["cached"] is False
    assert "cache_key" in data

def test_check_cache_hit_after_run():
    _create_recipe("r-chk2", deterministic=True)
    client.post("/api/recipes/r-chk2/run", json={})
    resp = client.get("/api/recipes/r-chk2/cache")
    data = resp.json()
    assert data["cached"] is True

def test_check_cache_returns_cache_key():
    _create_recipe("r-chk3", deterministic=True)
    resp = client.get("/api/recipes/r-chk3/cache")
    data = resp.json()
    assert len(data["cache_key"]) == 64  # SHA-256 hex digest

def test_check_cache_hit_count_is_zero_before_second_run():
    _create_recipe("r-chk4", deterministic=True)
    client.post("/api/recipes/r-chk4/run", json={})
    resp = client.get("/api/recipes/r-chk4/cache")
    # Cached entry was just written, no hits yet (only increments on cache reads via /run)
    data = resp.json()
    assert data["cached"] is True
    assert data["hit_count"] == 0


# ===== Cache Key Determinism =====

def test_cache_key_determinism_same_inputs():
    key1 = engine_module._cache_key("recipe-x", {"a": 1})
    key2 = engine_module._cache_key("recipe-x", {"a": 1})
    assert key1 == key2

def test_cache_key_differs_with_different_params():
    key1 = engine_module._cache_key("recipe-x", {"a": 1})
    key2 = engine_module._cache_key("recipe-x", {"a": 2})
    assert key1 != key2

def test_cache_key_differs_with_different_recipe_id():
    key1 = engine_module._cache_key("recipe-a", {"a": 1})
    key2 = engine_module._cache_key("recipe-b", {"a": 1})
    assert key1 != key2

def test_cache_key_is_sha256_hex():
    key = engine_module._cache_key("recipe-x", {})
    assert len(key) == 64
    int(key, 16)  # Raises ValueError if not valid hex


# ===== PM Triplets =====

def test_create_pm_triplet_returns_201():
    payload = {
        "triplet_id": "t-001",
        "recipe_id": "r-pm-01",
        "precondition": "user logged in",
        "method": "click login button",
        "postcondition": "user dashboard visible",
        "selector_hash": "",
    }
    resp = client.post("/api/pm-triplets", json=payload)
    assert resp.status_code == 201

def test_create_pm_triplet_returns_ok_true():
    payload = {
        "triplet_id": "t-002",
        "recipe_id": "r-pm-02",
        "precondition": "page loaded",
        "method": "submit form",
        "postcondition": "success message shown",
        "selector_hash": "abc123",
    }
    resp = client.post("/api/pm-triplets", json=payload)
    assert resp.json()["ok"] is True

def test_create_pm_triplet_contains_triplet():
    payload = {
        "triplet_id": "t-003",
        "recipe_id": "r-pm-03",
        "precondition": "pre",
        "method": "meth",
        "postcondition": "post",
        "selector_hash": "",
    }
    resp = client.post("/api/pm-triplets", json=payload)
    triplet = resp.json()["triplet"]
    assert triplet["triplet_id"] == "t-003"
    assert triplet["recipe_id"] == "r-pm-03"

def test_list_pm_triplets_empty():
    resp = client.get("/api/pm-triplets")
    assert resp.status_code == 200
    assert resp.json()["triplets"] == []

def test_list_pm_triplets_all():
    for i in range(3):
        client.post("/api/pm-triplets", json={
            "triplet_id": f"t-{i:03d}",
            "recipe_id": f"r-{i}",
            "precondition": "pre",
            "method": "meth",
            "postcondition": "post",
            "selector_hash": "",
        })
    resp = client.get("/api/pm-triplets")
    assert len(resp.json()["triplets"]) == 3

def test_list_pm_triplets_filtered_by_recipe_id():
    for i in range(3):
        client.post("/api/pm-triplets", json={
            "triplet_id": f"t-f{i}",
            "recipe_id": "r-target" if i < 2 else "r-other",
            "precondition": "pre",
            "method": "meth",
            "postcondition": "post",
            "selector_hash": "",
        })
    resp = client.get("/api/pm-triplets?recipe_id=r-target")
    triplets = resp.json()["triplets"]
    assert len(triplets) == 2
    assert all(t["recipe_id"] == "r-target" for t in triplets)

def test_list_pm_triplets_filter_no_match():
    client.post("/api/pm-triplets", json={
        "triplet_id": "t-x",
        "recipe_id": "r-exists",
        "precondition": "pre",
        "method": "meth",
        "postcondition": "post",
        "selector_hash": "",
    })
    resp = client.get("/api/pm-triplets?recipe_id=r-ghost")
    assert resp.json()["triplets"] == []


# ===== Models Validation =====

def test_node_type_enum_values():
    assert NodeType.LLM == "llm"
    assert NodeType.CPU == "cpu"
    assert NodeType.BROWSER == "browser"
    assert NodeType.HUMAN == "human"
    assert NodeType.COMPOSITE == "composite"

def test_recipe_step_default_timeout():
    step = RecipeStep(step_id="s", node_type=NodeType.LLM, action="gen")
    assert step.timeout_ms == 5000

def test_recipe_step_default_parameters():
    step = RecipeStep(step_id="s", node_type=NodeType.CPU, action="hash")
    assert step.parameters == {}

def test_recipe_step_expected_output_defaults_none():
    step = RecipeStep(step_id="s", node_type=NodeType.BROWSER, action="nav")
    assert step.expected_output is None

def test_pm_triplet_selector_hash_default_empty():
    triplet = PMTriplet(
        triplet_id="t",
        recipe_id="r",
        precondition="pre",
        method="meth",
        postcondition="post",
    )
    assert triplet.selector_hash == ""

def test_invalid_node_type_rejected():
    resp = client.post("/api/recipes", json={
        "recipe_id": "r-bad",
        "name": "Bad Recipe",
        "steps": [{
            "step_id": "s",
            "node_type": "invalid_type",
            "action": "do_something",
        }],
    })
    assert resp.status_code == 422


# ===== Multi-Step Recipe with Mixed Node Types =====

def test_multi_step_recipe_routes_all_steps():
    steps = [
        _llm_step("step-llm"),
        _cpu_step("step-cpu"),
        _browser_step("step-browser"),
        _human_step("step-human"),
    ]
    _create_recipe("r-multi", steps=steps)
    resp = client.post("/api/recipes/r-multi/run", json={})
    results = resp.json()["execution"]["results"]
    assert len(results) == 4

def test_multi_step_recipe_correct_port_per_step():
    steps = [
        _llm_step("s-llm"),
        _cpu_step("s-cpu"),
        _browser_step("s-browser"),
    ]
    _create_recipe("r-ports", steps=steps)
    resp = client.post("/api/recipes/r-ports/run", json={})
    results = {r["step_id"]: r for r in resp.json()["execution"]["results"]}
    assert results["s-llm"]["service_port"] == 8788
    assert results["s-cpu"]["service_port"] == 8792
    assert results["s-browser"]["service_port"] == 9222

def test_multi_step_recipe_all_steps_status_routed():
    steps = [_llm_step("a"), _cpu_step("b"), _browser_step("c")]
    _create_recipe("r-status", steps=steps)
    resp = client.post("/api/recipes/r-status/run", json={})
    results = resp.json()["execution"]["results"]
    for result in results:
        assert result["status"] == "routed"

def test_multi_step_recipe_execution_id_format():
    _create_recipe("r-exec-id")
    resp = client.post("/api/recipes/r-exec-id/run", json={})
    execution_id = resp.json()["execution"]["execution_id"]
    assert execution_id.startswith("exec-")

def test_multi_step_recipe_started_and_completed_at_set():
    _create_recipe("r-times")
    resp = client.post("/api/recipes/r-times/run", json={})
    execution = resp.json()["execution"]
    assert execution["started_at"] != ""
    assert execution["completed_at"] != ""
