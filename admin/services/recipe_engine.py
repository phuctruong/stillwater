"""Recipe Engine Service — recipe cache, routing, and PM triplet management.

Port: 8789
Purpose: Load recipes, classify steps by node type, route to appropriate
services (LLM/Browser/CPU), manage cache for deterministic recipes.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import hashlib
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from .recipe_models import (
    RecipeDefinition, RecipeExecution, RecipeStep, RecipeCache,
    PMTriplet, NodeType,
)

SERVICE_ID = "recipe-engine"
SERVICE_TYPE = "recipe"
VERSION = "0.1.0"
PORT = 8789

app = FastAPI(title="Stillwater Recipe Engine", version=VERSION)

# Storage
_recipes: dict[str, RecipeDefinition] = {}
_executions: dict[str, RecipeExecution] = {}
_cache: dict[str, RecipeCache] = {}
_pm_triplets: dict[str, PMTriplet] = {}

# Service routing table
SERVICE_PORTS = {
    NodeType.LLM: 8788,
    NodeType.CPU: 8792,
    NodeType.BROWSER: 9222,
}

# --- Helpers ---

def _cache_key(recipe_id: str, params: dict) -> str:
    canonical = json.dumps({"recipe_id": recipe_id, "params": params}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

def _classify_step(step: RecipeStep) -> NodeType:
    """Classify what service type a step needs."""
    return step.node_type

def _route_step(step: RecipeStep, admin_url: str = "http://127.0.0.1:8787") -> dict:
    """Route a step to the appropriate service. Returns the result."""
    port = SERVICE_PORTS.get(step.node_type)
    if not port:
        return {"status": "skipped", "reason": f"No service for {step.node_type}"}

    url = f"http://127.0.0.1:{port}"
    # For now, return a routing descriptor (actual execution in Phase 7+)
    return {
        "status": "routed",
        "service_port": port,
        "node_type": step.node_type.value,
        "action": step.action,
        "parameters": step.parameters,
    }

# --- Endpoints ---

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
        "recipe_count": len(_recipes),
        "cache_size": len(_cache),
        "cache_hit_rate": _compute_hit_rate(),
    }

@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID, "service_type": SERVICE_TYPE,
        "name": "Recipe Engine", "version": VERSION, "port": PORT,
    }

@app.get("/api/recipes")
async def list_recipes():
    return {"ok": True, "recipes": [r.model_dump() for r in _recipes.values()]}

@app.get("/api/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    recipe = _recipes.get(recipe_id)
    if not recipe:
        raise HTTPException(404, f"Recipe {recipe_id} not found")
    return {"ok": True, "recipe": recipe.model_dump()}

@app.post("/api/recipes", status_code=201)
async def create_recipe(recipe: RecipeDefinition):
    _recipes[recipe.recipe_id] = recipe
    return {"ok": True, "recipe": recipe.model_dump()}

@app.post("/api/recipes/{recipe_id}/run")
async def run_recipe(recipe_id: str, params: dict[str, Any] = {}):
    recipe = _recipes.get(recipe_id)
    if not recipe:
        raise HTTPException(404, f"Recipe {recipe_id} not found")

    # Check cache for deterministic recipes
    if recipe.deterministic:
        key = _cache_key(recipe_id, params)
        cached = _cache.get(key)
        if cached:
            cached.hit_count += 1
            return {
                "ok": True,
                "cache_hit": True,
                "result": cached.result,
                "cache_key": key,
                "hit_count": cached.hit_count,
            }

    # Classify and route each step
    execution_id = f"exec-{len(_executions):06d}"
    results = []
    for step in recipe.steps:
        step_result = _route_step(step)
        results.append({
            "step_id": step.step_id,
            "node_type": step.node_type.value,
            **step_result,
        })

    execution = RecipeExecution(
        execution_id=execution_id,
        recipe_id=recipe_id,
        status="completed",
        started_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat(),
        results=results,
    )
    _executions[execution_id] = execution

    # Cache if deterministic
    result_dict = execution.model_dump()
    if recipe.deterministic:
        key = _cache_key(recipe_id, params)
        _cache[key] = RecipeCache(
            cache_key=key,
            recipe_id=recipe_id,
            result=result_dict,
            cached_at=datetime.utcnow().isoformat(),
        )

    return {"ok": True, "cache_hit": False, "execution": result_dict}

@app.get("/api/recipes/{recipe_id}/cache")
async def check_cache(recipe_id: str, params: str = "{}"):
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        params_dict = {}
    key = _cache_key(recipe_id, params_dict)
    cached = _cache.get(key)
    if cached:
        return {"ok": True, "cached": True, "cache_key": key, "hit_count": cached.hit_count}
    return {"ok": True, "cached": False, "cache_key": key}

@app.post("/api/pm-triplets", status_code=201)
async def create_pm_triplet(triplet: PMTriplet):
    _pm_triplets[triplet.triplet_id] = triplet
    return {"ok": True, "triplet": triplet.model_dump()}

@app.get("/api/pm-triplets")
async def list_pm_triplets(recipe_id: str | None = None):
    triplets = list(_pm_triplets.values())
    if recipe_id:
        triplets = [t for t in triplets if t.recipe_id == recipe_id]
    return {"ok": True, "triplets": [t.model_dump() for t in triplets]}

def _compute_hit_rate() -> float:
    """Compute cache hit rate (0.0 to 1.0)."""
    if not _cache:
        return 0.0
    total_hits = sum(c.hit_count for c in _cache.values())
    total_entries = len(_cache)
    if total_entries == 0:
        return 0.0
    return round(total_hits / (total_hits + total_entries), 4)
